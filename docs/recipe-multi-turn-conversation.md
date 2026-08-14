# Continuous conversation: multi-turn dialog with `converse` and `get_response`

!!! abstract "In a nutshell"
    You build a `ConversationalSkill` that runs a multi-step exchange, combining `get_response` for a linear form with `converse` for open-ended back-and-forth.

!!! warning "Testing multi-turn flows over the bus"
    When driving this recipe from a test or script, re-fetch the live session before each
    follow-up utterance. Reusing a stale serialized `Session` erases the activation from
    turn 1. See [Testing Your Skill](testing-your-skill.md#multi-turn-tests-always-re-pull-the-session).

**When you'd want this:** the interaction needs more than one exchange. Booking a table means asking for a time, a party size, and a name in sequence, or reacting to whatever the user says next without them repeating the skill's name.

There are two complementary tools for this:

- `self.get_response(...)`: call it *from inside an intent handler* to ask one question and block until an answer (or timeout) comes back. Best for a short, linear form.
- `ConversationalSkill.converse(message)`: override this to intercept **every** utterance while your skill is "active" (recently used), before intent matching even runs. Best for an open-ended back-and-forth.

```python
from ovos_workshop.skills.converse import ConversationalSkill
from ovos_workshop.decorators import intent_handler


class TableBookingSkill(ConversationalSkill):
    def initialize(self):
        self._pending_booking = None

    @intent_handler("book_table.intent")
    def handle_book_table(self, message):
        party_size = self.get_response("ask_party_size")
        if party_size is None:
            self.speak_dialog("booking_cancelled")
            return
        time_str = self.get_response("ask_time")
        if time_str is None:
            self.speak_dialog("booking_cancelled")
            return

        self._pending_booking = {"size": party_size, "time": time_str}
        # stay "active" so the next thing the user says, even without
        # re-invoking this skill, is routed to converse() below
        self.activate()
        self.speak_dialog("confirm_booking", self._pending_booking)

    def converse(self, message):
        if self._pending_booking is None:
            return False  # not our turn, let normal intent matching happen

        utterance = message.data.get("utterances", [""])[0]
        if self.voc_match(utterance, "yes"):
            self.speak_dialog("booking_confirmed", self._pending_booking)
            self._pending_booking = None
            return True
        if self.voc_match(utterance, "no"):
            self.speak_dialog("booking_cancelled")
            self._pending_booking = None
            return True
        return False  # didn't understand, let something else try
```

### Moving parts

- `get_response(dialog="", data=None, validator=None, on_fail=None, num_retries=-1)` speaks `dialog` (rendered with `data`), then waits for a reply. It returns the utterance string, or `None` if the user didn't answer / said "cancel". `validator` can reject and re-ask (e.g. requiring a number).
- `converse()` only runs while the skill is **active**: recently handled an intent, or explicitly kept alive with `self.activate(duration_minutes=...)` as shown above. It must subclass `ConversationalSkill` (not plain `OVOSSkill`) to be dispatched. Returning `True` claims the utterance, `False` lets normal pipeline processing continue. See [Converse](converse.md) and the [Converse Pipeline](converse-pipeline.md) for how a skill enters and leaves the active list.
- `self.voc_match(utterance, "yes")` checks against `locale/en-us/vocab/yes.voc`. See [Skill Design Guidelines](skill-design-guidelines.md) for vocab file conventions.
- [Context](context.md) (`self.set_context()`) is the lighter-weight alternative when you only need to bias which of *your own* intents can match next, rather than intercepting raw utterances. In practice that means the Adapt `.require()` path, because the skill API cannot declare `requires_context` / `excludes_context` on an intent yet. The entries `set_context` writes are already gate-visible (see [Conversational Context](context.md)).

!!! tip "Full production example"
    [`ovos-skill-parrot`](https://github.com/OpenVoiceOS/ovos-skill-parrot) is a minimal `ConversationalSkill` with an explicit `can_converse`/`converse` pair, good for seeing the bare mechanism with nothing else around it. [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) shows the same tools used for real work, combining `converse` with `get_response` to collect an alert's details across several turns.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Converse](converse.md) · [Converse Pipeline](converse-pipeline.md) · [Validated slot collection](recipe-validated-get-response.md)
