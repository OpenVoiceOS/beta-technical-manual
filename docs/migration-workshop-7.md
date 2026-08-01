# Migrating Through the ovos-workshop 7.0.0 Release Train

!!! abstract "In a nutshell"
    Skill maintainers are affected. Four `ovos-workshop` major versions
    landed in about a day (4.0.0 → 7.0.0), each breaking a different part
    of the `OVOSSkill` family, and the later-removed `CommonQuerySkill`
    belongs to the same train. Fix it by applying all four `OVOSSkill`
    changes at once and dropping `CommonQuerySkill` in favor of the
    pipeline-plugin approach.

### The ovos-workshop 2025-06 release train (4.0.0 → 7.0.0)

`ovos-workshop` went through four major-version breaks on the `OVOSSkill`
family in the space of about a day, each one landing on top of the last
before the previous change had even settled. A skill author jumping the
gap felt it as a moving target: `can_answer` went abstract, converse moved
into a mixin, `can_stop` briefly went hard-abstract then was loosened
hours later, and the mixin's own method name turned out to be wrong for
about a day before being renamed. Anyone upgrading past a pre-2025-06
workshop version in one hop needs to treat all four changes as landing at
once, not as separable steps.

Four major versions of `ovos-workshop` shipped on the same day
(2025-06-07/08). Each is a separate breaking change to the `OVOSSkill`
family. If you are jumping from a pre-2025-06 workshop version to anything
after `7.0.0`, expect all four of these to apply at once.

**v4.0.0: `FallbackSkill.can_answer` becomes abstract.**

```python
# old: default True if any handler registered, no override needed
class MySkill(FallbackSkill):
    def handle_fallback(self, message):
        ...

# new: must implement can_answer explicitly
class MySkill(FallbackSkill):
    def can_answer(self, utterances: list[str], lang: str) -> bool:
        return True  # or real logic
    def handle_fallback(self, message):
        ...
```

`FallbackSkill.make_intent_failure_handler(cls, bus)` (the old mycroft-style
bus-driven fallback dispatcher) is removed with it (ovos-workshop `c066bc3`, #336).

**v5.0.0: converse moves out of `OVOSSkill` into a mixin.**

```python
# old: converse lived directly on OVOSSkill
class MySkill(OVOSSkill):
    def converse(self, message=None):
        ...

# new: subclass the mixin too
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(OVOSSkill, ConversationalSkill):
    def can_converse(self, message) -> bool:
        return True
    def converse(self, message=None):
        ...
```

An `OVOSSkill` subclass that overrides `converse()` without also inheriting
`ConversationalSkill` compiles fine but is silently never called by the
pipeline (ovos-workshop `f725f5e`, #339).

**v6.0.0 / v6.0.1: `can_stop` conditional abstract method.**
`can_stop(self, message)` briefly became a hard `@abc.abstractmethod`
(`10f9781`, #344) then was loosened the same day to only require
overriding if the skill also overrides `stop`/`stop_session`
(`813f7b5`, #346, released as `6.0.1`). If you implement `stop()` or
`stop_session()`, also implement `can_stop()`.

**v7.0.0: `can_answer` on `ConversationalSkill` renamed to `can_converse`.**
The v5.0.0 mixin shipped with the wrong method name for about a day. Rename
`can_answer` → `can_converse` in any `ConversationalSkill` subclass
(ovos-workshop `1fdd532`, #348).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `FallbackSkill.can_answer` concrete/optional | before `4.0.0` (2025-06-07) | unverified | `4.0.0` |
| `converse()` on `OVOSSkill` directly | before `5.0.0` (2025-06-07) | unverified | `5.0.0` |
| `stop_is_implemented` property / concrete `can_stop` | before `6.0.0` | `6.0.1` (conditional requirement) | `6.0.0` (briefly hard), loosened in `6.0.1` |
| `ConversationalSkill.can_answer` | `5.0.0` to `6.0.1` (about one day) | none | `7.0.0` |

### CommonQuerySkill removal

`CommonQuerySkill` sat deprecation-flagged for the better part of two
years before it was finally cut in one commit, with no
direct successor class left in `ovos-workshop`. The removal only
completed a migration that had already happened underneath it: the
matching hardcoded common-query wiring inside `ovos-core` itself had been
pulled out earlier, when the whole intent-service module turned into a
config-driven OPM pipeline factory, so by the time the skill class was
deleted, common-query matching already lived in whichever pipeline plugin
happened to own it.

`CommonQuerySkill` had been deprecation-flagged since ovos-workshop
`4.0.0` and was deleted entirely (259 lines, including the `CQSMatchLevel`
enum and `CQS_match_query_phrase`/`CQS_action` abstract methods) in
`6382d0a` (#400, 2026-04-08), ahead of the `8.0.0` release. There is no
direct successor class in `ovos-workshop`. Common-query matching now lives
in whatever pipeline plugin currently owns it (check `ovos-core`'s
common-query pipeline plugin). On `ovos-core` itself, the equivalent
hardcoded common-query wiring was removed from `ovos_core.intent_services`
in `62024dbf98` (#690, 2025-06-10, first stable release `1.3.0`) when the
whole intent-service module became a config-driven OPM pipeline factory.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `ovos_workshop.skills.common_query_skill.CommonQuerySkill` | before `4.0.0` | `4.0.0` to pre-`8.0.0` | `6382d0a` (2026-04-08, pre-`8.0.0`) |
| `ovos-core` hardcoded common-query wiring | before `62024dbf98` | unverified | `62024dbf98` (`1.3.0`, 2025-06-10) |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Skill Maintainers](updating-skills.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
