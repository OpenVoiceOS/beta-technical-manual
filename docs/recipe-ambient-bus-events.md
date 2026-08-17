# Ambient behavior from bus events: react to listening state and time of day

!!! abstract "In a nutshell"
    You build an `OVOSSkill` that reacts to bus events instead of utterances, using `add_event` on `recognizer_loop:*` events plus a repeating scheduled check.

**When you'd want this:** a skill needs to do something not triggered by an utterance at all. Examples include dimming a light while the device is actively listening, or changing its greeting depending on whether it's morning or night, driven purely by bus events other services already emit.

```python
import datetime

from ovos_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill


class AmbientMoodSkill(OVOSSkill):
    def initialize(self):
        # the listener (ovos-dinkum-listener) emits these around each
        # recording, independent of any skill or intent
        self.add_event("ovos.listener.record.started", self.handle_listening_start)
        self.add_event("ovos.listener.record.ended", self.handle_listening_end)
        # ovos-audio emits these around each spoken response
        self.add_event("ovos.audio.output.started", self.handle_speaking_start)
        self.add_event("ovos.audio.output.ended", self.handle_speaking_end)

        # check the time of day once now, and again every 15 minutes
        self._update_time_of_day()
        self.schedule_repeating_event(self._update_time_of_day, None, 15 * 60,
                                       name="mood_time_check")

    def handle_listening_start(self, message):
        self._set_mood("listening")

    def handle_listening_end(self, message):
        self._set_mood("idle")

    def handle_speaking_start(self, message):
        self._set_mood("speaking")

    def handle_speaking_end(self, message):
        self._set_mood("idle")

    def _update_time_of_day(self, message=None):
        hour = datetime.datetime.now().hour
        self.is_daytime = 7 <= hour < 20

    def _set_mood(self, mood):
        self.bus.emit(Message("ovos.ambient_mood.changed",
                               {"mood": mood, "daytime": self.is_daytime}))
```

### Moving parts

- `ovos.listener.record.started` / `ovos.listener.record.ended` bracket an active recording (wake word already triggered). `ovos.audio.output.started` / `.ended` bracket the device speaking and are emitted by `ovos-audio`. Each of these four also travels under a pre-spec name (`recognizer_loop:record_begin`, `recognizer_loop:record_end`, `recognizer_loop:audio_output_start`, `recognizer_loop:audio_output_end`), so older subscribers keep working, but new skills subscribe to the spec names shown here. Both pairs fire regardless of which skill (if any) is involved. There is also `recognizer_loop:wakeword`, emitted the instant the wake word itself is detected, slightly before recording begins.
- `self.add_event(msg_type, handler)` subscribes for the lifetime of the skill (auto-removed on shutdown). This is the general-purpose alternative to a decorator-based intent handler, for any bus event that isn't an utterance.
- `schedule_repeating_event(handler, when, frequency, name=...)` with `when=None` starts the first run after one `frequency` interval. Pass a `datetime` for `when` instead if the first run needs to happen at a specific moment.
- This skill emits its own `ovos.ambient_mood.changed` event rather than reaching into a light/hardware plugin directly, keeping it decoupled from whatever actually consumes the mood (a PHAL plugin, another skill, a GUI). See [Bus Service](bus-service.md) for the emit/on API and [PIPELINE-1 correlation](converse-pipeline.md) for how bus events relate to a given utterance's session.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Bus Service](bus-service.md) · [Converse Pipeline](converse-pipeline.md) · [Reminder with restart persistence](recipe-reminder-persistence.md)
