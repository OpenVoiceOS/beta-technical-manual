# Skill Cookbook

!!! abstract "In a nutshell"
    The rest of this manual documents individual building blocks (settings, scheduling, playback, a GUI) one at a time. This page instead shows them **combined**, the way a real skill uses them: a complete, working file for each common job a skill needs to do. If you already know what `schedule_event` or `@ocp_search` does and just want to see it used correctly next to everything else it needs, start here.

## Recipe index

| # | Recipe | Base class | Key APIs |
|---|--------|-----------|----------|
| 1 | Reminder with restart persistence | `OVOSSkill` | `schedule_event`, `settings` |
| 2 | Configurable + reactive settings | `OVOSSkill` | `settings_change_callback`, `settingsmeta.yaml` |
| 3 | Safe external API call | `OVOSSkill` | `runtime_requirements`, `file_system` |
| 4 | Multi-turn conversation | `ConversationalSkill` | `get_response`, `converse`, `activate` |
| 5 | Local media playlist | `OVOSCommonPlaybackSkill` | `@ocp_search`, `MediaType`/`PlaybackType` |
| 6 | GUI + voice together | `OVOSSkill` | `self.gui`, `show_page` |
| 7 | Fallback to an LLM solver | `FallbackSkill` | `register_fallback`, `QuestionSolver` |
| 8 | Ambient bus-event behavior | `OVOSSkill` | `add_event`, `recognizer_loop:*` |
| 9 | Converse-driven game loop | `ConversationalGameSkill` | `on_play_game`, `on_game_command`, `converse` |
| 10 | Validated slot collection | `OVOSSkill` | `get_response(validator=..., on_fail=..., num_retries=...)` |
| 11 | Control an external device (MQTT) | `OVOSSkill` | `paho.mqtt.client.Client`, `connect`, `publish`, `disconnect` |
| 12 | A skill with a settings UI | `OVOSSkill` | `settingsmeta.yaml`, `ovos-skill-config-tool`, `settings_change_callback` |

Each recipe below is a **complete skill module** (or a clearly-marked excerpt of one), followed by notes on the moving parts and links to the reference page that documents each API in full. None of these recipes invent new methods: every class, method signature, and bus event name was checked against the installed `ovos-workshop`, `ovos-bus-client`, and `ovos-utils` packages.

!!! note "Scaffolding not shown"
    To keep each recipe focused, `requirements.txt`, `manifest.yml`, `setup.py`/`pyproject.toml`, and the `__init__.py` boilerplate needed to actually publish a skill are omitted here. See [Anatomy of a Skill](skill-structure.md) for those. Intent files (`.intent`, `.voc`) referenced below live under `locale/<lang>/`.

---

## 1. A reminder skill: scheduled events with restart persistence

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

## 2. User-configurable behavior: settings + settingsmeta + live reload

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

## 3. Calling an external API safely: timeouts, spoken errors, and a cache

**When you'd want this:** a skill answers "what's the exchange rate" or similar by hitting a remote HTTP API, and needs to (a) never hang the skill process on a slow/dead endpoint, and (b) fail with a spoken sentence instead of a traceback.

!!! note
    This recipe also shows `runtime_requirements`, a deprecated, legacy declaration kept here
    for skills that already use it. See [Runtime Requirements](skill-runtime-requirements.md)
    for what it currently does. New skills don't need it for the timeout/cache/spoken-error
    pattern below, which works regardless.

```python
import json
import time

import requests
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

API_URL = "https://api.example.com/rate"
CACHE_TTL = 3600  # seconds


class ExchangeRateSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        # legacy declaration: this skill needs a live network connection.
        # only gates loading if "skills.use_deferred_loading" is enabled.
        return RuntimeRequirements(
            network_before_load=True,
            internet_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=False,
            no_network_fallback=False,
        )

    def _cache_path(self):
        return self.file_system.path + "/rate_cache.json"

    def _read_cache(self):
        try:
            with open(self._cache_path()) as f:
                data = json.load(f)
            if time.time() - data["fetched_at"] < CACHE_TTL:
                return data["rate"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
        return None

    def _write_cache(self, rate):
        with open(self._cache_path(), "w") as f:
            json.dump({"rate": rate, "fetched_at": time.time()}, f)

    def _fetch_rate(self):
        cached = self._read_cache()
        if cached is not None:
            return cached
        try:
            resp = requests.get(API_URL, timeout=5)
            resp.raise_for_status()
            rate = resp.json()["rate"]
        except requests.exceptions.Timeout:
            self.speak_dialog("api_timeout")
            return None
        except requests.exceptions.RequestException as e:
            self.log.warning(f"exchange rate API call failed: {e}")
            self.speak_dialog("api_error")
            return None
        self._write_cache(rate)
        return rate

    @intent_handler("exchange_rate.intent")
    def handle_exchange_rate(self, message):
        rate = self._fetch_rate()
        if rate is not None:
            self.speak_dialog("exchange_rate", {"rate": rate})
```

