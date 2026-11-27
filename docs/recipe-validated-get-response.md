# Collecting structured input: `get_response` with a validator

!!! abstract "In a nutshell"
    You build an `OVOSSkill` intent handler that collects one specific, validated value, using `get_response(validator=..., on_fail=..., num_retries=...)`. `num_retries` limits the silent answers. A time limit stops the questions when the user keeps giving wrong answers.

**When you'd want this:** an intent needs one specific piece of information, such as a number in a known range, not a free-form sentence. The skill asks again after a bad answer, and stops with a clear message when no valid answer comes.

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
- `on_fail` is what the skill speaks after a failed validation, before it listens again. It can be a dialog name or a string. It can also be a callable that receives the list of transcriptions and returns the string to speak.
- `num_retries` counts only consecutive silent answers. With `2` above, `get_response` stops after two silent answers in a row. An answer that fails validation causes a reprompt and sets the counter to zero. Thus a user who keeps giving wrong answers is asked again until a time limit. The time limit is `(skills.get_response_timeout + 15)` seconds multiplied by the maximum attempts. The maximum attempts is `num_retries + 1`, or `2` when `num_retries` is `-1`. `get_response_timeout` has a default of `20`. After the time limit, `get_response` returns `None`.
- `get_response` returns the matched utterance as a `str` on success, or `None` if no valid response was ever captured, whether because retries ran out, the user said "cancel", or nobody answered. `handle_set_temperature` above checks for `None` and speaks a distinct "gave up" dialog rather than assuming `response` is always usable. See [Get User Response](prompts.md#2-request-extra-information-with-get_response) for `get_response` alongside `ask_yesno` and `ask_selection`.

!!! tip "Full production example"
    [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl)'s `handle_custom_eye_color` chains three validated `get_response` calls back to back, one each for red, green, and blue (0-255), all three with `on_fail="error_rgbvalue"` and `num_retries=2`, then falls through to `ask_yesno` to offer saving the result as the default eye color.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Get User Response](prompts.md#2-request-extra-information-with-get_response) · [Continuous conversation](recipe-multi-turn-conversation.md) · [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl)
