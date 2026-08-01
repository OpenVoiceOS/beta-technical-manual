# A reminder skill: scheduled events with restart persistence

!!! abstract "In a nutshell"
    You build a reminder skill on `OVOSSkill` that survives a device restart, by writing pending timers to `settings` and re-arming them with `schedule_event` on load.

**When you'd want this:** the user says "remind me in 10 minutes to check the oven", and the reminder must still fire even if the device rebooted in the meantime.

The scheduler (`self.schedule_event`) lives entirely in memory. If the skill process restarts, every pending timer is gone. The only thing that survives a restart is the skill's [settings](skill-settings.md) file, so a reminder skill must write down *when* each reminder is due and re-schedule anything still in the future the moment the skill reloads.

```python
import datetime
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class ReminderSkill(OVOSSkill):
    def initialize(self):
        # on every load (including after a restart), re-arm anything
        # that was still pending when we last shut down
        for name, when_iso in self.settings.get("pending_reminders", {}).items():
            when = datetime.datetime.fromisoformat(when_iso)
            if when > datetime.datetime.now():
                self.schedule_event(self.handle_reminder_due, when, name=name)
            else:
                # missed it while we were down, fire immediately
                self.schedule_event(self.handle_reminder_due, 1, name=name)

    @intent_handler("set_reminder.intent")
    def handle_set_reminder(self, message):
        minutes = message.data.get("minutes", 5)
        text = message.data.get("utterance", "your reminder")
        when = datetime.datetime.now() + datetime.timedelta(minutes=float(minutes))
        name = f"reminder_{when.timestamp():.0f}"

        self.schedule_event(self.handle_reminder_due, when,
                             data={"text": text, "name": name}, name=name)

        pending = self.settings.get("pending_reminders", {})
        pending[name] = when.isoformat()
        self.settings["pending_reminders"] = pending
        self.settings.store()

        self.speak_dialog("reminder_set", {"minutes": minutes})

    def handle_reminder_due(self, message):
        # self.play_audio(self.find_resource("chime.mp3", "snd")) would play a
        # sound file instead of/before speaking — see self.play_audio
        self.speak_dialog("reminder_due", {"text": message.data["text"]})
        pending = self.settings.get("pending_reminders", {})
        pending.pop(message.data["name"], None)
        self.settings["pending_reminders"] = pending
        self.settings.store()

    @intent_handler("cancel_reminder.intent")
    def handle_cancel_reminder(self, message):
        pending = self.settings.get("pending_reminders", {})
        # cancel every reminder we know about; a real skill would
        # let the user pick one by name/time instead
        for name in list(pending):
            self.cancel_scheduled_event(name)
            pending.pop(name)
        self.settings["pending_reminders"] = pending
        self.settings.store()
        self.speak_dialog("reminders_cleared")
```

`locale/en-us/dialog/reminder_set.dialog`:

```text
I'll remind you in {minutes} minutes
```

`locale/en-us/dialog/reminder_due.dialog`:

```text
Reminder: {text}
```

### Moving parts

- `self.schedule_event(handler, when, data=None, name=None)`: `when` accepts a
  `datetime.datetime` (absolute) or an `int`/`float` (seconds from now). `name` is
  the handle you cancel or update by later. Full signature and semantics: [Scheduling Events](ovos-skill.md#scheduling-events).
- `self.cancel_scheduled_event(name)` / `self.update_scheduled_event(name, data)`: manage an existing timer by name.
- For a recurring alarm (not a one-shot reminder), use `self.schedule_repeating_event(handler, when, frequency, name=...)` instead. Same page.
- `self.settings` is a `JsonStorage` (dict-like) backed by `settings.json`. `self.settings.store()` writes it to disk immediately. See [Skill Settings](skill-settings.md) for the storage location and lifecycle.
- The pattern of "write intended future state to settings, replay it in `initialize()`" is the standard way any OVOS skill survives a restart. There is no separate scheduler persistence API.

!!! tip "Full production example"
    [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) implements exactly this pattern for real alarms and timers, including recurring (weekday) alarms via `schedule_repeating_event`.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Scheduling Events](ovos-skill.md#scheduling-events) · [Skill Settings](skill-settings.md) · [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts)
