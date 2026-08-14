# Skill Classes

!!! abstract "In a nutshell"
    A "skill" is an add-on that gives your voice assistant a new ability. Rather than building each one from scratch, you start from a ready-made template (a "base class") and customize it. This page lists the available templates: a general-purpose one and specialized ones for things like games, media playback, or catch-all replies, so you can pick the closest fit. Unsure what a term means? See the [Glossary](glossary.md). For hands-on basics see [Skill Best Practices](skill-best-practices.md).

`ovos-workshop` provides all base classes needed to write skills for OpenVoiceOS. Every skill ultimately inherits from `OVOSSkill`.

**Package:** `ovos-workshop` | **Entry point group:** `opm.skill`

---

## Class Hierarchy

```text
OVOSSkill                             ovos_workshop/skills/ovos.py
├── ConversationalSkill               ovos_workshop/skills/converse.py
│   └── ActiveSkill                   ovos_workshop/skills/active.py
│       └── PassiveSkill              ovos_workshop/skills/passive.py
├── FallbackSkill                     ovos_workshop/skills/fallback.py
├── IdleDisplaySkill                  ovos_workshop/skills/idle_display_skill.py
├── OVOSCommonPlaybackSkill           ovos_workshop/skills/common_play.py
│   └── OVOSGameSkill                 ovos_workshop/skills/game_skill.py
│       └── ConversationalGameSkill   ovos_workshop/skills/game_skill.py
├── UniversalSkill                    ovos_workshop/skills/auto_translatable.py
│   └── UniversalFallback             ovos_workshop/skills/auto_translatable.py
└── OVOSAbstractApplication           ovos_workshop/app.py

```

---

## OVOSSkill

**Module:** `ovos_workshop.skills.ovos.OVOSSkill`

The universal base class. Every skill and application ultimately inherits from `OVOSSkill`. Handles intent registration, resource files, settings, GUI interface, [messagebus](bus-service.md) events, and the full skill lifecycle.

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import intent_handler

class HelloWorldSkill(OVOSSkill):
    """A minimal OVOS skill."""

    @intent_handler("hello.intent")
    def handle_hello(self, message):
        """Respond to a greeting."""
        self.speak_dialog("hello.response")


def create_skill():
    return HelloWorldSkill()

```

`pyproject.toml` entry point:

```toml
[project.entry-points."opm.skill"]
hello-world-skill = "hello_world_skill:HelloWorldSkill"

```

### Constructor

```python
OVOSSkill(
    name: str = None,          # DEPRECATED, use skill_id
    bus: MessageBusClient = None,
    resources_dir: str = None,
    settings: JsonStorage = None,  # settings object, else loaded from the skill config path
    gui: GUIInterface = None,
    skill_id: str = "",        # set by SkillLoader
)

```

Modern skills should always accept `**kwargs` and pass them to `super().__init__`:

```python
class MySkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

```

### Lifecycle Methods

Override these in your skill class:

| Method | When called | Notes |
|---|---|---|
| `initialize()` | After full startup | Legacy. Prefer `__init__`. |
| `get_intro_message()` | First run only | Return a dialog name or string to speak on first install |
| `stop()` | User/system stop | Return `True` if the skill handled the stop |
| `stop_session(session)` | Per-session stop | Called before `stop()`. Return `True` to prevent global `stop()` |
| `can_stop(message)` | Before stop | Must be implemented if `stop()` or `stop_session()` is defined |
| `shutdown()` | Skill unload | Final cleanup after all other shutdown steps |

### Startup Sequence (`_startup`)

1. Set `skill_id`


2. Init settings (`_init_settings`)


3. Bind bus (`bind`)


4. Init GUI (skipped if a `gui` object was already passed to the constructor)


5. Load resource files (`load_data_files`)


6. Register `skill.json` examples with the homescreen (`_register_skill_json`)


7. Register decorated intents (`_register_decorated`)


8. Register homescreen app if `@homescreen_app` used


9. Register resting screen if `@resting_screen_handler` used


10. Call `initialize()`


11. Check first run


12. Set status to `ready`

### Shutdown Sequence

1. `SkillManager` calls `shutdown()`: skill-specific cleanup


2. `SkillManager` calls `default_shutdown()`, which:
    1. Calls `stop()`
    2. Stores settings
    3. Shuts down the GUI
    4. Shuts down the event scheduler, clears events
    5. Emits `detach_skill`

!!! note
    `shutdown()` and `default_shutdown()` are two separate calls made by
    `SkillManager` when it unloads a skill. `default_shutdown()` does not call
    `shutdown()` itself. Override `shutdown()` for your own cleanup code.
    Never call `default_shutdown()` directly.

This constructor/lifecycle/startup/shutdown sequence is shared by every `OVOSSkill`
subclass below. See [OVOSSkill](ovos-skill.md) for event scheduling and the full
list of bus events an `OVOSSkill` handles, and [Skill API: Inter-Skill RPC](skill-api.md)
for `SkillApi`.

### Key Properties

**[Session](session.md)-aware (read from current Session):**

| Property | Type | Description |
|---|---|---|
| `lang` | `str` | BCP-47 language of the current request |
| `core_lang` | `str` | Default configured language |
| `secondary_langs` | `list` | Configured secondary languages |
| `location` | `dict` | Location preferences |
| `location_timezone` | `str` | Timezone code |
| `system_unit` | `str` | `"metric"` or `"imperial"` |

**Infrastructure:**

| Property | Type | Description |
|---|---|---|
| `settings` | `JsonStorage` | Persistent skill settings |
| `bus` | `MessageBusClient` | messagebus connection |
| `gui` | `SkillGUI` | GUI interface |
| `file_system` | `FileSystemAccess` | Managed local file access |
| `resources` | `SkillResources` | Resource files for `self.lang` |
| `event_scheduler` | `EventSchedulerInterface` | Schedule future bus events |
| `audio_service` | `OCPInterface` | Control audio/[OCP](ocp-pipeline.md) playback |
| `is_fully_initialized` | `bool` | True after `_startup` completes |

### Speaking

```python
self.speak("Hello world")
self.speak_dialog("my.dialog.file")            # uses locale/<lang>/dialog/my.dialog.file
self.speak_dialog("my.dialog", data={"name": "Alice"})  # Mustache templating

