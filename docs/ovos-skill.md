# OVOSSkill

!!! abstract "In a nutshell"
    A "skill" is an add-on that teaches your voice assistant to do one new thing, like telling the weather or setting a timer. Every skill is built on top of a shared starter kit called `OVOSSkill`, which quietly handles the housekeeping: starting up, listening for commands, speaking replies, remembering settings, and shutting down. This page is a reference for that starter kit and its methods. New to all this? Start with [Skill Classes](skill-classes.md) or the [Glossary](glossary.md).

**Module:** `ovos_workshop.skills.ovos.OVOSSkill`

`OVOSSkill` is the base class that all OVOS skills inherit from. It handles startup, intent registration, resource loading, settings, event management, GUI, and shutdown.

!!! note "Constructor, lifecycle, and startup/shutdown sequence"
    The constructor signature, the lifecycle methods to override (`initialize()`, `stop()`,
    `shutdown()`, etc.), and the full startup/shutdown sequence are documented once, on
    [Skill Classes](skill-classes.md#ovosskill). This page covers `OVOSSkill`'s remaining
    surface: properties, speaking, user input, scheduling, `SkillApi`, and the bus events it
    handles.

## Key Properties

### Session-aware (read from current Session)

| Property | Type | Description |
|---|---|---|
| `lang` | `str` | BCP-47 language of the current request |
| `core_lang` | `str` | Default configured language |
| `secondary_langs` | `list` | Configured secondary languages |
| `native_langs` | `list` | `core_lang` + `secondary_langs` |
| `location` | `dict` | Location preferences |
| `location_pretty` | `str` | City name |
| `location_timezone` | `str` | Timezone code |
| `system_unit` | `str` | `"metric"` or `"imperial"` |
| `date_format` | `str` | `"DMY"`, `"MDY"`, or `"YMD"` |
| `time_format` | `str` | `"half"` or `"full"` |

### Infrastructure

| Property | Type | Description |
|---|---|---|
| `settings` | `JsonStorage` | Persistent skill settings |
| `bus` | `MessageBusClient` | [messagebus](bus-service.md) connection |
| `gui` | `SkillGUI` | GUI interface |
| `enclosure` | `EnclosureAPI` | Mark 1 faceplate interface (⚠️ [being removed from the base class](mark1.md) like `self.gui`, moves to `ovos-mark1-utils`, faceplate becomes a GUI plugin) |
| `file_system` | `FileSystemAccess` | Managed local file access |
| `resources` | `SkillResources` | Resource files for `self.lang` |
| `dialog_renderer` | `MustacheDialogRenderer` | Render dialog templates |
| `event_scheduler` | `EventSchedulerInterface` | Schedule future bus events |
| `intent_service` | `IntentServiceInterface` | Register/manage intents |
| `intent_layers` | `IntentLayers` | Manage intent layer sets |
| `audio_service` | `OCPInterface` | Control audio/[OCP](ocp-pipeline.md) playback |
| `translator` | `OVOSLangTranslation` | Language translation (lazy init) |
| `lang_detector` | `OVOSLangDetection` | Language detection (lazy init) |
| `is_fully_initialized` | `bool` | True after `_startup` completes |
| `reload_skill` | `bool` | Set to `False` to prevent hot-reload |

## Speaking

```python
self.speak("Hello world")
self.speak_dialog("my.dialog.file")            # uses locale/lang/dialog/my.dialog.file
self.speak_dialog("my.dialog", data={"name": "Alice"})  # Mustache templating

self.speak("Anything else?", expect_response=True)  # speak, then listen for a reply
```

Both `speak()` and `speak_dialog()` accept `expect_response=False`. Set it to `True` and OVOS
re-opens the microphone as soon as the prompt finishes speaking, so the user's next utterance is
captured without a wake word. This is the basis of a follow-up question. (To capture and *return* that
reply inside your handler, use `get_response` instead. See [Getting User Input](#getting-user-input)
below and the [Skill Cookbook](skill-cookbook.md).)

### Playing audio files

```python
self.play_audio(self.find_resource("chime.mp3", "snd"))
```

`play_audio(filename, instant=False, wait=False)` queues (or, with `instant=True`,
immediately plays) an audio file through `ovos-audio`. `filename` must be a path to a real
file on disk or a URI. `play_audio` does **not** search skill resource directories for you,
so resolve the path yourself first, typically with `self.find_resource(name, "snd")` (looking
up `<skill>/snd/<name>` or a locale-specific variant). Pass `wait=True` to block until playback
finishes or a 30-second default timeout elapses, or `wait=<seconds>` for a custom timeout.

## Getting User Input

`get_response`, `ask_yesno`, and `ask_selection` ask the user a question and capture the
reply. See [Asking the User for Responses](prompts.md) for the full reference, including
the `validator`, `on_fail`, and `num_retries` options.

## Intent Registration

```python

# Padatious (intent file)
self.register_intent_file("my.intent", self.handler)

# Adapt (vocab-based)
from ovos_workshop.intents import IntentBuilder
intent = IntentBuilder("MyIntent").require("Keyword").build()
self.register_intent(intent, self.handler)

# Vocabulary keywords
self.register_vocabulary("hello", "HelloKeyword")
self.register_entity_file("food.entity")

```

## Context Management

```python
self.set_context("MyContext", "value")
self.remove_context("MyContext")

```

## Scheduling Events

Skills can ask the [`event_scheduler`](#infrastructure) to call a handler at a future time,
once or repeatedly:

```python
import datetime

# once, 60 seconds from now
self.schedule_event(self.handle_timeout, 60, name="my-timeout")

# once, at a specific point in time
self.schedule_event(self.handle_timeout, datetime.datetime.now() + datetime.timedelta(hours=1),
                    name="my-timeout")

# repeating every 30 minutes, starting 30 minutes from now
self.schedule_repeating_event(self.handle_tick, None, 60 * 30, name="my-tick")

# cancel a scheduled event by name
self.cancel_scheduled_event("my-tick")

```

- **`schedule_event(handler, when, data=None, name=None, context=None)`**: single-shot.
  `when` is either a `datetime` (interpreted in the system timezone) or a number of seconds
  from now.
- **`schedule_repeating_event(handler, when, frequency, data=None, name=None, context=None)`**:
  repeating. `frequency` is the interval **in seconds** between calls. `when=None` fires the
  first call `frequency` seconds from now. Pass a `datetime`/number to control the first firing
  explicitly.
- Both accept an optional `name` used to reference/cancel the event later with
  `cancel_scheduled_event(name)`. Reusing a `name` for `schedule_event` does **not** warn or
  replace a previously scheduled event of the same name. Use unique names, or cancel the old
  one first.
- Scheduled events are persisted by the [`EventScheduler`](bus-service.md) so they survive an
  `ovos-core` restart. They are not tied to the skill instance staying in memory.

## Public Skill API

Decorate a method with `@skill_api_method` to expose it over the bus. Other skills or tools can call it via `SkillApi`. The full RPC mechanism — discovery, call protocol, the `SkillApi` proxy class, and a worked client/server example — is documented on [Skill API: Inter-Skill RPC](skill-api.md).

## RuntimeRequirements

!!! note
    `RuntimeRequirements` is a deprecated mechanism. See [Runtime Requirements](skill-runtime-requirements.md) for what it currently does.

Override the class property to declare connectivity needs:

```python
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements

@classproperty
def runtime_requirements(self):
    return RuntimeRequirements(
        network_before_load=False,
        internet_before_load=False,
        gui_before_load=False,
        requires_internet=False,
        requires_network=False,
        requires_gui=False,
        no_internet_fallback=False,
        no_network_fallback=False,
        no_gui_fallback=True,
    )

```

All nine fields default `True` except `gui_before_load`, `requires_gui`, and
`no_internet_fallback`/`no_network_fallback` (default `False`), and `no_gui_fallback` (default
`True`). This is used by `SkillManager` to defer loading until the required connectivity is
available.

## System Bus Events Handled (per skill)

| Event | Description |
|---|---|
| `mycroft.stop` | Global stop broadcast, cease all activity for the inbound session |
| `{skill_id}.stop` | Skill-directed stop, cease the stoppable activity for the inbound session |
| `{skill_id}.stop.ping` | Check if the skill can stop. The base class answers with `{skill_id}.stop.response` carrying whether it can handle the stop |
| `{skill_id}.converse.get_response` | Feed user response to `get_response` |
| `mycroft.skill.enable_intent` | Enable a disabled intent (the bus-facing counterpart to calling `self.enable_intent(intent_name)` from Python) |
| `mycroft.skill.disable_intent` | Disable an active intent (the bus-facing counterpart to calling `self.disable_intent(intent_name)` from Python) |
| `mycroft.skill.set_cross_context` | Set cross-skill context |
| `mycroft.skill.remove_cross_context` | Remove cross-skill context |
| `mycroft.skills.settings.changed` | Remote settings update |
| `ovos.skills.settings_changed` | Local settings file changed |
| `question:query` | Common query pipeline request |
| `ovos.common_query.ping` | Common query service discovery |
| `question:action.{skill_id}` | Common query callback (this skill's answer was selected) |
| `question:action` | Common query callback (generic, any skill's answer was selected) |
| `homescreen.metadata.get` | Homescreen requesting metadata |
| `{skill_id}.public_api` | Skill API introspection |

A skill subscribes to **both** stop topics (OVOS-STOP-1 §9): `{skill_id}.stop`, the
targeted dispatch that ceases only its own stoppable activity for the inbound session, and
`mycroft.stop`, the universal broadcast that ceases everything for that session. A duplicate
arrival on either topic while the skill is already stopping is a no-op. See the
[Stop Pipeline](stop-pipeline.md).

---
**Read next:** [Skill API: Inter-Skill RPC](skill-api.md)
**Related:** [ovos-workshop Documentation](workshop-overview.md) · [Decorators](decorators.md) · [Skill Settings](skill-settings.md) · [Session Aware Skills](session.md)
