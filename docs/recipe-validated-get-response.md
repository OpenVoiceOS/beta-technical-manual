# Collecting structured input: `get_response` with a validator

!!! abstract "In a nutshell"
    You build an `OVOSSkill` intent handler that collects one specific, validated value, using `get_response(validator=..., on_fail=..., num_retries=...)` with a bounded retry count.

**When you'd want this:** an intent needs one specific piece of information, such as a number in a known range, not a free-form sentence. The user should be re-prompted on a bad answer, a limited number of times, and the skill should give up gracefully rather than loop forever.

```python
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class ThermostatSkill(OVOSSkill):
    @intent_handler("set_temperature.intent")
    def handle_set_temperature(self, message):
        def in_range(utterance: str) -> bool:
            try:
                return 10 <= int(utterance) <= 30
            except ValueError:
                return False

        response = self.get_response("ask_temperature",
                                     validator=in_range,
                                     on_fail="temperature_out_of_range",
                                     num_retries=2)
        if response is None:
            self.speak_dialog("temperature_not_set")
            return

        self.settings["target_temperature"] = int(response)
        self.speak_dialog("temperature_set", {"temp": response})
```

### Moving parts

- `get_response(dialog='', data=None, validator=None, on_fail=None, num_retries=-1, message=None, wait=True)` speaks `dialog`, listens for a reply, and, if `validator` is given, keeps re-asking until the reply passes it or the retries run out. `validator` takes the raw utterance string and returns `True`/`False`; `in_range` above rejects anything that isn't an integer between 10 and 30.
- `on_fail` is what gets spoken on a failed validation, before listening again. It can be a dialog name/string, or a `(str) -> str` callable that builds a message from the failing utterance.
- `num_retries` bounds the re-prompt loop. `2` above means the user gets up to three attempts total (the original ask plus two retries) before `get_response` gives up. `-1`, the default, retries indefinitely, but a silent (no-answer) timeout with `-1` still only retries once. Cap `num_retries` deliberately whenever a bad or silent answer should end the interaction instead of looping.
- `get_response` returns the matched utterance as a `str` on success, or `None` if no valid response was ever captured, whether because retries ran out, the user said "cancel", or nobody answered. `handle_set_temperature` above checks for `None` and speaks a distinct "gave up" dialog rather than assuming `response` is always usable. See [Get User Response](prompts.md#2-request-extra-information-with-get_response) for `get_response` alongside `ask_yesno` and `ask_selection`.

!!! tip "Full production example"
    [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl)'s `handle_custom_eye_color` chains three validated `get_response` calls back to back, one each for red, green, and blue (0-255), each with its own `on_fail` dialog and `num_retries=2`, then falls through to `ask_yesno` to offer saving the result as the default eye color.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Get User Response](prompts.md#2-request-extra-information-with-get_response) · [Continuous conversation](recipe-multi-turn-conversation.md) · [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl)