```

### Getting User Input

`get_response`, `ask_yesno`, and `ask_selection` ask the user a question and capture the
reply. See [Asking the User for Responses](prompts.md) for the full reference, including
the `validator`, `on_fail`, and `num_retries` options.

### RuntimeRequirements

!!! note
    `RuntimeRequirements` is a deprecated mechanism. See [Runtime Requirements](skill-runtime-requirements.md) for what it currently does.

Override the class property to declare connectivity needs:

```python
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements

@classproperty
def runtime_requirements(cls):
    return RuntimeRequirements(
        network_before_load=False,
        internet_before_load=False,
        gui_before_load=False,
        requires_internet=False,
        requires_network=False,
        requires_gui=False,
        no_internet_fallback=False,
        no_network_fallback=False,
        no_gui_fallback=True,
    )

```

All nine fields default `True` except `gui_before_load`, `requires_gui`,
`no_internet_fallback`, and `no_network_fallback` (default `False`). Used by `SkillManager`
to defer loading until requirements are met. See [OVOSSkill: RuntimeRequirements](ovos-skill.md#runtimerequirements)
for the full field reference.

---

## Which Class Do I Pick?

Everything below `OVOSSkill` in the hierarchy adds one specific capability. The full
per-class reference, including constructors, code samples, and every method you must
implement, lives on **[Skill Classes Reference](skill-classes-reference.md)**.

| If you need... | Use | Extends |
|---|---|---|
| A plain intent-driven skill | `OVOSSkill` (this page) | — |
| Explicit converse control (`activate()`/`deactivate()`) | [ConversationalSkill](skill-classes-reference.md#conversationalskill) | `OVOSSkill` |
| A skill that's always in the converse active-skills list | [ActiveSkill](skill-classes-reference.md#activeskill) | `ConversationalSkill` |
| A skill that passively hears every utterance without claiming any (e.g. metrics) | `PassiveSkill` | `ActiveSkill` |
| To catch utterances that matched no intent | [FallbackSkill](skill-classes-reference.md#fallbackskill) | `OVOSSkill` |
| To answer natural-language questions with a confidence score | [`@common_query`](skill-classes-reference.md#commonquery-common_query-on-ovosskill) decorator | `OVOSSkill` |
| To play audio/video and appear in the OCP media browser | [OVOSCommonPlaybackSkill](skill-classes-reference.md#ovoscommonplaybackskill) | `OVOSSkill` |
| A structured, OCP-integrated voice game | [OVOSGameSkill](skill-classes-reference.md#ovosgameskill) | `OVOSCommonPlaybackSkill` |
| A voice game with a converse loop for free-form commands | [ConversationalGameSkill](skill-classes-reference.md#conversationalgameskill) | `OVOSGameSkill` |
| A skill that auto-translates utterances and speech | [UniversalSkill](skill-classes-reference.md#universalskill) | `OVOSSkill` |
| A fallback skill that also auto-translates | [UniversalFallback](skill-classes-reference.md#universalfallback) | `UniversalSkill` + `FallbackSkill` |
| A standalone app with no intent service | [OVOSAbstractApplication](skill-classes-reference.md#ovosabstractapplication) | — |

See also [Skill Launcher](skill-classes-reference.md#skill-launcher) for how plugin-based
skills are loaded, and [Decorators Quick Reference](skill-classes-reference.md#decorators-quick-reference)
for the full decorator list.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Skill Classes Reference](skill-classes-reference.md) · [Decorators](decorators.md)
**Related:** [OVOSSkill](ovos-skill.md) · [Fallback Skill](fallbacks.md) · [Common Query Framework](common-query.md) · [OCP Skills](ocp-skills.md)
