# GUI + voice together: show a page while speaking, update it live

!!! abstract "In a nutshell"
    You build an `OVOSSkill` that shows a GUI page at the same moment it speaks, and keeps the page in sync afterward, using `self.gui` session data and `show_page`.

**When you'd want this:** a skill on a screen-equipped device (a Mark 2, say) should show a result, such as a weather card, a list, or a picture, at the same moment it speaks about it, and keep the screen in sync as things change (e.g. counting down a timer).

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class WeatherCardSkill(OVOSSkill):
    @intent_handler("weather.intent")
    def handle_weather(self, message):
        temperature = self._get_temperature()  # however this skill fetches it

        self.gui["temperature"] = temperature
        self.gui["condition"] = "Sunny"
        self.gui.show_page("weather.qml", override_idle=30)

        self.speak_dialog("weather", {"temp": temperature})

    def handle_temperature_update(self, message):
        # e.g. called from a scheduled event every few minutes while the
        # weather page is showing, to refresh the number without re-speaking
        self.gui["temperature"] = message.data["temperature"]
```

`gui/qt5/weather.qml` renders `temperature`/`condition` as GUI session data. See [Skill GUI](skill-gui.md) for the full page/session-data lifecycle and `gui/qt6`/other render-backend layout conventions.

### Moving parts

- `self.gui` is a `SkillGUI` instance (a subclass of `GUIInterface`), set up automatically once a skill initializes. No separate import or manual construction is needed.
- `self.gui["key"] = value` sets session data the page template reads. `self.gui.show_page(name, override_idle=...)` requests that page be displayed (`override_idle` keeps it up for N seconds even if something would otherwise return to the idle screen).
- Updating `self.gui[...]` again while the page is already showing (as in `handle_temperature_update`) pushes fresh data to an already-visible page without calling `show_page` again.
- !!! danger "This is the legacy GUI stack"
    Everything in this recipe targets the current, **deprecated** `.qml`-based GUI stack, which [Skill GUI](skill-gui.md) documents as effectively unusable outside Mark 2 maintenance today. The forward-looking replacement is the **Upcoming** [GUI rework](gui-adapters.md) (spec OVOS-GUI-1), which instead has a skill declare intent via a closed `SYSTEM_*` template vocabulary rather than shipping custom `.qml`. That page is the one to design new screen support against.

!!! tip "Full production example"
    [`ovos-skill-camera`](https://github.com/OpenVoiceOS/ovos-skill-camera) runs a near-identical sequence: `show_text` for a countdown, then `show_image` once the photo is ready. [`ovos-skill-wallpapers`](https://github.com/OpenVoiceOS/ovos-skill-wallpapers) shows the other half of the lifecycle, calling `gui.release()` to hand screen ownership back to the homescreen when the skill is done with it.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Skill GUI](skill-gui.md) · [GUI rework](gui-adapters.md) · [`ovos-skill-camera`](https://github.com/OpenVoiceOS/ovos-skill-camera)
