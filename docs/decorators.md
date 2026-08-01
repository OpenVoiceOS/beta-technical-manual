# Decorators

!!! abstract "In a nutshell"
    A "decorator" is a small label you place on a line just above one of your skill's functions (it starts with an `@`). The label tells OVOS what that function is for, for example, "run this when the user asks about the weather" or "run this only if nothing else understood the request." It's like sticking a labeled note on a drawer, so the system knows what's inside without opening it. This page lists the available labels and what each one does. New to skills? See [Skill Classes](skill-classes.md) or the [Glossary](glossary.md).

All decorators are importable from `ovos_workshop.decorators`.

```python
from ovos_workshop.decorators import (
    intent_handler,
    fallback_handler,
    converse_handler,
    conversational_intent,
    common_query,
    skill_api_method,
    adds_context,
    removes_context,
    homescreen_app,
    resting_screen_handler,
    killable_intent,
    killable_event,
)
from ovos_workshop.decorators.layers import (
    layer_intent,
    enables_layer,
    disables_layer,
    replaces_layer,
    removes_layer,
    resets_layers,
)
from ovos_workshop.decorators.ocp import (
    ocp_search,
    ocp_play,
    ocp_pause,
    ocp_resume,
    ocp_next,
    ocp_previous,
    ocp_featured_media,
)

```

---

## Intent Decorators

### `@intent_handler`

`intent_handler`: `ovos_workshop/decorators/__init__.py`

Register a method as a [Padatious](padatious-pipeline.md) (`.intent` file) or [Adapt](adapt-pipeline.md) (`IntentBuilder`) intent handler.

```python
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder

# Padatious intent file
@intent_handler("my.intent")
def handle_my(self, message): ...

# Adapt intent
@intent_handler(IntentBuilder("GreetIntent").require("Hello"))
def handle_greet(self, message): ...

# With voc blacklist — suppress adapt keywords in this handler
@intent_handler("my.intent", voc_blacklist=["StopKeyword"])
def handle_my_no_stop(self, message): ...

```

A method can have multiple `@intent_handler` decorators to handle multiple intents with the same function.

---

### `@conversational_intent`

`conversational_intent`: `ovos_workshop/decorators/__init__.py`

Register a Padatious `.intent` file as a converse-only matcher. Only active when the skill is in converse mode. Requires the skill to extend `ConversationalSkill`.

> **Note:** Only Padatious intents are supported, not Adapt.

```python
from ovos_workshop.decorators import conversational_intent

@conversational_intent("help.intent")
def handle_help_in_converse(self, message): ...

```

---

### `@fallback_handler`

`fallback_handler`: `ovos_workshop/decorators/__init__.py`

Register a method as a fallback handler with a given priority (0-100, lower = higher priority).

```python
from ovos_workshop.decorators import fallback_handler

@fallback_handler(priority=50)
def handle_unknown(self, message):
    self.speak("I don't know.")
    return True  # consumed — stop checking other fallbacks

```

---

### `@common_query`

`common_query`: `ovos_workshop/decorators/__init__.py`

Register a method as a CommonQuery handler. The method must return `(answer, confidence)` or `None`.

```python
from ovos_workshop.decorators import common_query

@common_query(callback=None)
def handle_query(self, phrase, lang):
    if "meaning of life" in phrase:
        return "42", 0.99
    return None, 0

```

`callback` is optional. If provided, it is called with `(phrase, answer, lang)` after the answer is spoken.

---

## Converse Decorators

### `@converse_handler`

`converse_handler`: `ovos_workshop/decorators/__init__.py`

Alias a method as the skill's `converse` handler instead of overriding `converse()` directly.

```python
from ovos_workshop.decorators import converse_handler

@converse_handler
def my_converse(self, message):
    return False  # not consumed

```

---

## Context Decorators

`adds_context`: `ovos_workshop/decorators/__init__.py`
`removes_context`: `ovos_workshop/decorators/__init__.py`

These run **after** the decorated method completes.

### `@adds_context`

```python
from ovos_workshop.decorators import adds_context

@adds_context("OrderContext", "ordering")
def handle_order(self, message):
    self.speak("What would you like to order?")

```

### `@removes_context`

```python
from ovos_workshop.decorators import removes_context

@removes_context("OrderContext")
def handle_cancel(self, message):
    self.speak("Order cancelled.")

```

---

## Killable, Intent Layer, and OCP Decorators

The killable/abortable decorators (interrupting a running handler), the intent
layer decorators (enabling/disabling groups of intents for modal flows), and
the OCP media-playback decorators are each substantial families of their own.
They are documented on [Advanced Decorators](decorators-advanced.md).

