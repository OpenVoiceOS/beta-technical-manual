# A reminder skill: scheduled events across a restart

!!! abstract "In a nutshell"
    You build a reminder skill on `OVOSSkill` where each reminder is a single
    scheduled event. The scheduler persists it on disk and replays it after a
    device restart on its own, so the skill only needs to schedule the event
    once and clean up its own bookkeeping when it fires or gets canceled.

**When you'd want this:** the user says "remind me in 10 minutes to check the
oven", and the reminder must still fire even if the device rebooted in the
meantime.

`self.schedule_event` writes the schedule to disk before returning, and the
[scheduler](scheduler-service.md) reloads every pending schedule on startup,
recomputing what is still due and firing anything it missed while it was
down. A skill does not re-arm its own timers after a restart. It only needs
to track its own reminders well enough to answer "what's still pending" and
"cancel this one" when the user asks.

```python
import datetime
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class ReminderSkill(OVOSSkill):
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

### Why the skill still keeps `pending_reminders`

The scheduler owns the timer. The skill still owns the user-facing list of
what it promised. `pending_reminders` in [settings](skill-settings.md) is
what lets `handle_cancel_reminder` speak "reminders cleared" and know which
schedule names to cancel by, and it is what a listing/status intent would
read from if this skill grew one. It is bookkeeping for the skill's own
conversation with the user, not a workaround for a scheduler that would
otherwise forget the timer.

Because the scheduler already restores the schedule itself, the skill does
not need an `initialize()` step that re-arms anything: the event fires
under its original `name` whether the process that set it is still running
or was restarted in between. If the device was off past the due time, the
scheduler's [misfire policy](scheduler-service.md#misfire-policy) fires the
most recent missed occurrence once by default, so `handle_reminder_due`
still runs and the reminder still clears itself out of `pending_reminders`.

### Moving parts

- `self.schedule_event(handler, when, data=None, name=None)`: `when` accepts a
  `datetime.datetime` (absolute) or an `int`/`float` (seconds from now). `name` is
  the handle you cancel or update by later. Full signature and semantics: [Scheduling Events](ovos-skill.md#scheduling-events).
- `self.cancel_scheduled_event(name)` / `self.update_scheduled_event(name, data)`: manage an existing timer by name.
- For a recurring alarm (not a one-shot reminder), use `self.schedule_repeating_event(handler, when, frequency, name=...)` instead. Same page.
- `self.settings` is a `JsonStorage` (dict-like) backed by `settings.json`. `self.settings.store()` writes it to disk immediately. See [Skill Settings](skill-settings.md) for the storage location and lifecycle.

!!! tip "Full production example"
    [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) implements this pattern for real alarms and timers, including recurring (weekday) alarms via `schedule_repeating_event`.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Scheduling Events](ovos-skill.md#scheduling-events) · [Scheduled Events](scheduler-service.md) · [Skill Settings](skill-settings.md) · [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts)
