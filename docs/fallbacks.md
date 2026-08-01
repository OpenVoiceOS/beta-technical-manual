# Fallback [Skill](skill-design-guidelines.md)

!!! abstract "In a nutshell"
    A fallback skill is a catch-all. It only gets a turn when no regular skill understood what you said. Use it for things like "sorry, I didn't catch that", a web search, or a large language model that should answer only when nothing more specific did. Each fallback has a priority number, so you can decide which ones try first. Broad "I don't understand" handlers go last. To see how this fits into the bigger picture, read the [Fallback Pipeline](fallback-pipeline.md), or the [Glossary](glossary.md) for terms.

??? info "📐 Formal specification"
    Fallback handling is specified by **[OVOS-FALLBACK-1 — Fallback Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/fallback.md)** (a formal [architecture spec](architecture-specs.md)). A skill declares itself a fallback handler by calling `register_fallback()`, which emits `ovos.skills.fallback.register` with a `skill_id` and integer `priority`. The fallback **pipeline plugin** builds a pool ordered by **ascending** priority (**lower number runs earlier**, matching this page). It then pings each candidate with `ovos.skills.fallback.ping` and reads its `can_answer()` verdict off the `ovos.skills.fallback.pong` reply, dispatching in priority order to the first willing skill via `ovos.skills.fallback.<skill_id>.request`. A catch-all skill is typically registered at a high number (e.g. `100`) so every utterance gets a response. This is the opposite of what "priority" usually implies elsewhere: a *lower* number here means the handler is tried *sooner*, not that it is more important.

A **Fallback** skill is the last line of defense. It is only consulted when no intent matched the utterance. Use it for a catch-all ("I didn't understand"), an LLM, a web search, or any handler that should run *only* when nothing more specific did.

## Order of precedence

Fallback Skills each have a **priority** and are tried in order from low priority value to high priority value. Lower number means tried earlier. When a Fallback Skill handles the **[Utterance](life-of-an-utterance.md)** it returns `True` and no further fallbacks are tried.

!!! note "Two different facts: internal stages vs. your pick"
    The pipeline internally splits the 0-101 priority space into three dispatch stages,
    checked in this order: `fallback_high` (priority above 0, up to and including 5),
    `fallback_medium` (above 5, up to and including 90), and `fallback_low` (above 90, up to and
    including 101). A priority of exactly `5` lands in `fallback_high`; exactly `90` lands in
    `fallback_medium`. These are implemented directly
    in `ovos-core`'s `FallbackService` (no separate pipeline plugin package involved).
    That is an implementation detail, not a recommendation. The **recommended pick ranges**
    below are a separate, coarser convention. They help you choose *where in the medium/low stages*
    your own handler's priority should sit.

Pick your priority number by how broad your handler is. Remember, a smaller number runs **earlier**, a larger number runs **later**:

- Very specific handlers should use a **small number** (e.g. `0–49`) so they run before broad ones and get first refusal.
- Handlers that fit a middle ground should use `50–74`.
- Broad, catch-all handlers (an LLM, "I don't understand") should use a **large number** (`75–100`) so specific skills run and win first.

---

## Fallback Handlers

Import the `FallbackSkill` base class, derive from it, and register a handler with the fallback system.

The handler decides whether it can handle the **Utterance**, speaks if it can, and returns `True` if it handled it or `False` if not.

```python
from ovos_workshop.skills.fallback import FallbackSkill


class MeaningFallback(FallbackSkill):
    """
    A Fallback skill to answer the question about the
    meaning of life, the universe and everything.
    """

    def initialize(self):
        # register the handler with priority 10
        self.register_fallback(self.handle_fallback, 10)

    def handle_fallback(self, message):
        utterance = message.data.get("utterances", [""])[0]
        if ("what" in utterance and "meaning" in utterance and
                ("life" in utterance or "universe" in utterance
                 or "everything" in utterance)):
            self.speak("42")
            return True
        return False
```

> **NOTE**: a `FallbackSkill` can register any number of fallback handlers.

You can find this example in [the fallback-meaning skill example](https://github.com/forslund/fallback-meaning).

---

## Decorators

Alternatively, use the `@fallback_handler` decorator — no manual `register_fallback` call needed.

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler


class MeaningFallback(FallbackSkill):

    @fallback_handler(priority=10)
    def handle_fallback(self, message):
        utterance = message.data.get("utterances", [""])[0]
        if ("what" in utterance and "meaning" in utterance and
                ("life" in utterance or "universe" in utterance
                 or "everything" in utterance)):
            self.speak("42")
            return True
        return False
```

`fallback_handler` can also be imported from `ovos_workshop.decorators.fallback_handler`.

---

## `can_answer`

Fallback skills can report *whether* they would answer a question, without executing the action or speaking. This lets other OVOS components probe how an utterance will be handled with no side effects. It also lets the pipeline skip work when it isn't needed.

This method is **not implemented by default**. The base implementation raises `NotImplementedError`. The skills service pings every fallback skill (`ovos.skills.fallback.ping` → `can_answer()`) to decide whether it is even worth invoking. Always override `can_answer` in a real `FallbackSkill`:

```python
from ovos_bus_client.session import SessionManager


class MeaningFallback(FallbackSkill):

    def can_answer(self, message) -> bool:
        """
        Return True if this skill could answer the utterance as a fallback.

        - Utterance transcriptions: message.data["utterances"]
        - Session (e.g. for language): SessionManager.get(message)
        """
        utterances = message.data.get("utterances", [])
        return any("meaning" in u for u in utterances)
```

> The `can_answer` signature takes the full `Message` (transcriptions are in `message.data["utterances"]`), not a bare list of strings.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*
