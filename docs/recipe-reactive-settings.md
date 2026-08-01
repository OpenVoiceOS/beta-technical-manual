# User-configurable behavior: settings + settingsmeta + live reload

!!! abstract "In a nutshell"
    You build an `OVOSSkill` that reacts immediately to a changed setting, using `settings_change_callback` alongside a `settingsmeta.yaml` field declaration.

**When you'd want this:** a skill has a behavior the user should be able to tune, such as a unit system, a greeting name, or an API key, and it should react immediately when that value changes, whether the change came from a config file edit or a remote settings backend.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class GreeterSkill(OVOSSkill):
    def initialize(self):
        self.settings_change_callback = self.on_settings_changed
        self._apply_settings()

    def _apply_settings(self):
        self.greeting_name = self.settings.get("name", "friend")
        self.use_title_case = self.settings.get("shout", False)

    def on_settings_changed(self):
        # called whenever settings.json changes on disk, or a remote
        # settings backend pushes an update for this skill
        self._apply_settings()
        self.log.info(f"settings updated, now greeting as {self.greeting_name}")

    @intent_handler("greet.intent")
    def handle_greet(self, message):
        name = self.greeting_name.upper() if self.use_title_case else self.greeting_name
        self.speak_dialog("greeting", {"name": name})
```

`settingsmeta.yaml` (the optional form shown by web/companion-app settings UIs):

```yaml
skillMetadata:
  sections:
    - name: "Greeter"
      fields:
        - name: "name"
          type: "text"
          label: "What should I call you?"
          value: "friend"
        - name: "shout"
          type: "checkbox"
          label: "SHOUT the greeting"
          value: false
```

### Moving parts

- `self.settings_change_callback` is a plain attribute you assign a callable to (there is no decorator for it). The base class checks `if self.settings_change_callback is not None` both on a local file-watcher change and on a remote `mycroft.skills.settings.changed` push, and calls it with no arguments either way. See [Skill Settings](skill-settings.md) for the two trigger paths.
- Read settings defensively with `.get(key, default)`. A fresh install has an empty `settings.json` until `settingsmeta.yaml` defaults are applied by a settings UI, or you seed `self.settings` yourself in `initialize()`.
- `settingsmeta.yaml`/`.json` is descriptive only. It drives a *UI* for editing settings, and does not itself create or validate keys. See [Skill Settings Meta](skill-settings-meta.md) for the full field-type table and where the file must live.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Skill Settings](skill-settings.md) · [Skill Settings Meta](skill-settings-meta.md) · [A skill with a settings UI](recipe-settings-ui.md)
