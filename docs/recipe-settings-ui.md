# A skill with a settings UI: declare, edit, read, react

!!! abstract "In a nutshell"
    You wire a `settingsmeta.yaml` field to a browser-based settings editor and an `OVOSSkill`'s own `settings_change_callback`, so a user can change a value with no terminal and no hand-edited JSON.

**When you'd want this:** a user should be able to change a skill's settings from a
browser, with no terminal and no hand-edited JSON, and the skill should pick up the
change immediately.

Three parts wire together: a `settingsmeta.yaml` field declaration, a settings-editing
UI that reads and writes it, and the skill's own code that reads the stored value and
reacts when it changes.

`settingsmeta.yaml`, next to the skill's `__init__.py`:

```yaml
skillMetadata:
  sections:
    - name: "Greeter"
      fields:
        - name: "volume"
          type: "number"
          label: "Reply volume (0-100)"
          value: 50
```

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class GreeterSkill(OVOSSkill):
    def initialize(self):
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()  # apply the stored (or default) value now

    def on_settings_changed(self):
        self.volume = self.settings.get("volume", 50)
        self.log.info(f"reply volume is now {self.volume}")

    @intent_handler("greet.intent")
    def handle_greet(self, message):
        self.speak_dialog("greeting", {"volume": self.volume})
```

Restart the skill (or all of OVOS) so it picks up the new `settingsmeta.yaml` field.
Then install and run the community web UI to edit the value from a browser instead of
a text editor:

```bash
pip install ovos-skill-config-tool
ovos-skill-config-tool
```

Open `http://<device-ip>:8000`, find the skill by name, and change "Reply volume".
Saving writes the new value to the skill's `settings.json`. The running skill notices
the change and calls `on_settings_changed()` without a restart.

### Moving parts

- `settingsmeta.yaml` only declares the field for a UI to render; it does not create or
  validate the key by itself. See [Skill Settings Meta](skill-settings-meta.md) for the
  full field-type table.
- `self.settings.get("volume", 50)` reads the stored value, falling back to `50` if the
  key is absent (e.g. before any UI has ever saved a value). See [Skill
  Settings](skill-settings.md#accessing-settings).
- `self.settings_change_callback`, assigned in `initialize()`, is called with no
  arguments whenever `settings.json` changes on disk (the file watcher) or a remote
  settings backend pushes an update for this skill. See [Skill Settings: Change
  Callback](skill-settings.md#change-callback).
- [`ovos-skill-config-tool`](https://github.com/OscillateLabsLLC/ovos-skill-config-tool)
  is the community web UI referenced above. It edits the same `settings.json` the skill
  itself reads; it does not talk to the skill process directly. See [Skill Settings:
  Web-Based Settings UI](skill-settings.md#web-based-settings-ui-community) for
  installation and default credentials.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Skill Settings Meta](skill-settings-meta.md) · [Skill Settings](skill-settings.md#accessing-settings) · [User-configurable behavior](recipe-reactive-settings.md)