---

## GUI / Homescreen Decorators

!!! warning "Homescreens are being deprecated"
    Skill-provided home/idle screens are on their way out. In the GUI rework, the
    idle screen becomes a job for the display backend rather than a skill (see
    [Home Screen](homescreen.md) and [Screens on OVOS Today](gui-status.md)). The
    decorators below still work on the legacy stack but should not be treated as
    the forward-looking way to build a home screen.

### `@homescreen_app`

`homescreen_app`: `ovos_workshop/decorators/__init__.py`

Register a method as a homescreen app launcher. The icon file must be inside the `gui/` subfolder of the skill.

```python
from ovos_workshop.decorators import homescreen_app

@homescreen_app(icon="my_app.png", name="My App")
def launch_app(self, message):
    self.gui.show_page("main.qml")

```

### `@resting_screen_handler`

`resting_screen_handler`: `ovos_workshop/decorators/__init__.py`

Register a method as a **resting screen** (idle screen) handler, optionally shown
when the device enters idle mode. `name` is the name the resting screen registers
under. See [Home Screen](homescreen.md) for the full idle-screen walkthrough.

```python
from ovos_workshop.decorators import resting_screen_handler

@resting_screen_handler(name="Clock")
def show_clock(self, message):
    self.gui.show_page("clock.qml")

```

---

## API Decorator

### `@skill_api_method`

`skill_api_method`: `ovos_workshop/decorators/__init__.py`

Expose a method over the bus so other skills or applications can call it via `SkillApi`. See [Skill API: Inter-Skill RPC](skill-api.md) for the full RPC documentation.

```python
from ovos_workshop.decorators import skill_api_method

@skill_api_method
def get_data(self, key: str) -> dict:
    """Return data for key."""
    return {"key": key, "value": self.settings.get(key)}

```

The method is registered as `{skill_id}.get_data` on the bus.

---

## Combining Decorators

Python applies stacked decorators **bottom-up** (innermost first). Whether
order matters depends on what each decorator does to the function:

- `@intent_handler`, `@fallback_handler`, `@common_query`, `@conversational_intent`,
  `@homescreen_app`, and `@skill_api_method` are pure **tags**. They set an
  attribute on the function object and return it unchanged, without wrapping
  it. Because of this, stacking one of these with a wrapping decorator (like
  `@killable_intent` or `@adds_context`) works in **either order**. The tag
  ends up on whatever object is on top by the time it runs, and
  `functools.wraps` propagates it if another wrapper is added afterward.

```python
# Both of these register the intent correctly — order does not matter here,
# because @intent_handler never wraps the function.
@killable_intent(react_to_stop=True)
@intent_handler("long_task.intent")
def handle_long_task(self, message):
    ...

@intent_handler("long_task.intent")
@killable_intent(react_to_stop=True)
def handle_long_task(self, message):
    ...
```

- `@adds_context`, `@removes_context`, `@killable_intent`, `@killable_event`,
  and the intent-layer decorators (`@enables_layer`, `@disables_layer`, and so on)
  do wrap the function. They run code before and/or after calling it.
  When you stack two wrapping decorators together, the order changes what
  actually executes and when, so make sure the one that should run
  last (for example, `@adds_context`, which fires after the handler body returns) is
  the outermost:

```python
@adds_context("ConfirmContext")   # runs after handle_confirm() returns
@intent_handler("confirm_order.intent")
def handle_confirm(self, message):
    self.speak("Order confirmed.")
```

---

## Coming from mycroft-core

!!! note "Renamed / merged decorators"
    mycroft-core split intent registration into two separate decorators:
    `@intent_handler` for Adapt intents and a second `@intent_file_handler`
    for Padatious `.intent` files. In `ovos-workshop`, **`@intent_file_handler`
    no longer exists**. Both cases are handled by the single
    [`@intent_handler`](#intent_handler) shown above, which accepts either an
    `.intent` filename (Padatious) or an `IntentBuilder` (Adapt). If you are
    porting an old skill, replace every `@intent_file_handler("x.intent")`
    with `@intent_handler("x.intent")`. See
    [Migrating from Mycroft](migrating-from-mycroft.md) for the full list of
    changes.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Advanced Decorators](decorators-advanced.md)
**Related:** [Skill Classes](skill-classes.md) · [OVOSSkill](ovos-skill.md) · [Intent Design](intents.md) · [Permissions & Activation Control](permissions.md)