### Moving parts

- `runtime_requirements` (a `@classproperty` you override, returning `RuntimeRequirements(...)`) is a deprecated, legacy declaration. Its `*_before_load` flags only gate loading when `skills.use_deferred_loading` is enabled in config. With the default config, all skills load unconditionally regardless of this declaration. See [Runtime Requirements](skill-runtime-requirements.md) for the current behavior.
- Always pass `timeout=` to `requests.get`/`.post`. An OVOS skill runs on the shared bus-handling thread pool, and a hung HTTP call can stall other skill callbacks.
- `self.file_system` (a `FileSystemAccess`, exposing `.path`) is a writable, skill-private directory distinct from `settings.json`. It is the right place for a response cache, downloaded assets, or anything larger than a few settings keys.
- Wrap the network call narrowly (`requests.exceptions.Timeout` / `.RequestException`) so a real bug elsewhere in the handler still raises normally instead of being swallowed by a broad `except Exception`.

---

## 4. Continuous conversation: multi-turn dialog with `converse` and `get_response`

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
- [Context](context.md) (`self.set_context()`) is the lighter-weight alternative when you only need to bias which of *your own* intents can match next, rather than intercepting raw utterances.

!!! tip "Full production example"
    [`ovos-skill-parrot`](https://github.com/OpenVoiceOS/ovos-skill-parrot) is a minimal `ConversationalSkill` with an explicit `can_converse`/`converse` pair, good for seeing the bare mechanism with nothing else around it. [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) shows the same tools used for real work, combining `converse` with `get_response` to collect an alert's details across several turns.

---

## 5. A small local media playlist: an OCP skill

**When you'd want this:** "play the office playlist" should hand back a short, fixed list of local audio files without any external search or streaming service.

```python
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill

PLAYLIST = [
    {
        "title": "Morning Briefing",
        "uri": "file:///opt/office-media/morning-briefing.mp3",
        "length": 180,
    },
    {
        "title": "Lobby Loop",
        "uri": "file:///opt/office-media/lobby-loop.mp3",
        "length": 600,
    },
]


class OfficePlaylistSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, supported_media=[MediaType.MUSIC], **kwargs)
        self.skill_icon = ""  # optional path/URI to an icon shown in OCP's UI

    @ocp_search()
    def search_office_playlist(self, phrase, media_type=MediaType.GENERIC):
        # self.voc_match() lets a skill claim narrow phrases confidently;
        # everything else gets a low, generic confidence
        confident = self.voc_match(phrase, "office_playlist")
        for track in PLAYLIST:
            if confident or track["title"].lower() in phrase.lower():
                yield {
                    "title": track["title"],
                    "uri": track["uri"],
                    "media_type": MediaType.MUSIC,
                    "playback": PlaybackType.AUDIO,
                    "match_confidence": 90 if confident else 40,
                    "length": track["length"],
                }
```

`locale/en-us/vocab/office_playlist.voc`:

```text
office playlist
lobby music
```

### Moving parts

- `MediaType` and `PlaybackType` are enums imported from `ovos_utils.ocp`. Results are plain dicts, not a dedicated result class. Mandatory keys are `uri`, `title`, `media_type`, `playback`, `match_confidence` (0-100), with `artist`, `album`, `image`, `length` (seconds) optional. Full field table: [OCP Skills](ocp-skills.md).
- `@ocp_search()` (imported from `ovos_workshop.decorators.ocp`) marks a method as a search provider. OCP calls every registered provider's search method in parallel and keeps the best-confidence result across all installed OCP skills. A search method may `return` a list or `yield` results incrementally.
- `supported_media` (passed to `super().__init__()`) tells OCP which `MediaType`s this skill should even be asked about.
- `self.voc_match(phrase, "office_playlist")` reuses the same vocabulary mechanism as intents to give a confident match a high score, while still falling back to a loose substring check.
- [OCP Skills](ocp-skills.md) also documents `self.extend_timeout()` (ask OCP to wait longer for a slow search) and notes that new integrations not needing the full skill lifecycle may prefer a `MediaProvider` plugin instead. See that page's opening warning.

!!! tip "Full production example"
    [`ovos-skill-somafm`](https://github.com/OpenVoiceOS/ovos-skill-somafm) is a full modern OCP skill: `@ocp_search`, `@ocp_featured_media`, `register_ocp_keyword`, and results built as `Playlist`/`MediaEntry` objects instead of plain dicts. [`ovos-skill-news`](https://github.com/OpenVoiceOS/ovos-skill-news) applies the same pattern for `MediaType.NEWS`.

---

## 6. GUI + voice together: show a page while speaking, update it live

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

## 7. Fallback + LLM: delegating unmatched utterances to a solver plugin

**When you'd want this:** every intent-matching skill has had its turn and none of them understood the utterance. Instead of a flat "sorry, I don't understand," hand it to a language-model-backed plugin and speak whatever it comes back with.

```python
from ovos_plugin_manager.templates.solvers import QuestionSolver
from ovos_workshop.skills.fallback import FallbackSkill


class LLMFallbackSkill(FallbackSkill):
    def initialize(self):
        # a specific solver plugin id, e.g. "ovos-solver-openai-persona-plugin";
        # find_question_solver_plugins lists everything registered under opm.solver
        from ovos_plugin_manager.solvers import find_question_solver_plugins
        plugin_id = self.settings.get("solver_plugin", "ovos-solver-openai-persona-plugin")
        plugins = find_question_solver_plugins()
        if plugin_id not in plugins:
            self.log.warning(f"solver plugin '{plugin_id}' not installed, "
                              "falling back to a plain 'I don't understand'")
            self.solver = None
        else:
            self.solver: QuestionSolver = plugins[plugin_id]()

        # broad catch-all: let every more specific fallback/skill go first
        self.register_fallback(self.handle_fallback, 90)

    def handle_fallback(self, message):
        utterance = message.data["utterance"]
        if self.solver is None:
            return False
        answer = self.solver.get_spoken_answer(utterance, lang=self.lang)
        if answer:
            self.speak(answer)
            return True
        return False
```

### Moving parts

- A `FallbackSkill` subclass calls `self.register_fallback(handler, priority)` in `initialize()`. `handler` must return `True` if it produced an answer (stopping the chain) or `False` to let the next-priority fallback try. Priority `90` is deliberately high (tried late) since an LLM should be the *last* resort, not the first. See [Fallback Skill](fallbacks.md) for the recommended priority tiers.
- `QuestionSolver.get_spoken_answer(query, lang=None, units=None)` is the common template every question-answering solver plugin implements. A plugin is just a Python entry point (`opm.solver`) you load by id, the same plugin-discovery pattern used everywhere else in OVOS.
- !!! warning "Upcoming: solver templates are being replaced"
      `ovos_plugin_manager.templates.solvers` (including `QuestionSolver`, used above because it is what ships and runs today) is deprecated in favor of `ovos_plugin_manager.templates.agents.AbstractAgentEngine` and the `opm.agents.*` entry point groups. New solver plugins should target the newer API. See [Deprecated Solver Types](agent-plugins.md#deprecated-solver-types) for the full migration table and what each new agent type replaces.
- `self.speak(text)` (a raw string) is used here instead of `self.speak_dialog(...)` because the LLM's answer is not a template. It is already the exact sentence to say.

!!! tip "Full production example"
    [`ovos-skill-wolfie`](https://github.com/OpenVoiceOS/ovos-skill-wolfie), [`ovos-skill-ddg`](https://github.com/OpenVoiceOS/ovos-skill-ddg), and [`ovos-skill-wordnet`](https://github.com/OpenVoiceOS/ovos-skill-wordnet) are real `FallbackSkill` skills that pair `register_fallback` with `@common_query`, so they can answer both as a last-resort fallback and as a ranked candidate earlier in the pipeline. [`ovos-skill-fallback-unknown`](https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown) is the canonical catch-all, registered at priority 100. Priority sets the order fallbacks are tried in: a lower number runs earlier and gets first refusal, and 100 is the terminal tier, tried only after everything else has passed.

---

## 8. Ambient behavior from bus events: react to listening state and time of day

**When you'd want this:** a skill needs to do something not triggered by an utterance at all. Examples include dimming a light while the device is actively listening, or changing its greeting depending on whether it's morning or night, driven purely by bus events other services already emit.

```python
import datetime

from ovos_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill


class AmbientMoodSkill(OVOSSkill):
    def initialize(self):
        # the listener (ovos-dinkum-listener) emits these around each
        # recording, independent of any skill or intent
        self.add_event("recognizer_loop:record_begin", self.handle_listening_start)
        self.add_event("recognizer_loop:record_end", self.handle_listening_end)
        self.add_event("recognizer_loop:audio_output_start", self.handle_speaking_start)
        self.add_event("recognizer_loop:audio_output_end", self.handle_speaking_end)

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

- `recognizer_loop:record_begin` / `recognizer_loop:record_end` bracket an active recording (wake word already triggered). `recognizer_loop:audio_output_start` / `_end` bracket the device speaking. Both pairs are emitted by the listener service regardless of which skill (if any) is involved. There is also `recognizer_loop:wakeword`, emitted the instant the wake word itself is detected, slightly before recording begins.
- `self.add_event(msg_type, handler)` subscribes for the lifetime of the skill (auto-removed on shutdown). This is the general-purpose alternative to a decorator-based intent handler, for any bus event that isn't an utterance.
- `schedule_repeating_event(handler, when, frequency, name=...)` with `when=None` starts the first run after one `frequency` interval. Pass a `datetime` for `when` instead if the first run needs to happen at a specific moment.
- This skill emits its own `ovos.ambient_mood.changed` event rather than reaching into a light/hardware plugin directly, keeping it decoupled from whatever actually consumes the mood (a PHAL plugin, another skill, a GUI). See [Bus Service](bus-service.md) for the emit/on API and [PIPELINE-1 correlation](converse-pipeline.md) for how bus events relate to a given utterance's session.

---

## 9. A voice game: converse-driven game loop

**When you'd want this:** the skill runs a game entirely by voice, such as a number-guessing game or a text adventure. While the game is playing, almost anything the user says is game input, not a new command, and the skill must still respond correctly to "stop" or "pause".

`ConversationalGameSkill` (from `ovos_workshop.skills.game_skill`) is a small set of `on_*` hooks over `OVOSCommonPlaybackSkill`. The OCP media pipeline treats a game as `MediaType.GAME`: saying "play guess the number" reaches the skill through the same "play X" matching as music or a podcast, and OCP's play/pause/resume/stop transport controls double as the game's transport.

```python
import random

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills.game_skill import ConversationalGameSkill


class GuessNumberGameSkill(ConversationalGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="GuessNumberGameKeyword",
                         *args, **kwargs)
        self.secret = None
        self.guesses_left = 0

    def on_play_game(self):
        # the framework already set self.is_playing True before this runs
        self.secret = random.randint(1, 100)
        self.guesses_left = 7
        self.speak_dialog("game_start", {"tries": self.guesses_left})

    def on_stop_game(self):
        self.speak_dialog("game_stop")

    def on_abandon_game(self):
        # called before on_stop_game if the user goes quiet mid-game
        self.speak_dialog("game_abandoned")

    def on_game_command(self, utterance: str, lang: str):
        # every utterance that isn't claimed by an intent below lands here
        try:
            guess = int(utterance)
        except ValueError:
            self.speak_dialog("not_a_number", expect_response=True)
            return

        self.guesses_left -= 1
        if guess == self.secret:
            self.speak_dialog("guess_correct")
            self.stop_game()
        elif self.guesses_left <= 0:
            self.speak_dialog("guess_out_of_tries", {"answer": self.secret})
            self.stop_game()
        elif guess < self.secret:
            self.speak_dialog("guess_higher", {"tries": self.guesses_left},
                             expect_response=True)
        else:
            self.speak_dialog("guess_lower", {"tries": self.guesses_left},
                             expect_response=True)

    @intent_handler("cheat_hint.intent")
    def handle_cheat_hint(self, message):
        # this is the ONLY declared intent in the whole skill; every other
        # utterance while playing falls through to on_game_command above,
        # keeping the game's own vocabulary out of the intent parser entirely
        if self.is_playing:
            self.speak_dialog("hint_refused")
```

### Moving parts

- `ConversationalGameSkill` subclasses `OVOSGameSkill`, which subclasses `OVOSCommonPlaybackSkill`. The constructor requires `skill_voc_filename`, a `.voc` file (`locale/en-us/vocab/GuessNumberGameKeyword.voc`) listing the game's name, so OCP's search step recognizes "play guess the number" as this skill and not a music query.
- `on_play_game()`, `on_stop_game()`, `on_save_game()`, `on_load_game()` are the abstract hooks every game must implement (the last two default to speaking a "can't save" dialog if left alone). OCP calls `on_play_game()` after already marking the skill as playing (`self.is_playing` is `True` inside it). `on_pause_game()`/`on_resume_game()` also come from the base class with a working default (an acknowledgement sound, plus an optional dialog gated by the `pause_dialog` setting); override them only if pausing needs game-specific behavior.
- `on_game_command(utterance, lang)` is where free-form game input arrives. The base class's `converse()` calls it whenever the skill is playing (and not paused) *and* the utterance would not otherwise trigger one of this skill's own `@intent_handler`s (checked via `skill_will_trigger`). That is what "keeping intents inert during play" means in practice: declare as few `@intent_handler`s as the game truly needs (`cheat_hint.intent` above), and everything else, digits, "up", "north", whatever the game vocabulary is, reaches `on_game_command` instead of missing every intent and falling through to a fallback skill.
- `self.stop_game()` is the base class helper a skill calls to end the game itself (a correct guess, running out of tries). It clears playback state and then calls `on_stop_game()` for you; don't call `on_stop_game()` directly.
- Abort/inactivity is handled above the skill entirely: if the user goes quiet for a while, the intent service deactivates the skill, which calls `on_abandon_game()` and then `stop_game()` (which in turn calls `on_stop_game()`). Explicit "stop" while playing goes through the normal OCP stop transport, which calls `stop_game()` the same way.
- Set `self.settings["auto_save"] = True` and implement `on_save_game()` for autosave-before-stop behavior; `ConversationalGameSkill` calls it for you on every `converse()` turn and on `stop()` when both the setting and the override are present (checked via `save_is_implemented`).

!!! tip "Full production example"
    [`skill-moon-game`](https://github.com/JarbasSkills/skill-moon-game) is a full `ConversationalGameSkill`: a branching narrative driven entirely through `on_game_command`, with `IntentLayers` gating which branch-specific phrases are even considered at each story beat. `FrotzSkill` (from the [`pyfrotz`](https://github.com/JarbasAl/pyfrotz) package) shows the same hooks wrapping something entirely different: every utterance in `on_game_command` is piped as a raw command to an external Z-machine interpreter process, and its text output is what gets spoken.

---

## 10. Collecting structured input: `get_response` with a validator

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

## 11. Control an external device: publish to an MQTT broker

**When you'd want this:** a device on the network, such as a smart plug or a relay board, listens for commands on an MQTT topic. The skill publishes to that topic on a voice command. It uses the same timeout-plus-spoken-error pattern as Recipe 3, applied to a broker connection instead of an HTTP call.

```python
import paho.mqtt.client as mqtt
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

BROKER_HOST = "192.168.1.50"
BROKER_PORT = 1883
TOPIC = "home/office/plug1/set"
CONNECT_TIMEOUT = 5


class MqttPlugSkill(OVOSSkill):
    def initialize(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id="ovos-mqtt-plug-skill")
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=CONNECT_TIMEOUT)
            self.client.loop_start()
        except (OSError, TimeoutError) as e:
            self.log.warning(f"MQTT broker unreachable at init: {e}")

    @intent_handler("turn_on_plug.intent")
    def handle_turn_on(self, message):
        self._publish("ON", "plug_turned_on", "plug_unreachable")

    @intent_handler("turn_off_plug.intent")
    def handle_turn_off(self, message):
        self._publish("OFF", "plug_turned_off", "plug_unreachable")

    def _publish(self, payload, ok_dialog, fail_dialog):
        try:
            info = self.client.publish(TOPIC, payload, qos=1)
            info.wait_for_publish(timeout=CONNECT_TIMEOUT)
            if not info.is_published():
                raise TimeoutError("publish did not confirm in time")
        except (OSError, TimeoutError, ValueError, RuntimeError) as e:
            self.log.warning(f"MQTT publish failed: {e}")
            self.speak_dialog(fail_dialog)
            return
        self.speak_dialog(ok_dialog)

    def shutdown(self):
        self.client.loop_stop()
        self.client.disconnect()
```

### Moving parts

- `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=...)` is the current, non-deprecated way to construct a client; `client_id` should be unique per device to avoid the broker dropping a duplicate session.
- `connect(host, port, keepalive=...)` is a blocking call, so wrap it (and any use of the client) in a `try`/`except` for `OSError`/`TimeoutError` and speak a dialog instead of letting the exception surface, the same safety pattern as [Recipe 3](#3-calling-an-external-api-safely-timeouts-spoken-errors-and-a-cache).
- `loop_start()` runs the client's network loop on a background thread so `publish()` calls don't block waiting on broker I/O. Call `loop_stop()` in `shutdown()` to clean it up.
- `publish(topic, payload, qos=...)` returns an `MQTTMessageInfo`. `wait_for_publish(timeout=...)` blocks until the broker acknowledges it, or the timeout elapses. `is_published()` confirms it went through, so a network drop mid-call is caught instead of silently swallowed.
- `disconnect()` closes the connection cleanly. Pair it with `loop_stop()` in `shutdown()` so the skill doesn't leave a background thread or an open socket behind when unloaded.
- If the hardware is attached to the OVOS device itself, a [PHAL plugin](phal.md) is the intended home for device control; a skill and broker like this one suits a device reachable over the network instead.

---

## 12. A skill with a settings UI: declare, edit, read, react

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

## Learn from the official skills

Every pattern in this cookbook also runs in a real, installable skill. Read the source when you need to see a full manifest, locale files, and edge cases this cookbook leaves out.

| Pattern | Official skill |
|---|---|
| `ConversationalSkill` + scheduling + settings persistence | [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| Full OCP (`@ocp_search`, `@ocp_featured_media`, `Playlist`/`MediaEntry`) | [`ovos-skill-somafm`](https://github.com/OpenVoiceOS/ovos-skill-somafm) |
| `FallbackSkill` + `@common_query` | [`ovos-skill-wolfie`](https://github.com/OpenVoiceOS/ovos-skill-wolfie), [`ovos-skill-ddg`](https://github.com/OpenVoiceOS/ovos-skill-ddg), [`ovos-skill-wordnet`](https://github.com/OpenVoiceOS/ovos-skill-wordnet) |
| `@common_query` on a plain `OVOSSkill` | [`ovos-skill-wikipedia`](https://github.com/OpenVoiceOS/ovos-skill-wikipedia) |
| Minimal `converse` | [`ovos-skill-parrot`](https://github.com/OpenVoiceOS/ovos-skill-parrot) |
| Converse-driven game (`ConversationalGameSkill`) | [`skill-moon-game`](https://github.com/JarbasSkills/skill-moon-game) |
| GUI sequencing (`show_text` then `show_image`) | [`ovos-skill-camera`](https://github.com/OpenVoiceOS/ovos-skill-camera) |
| GUI ownership handoff (`gui.release()`) | [`ovos-skill-wallpapers`](https://github.com/OpenVoiceOS/ovos-skill-wallpapers) |
| Validated `get_response` slot collection | [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl) |
| Terminal fallback (priority 100) | [`ovos-skill-fallback-unknown`](https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown) |
| Locale-correct number/date speech | [`ovos-skill-count`](https://github.com/OpenVoiceOS/ovos-skill-count), [`ovos-skill-date-time`](https://github.com/OpenVoiceOS/ovos-skill-date-time) |
| Simplest complete skill | [`ovos-skill-hello-world`](https://github.com/OpenVoiceOS/ovos-skill-hello-world) |

---
**Read next:** [Skill Structure](skill-structure.md) · [Intent Design](intents.md)
**Related:** [Your First Skill](first-skill.md) · [Skill Design Best Practices](skill-best-practices.md) · [OCP Skills](ocp-skills.md) · [Common Query Framework](common-query.md)

