# Skill Classes Reference

!!! abstract "In a nutshell"
    This page is the per-class reference for every specialized skill base class in
    `ovos-workshop` beyond the universal `OVOSSkill`: converse-aware skills, fallback
    skills, media/game skills, auto-translating skills, and standalone applications,
    plus the skill launcher and the decorator quick reference. For `OVOSSkill` itself
    and guidance on which class to pick, see [Skill Classes](skill-classes.md).

`ovos-workshop` provides all base classes needed to write skills for OpenVoiceOS. Every skill ultimately inherits from `OVOSSkill`.

**Package:** `ovos-workshop` | **Entry point group:** `opm.skill`

---

## ConversationalSkill

**Module:** `ovos_workshop.skills.converse.ConversationalSkill`

Extends `OVOSSkill` with explicit converse support: `activate()`, `deactivate()`, and `@conversational_intent` decorated handlers. The skill registers itself in the active-skills list after handling an intent.

```python
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(ConversationalSkill):
    def converse(self, message):
        utterance = message.data["utterances"][0]
        if "help" in utterance:
            self.speak("Here to help!")
            return True   # consumed
        return False      # pass to next handler

```

Additional bus events registered:

- `{skill_id}.converse.ping`: capability advertisement


- `{skill_id}.converse.request`: converse request from pipeline


- `{skill_id}.activate` / `{skill_id}.deactivate`

---

## ActiveSkill

**Module:** `ovos_workshop.skills.active.ActiveSkill`

Extends `ConversationalSkill`. Always present in the converse active-skills list. The skill never deactivates unless explicitly told to. Useful for always-on assistants or global command handlers.

```python
from ovos_workshop.skills.active import ActiveSkill

class AlwaysListeningSkill(ActiveSkill):
    def converse(self, message):
        utterance = message.data["utterances"][0]
        # handle every utterance
        return False  # let other skills also process

```

---

## FallbackSkill

**Module:** `ovos_workshop.skills.fallback.FallbackSkill`

Handles utterances that matched no intent. Must implement `can_answer()` and provide at least one `@fallback_handler`.

```python
from ovos_workshop.skills.fallback import FallbackSkill
from ovos_workshop.decorators import fallback_handler

class MyFallback(FallbackSkill):
    def can_answer(self, message: Message) -> bool:
        # utterances are read from the message internally
        return True   # always willing to try

    @fallback_handler(priority=50)
    def handle_fallback(self, message):
        self.speak("I don't know, but I tried.")
        return True   # consumed: stop checking other fallbacks

```

Priority determines which internal pipeline stage checks the fallback first (lower runs
earlier). These are the dispatch stage boundaries, verified in `FallbackService`
(`ovos_core/intent_services/fallback_service.py`). This is a separate fact from *which* priority
you should actually pick for a handler, covered in [Fallback Skill](fallbacks.md#order-of-precedence):

| Range (exclusive start, inclusive stop) | Pipeline stage |
|---|---|
| 0–5 | `fallback_high` |
| 5–90 | `fallback_medium` |
| 90–101 | `fallback_low` |

A priority of exactly `5` lands in `fallback_high`, and exactly `90` lands in `fallback_medium`,
since the stage boundary itself is included in the lower stage.

Priority can be overridden in config:

```json
{"skills": {"fallbacks": {"fallback_priorities": {"my-skill-id": 10}}}}

```

---

## CommonQuery: `@common_query` on `OVOSSkill`

There is no dedicated `CommonQuerySkill` base class. Decorate a method on a
regular `OVOSSkill` with `@common_query()` to join the `question:query` /
`ovos-common-query-pipeline-plugin` pipeline. The handler answers a natural language question and returns
a confidence score. The pipeline collects responses from all skills and speaks
the highest-confidence answer.

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import common_query

class MyQuerySkill(OVOSSkill):
    @common_query()
    def handle_query(self, phrase, lang):
        if "capital of france" in phrase.lower():
            return "Paris", 0.9   # (answer, confidence)
        return None, 0

```

!!! note "Under the hood"
    On startup `OVOSSkill` scans for a method tagged by `@common_query`
    (in `ovos_workshop/skills/ovos.py`) and wires up the CommonQuery ping/answer bus handlers
    automatically. Only one such handler per skill is supported.

---

## OVOSCommonPlaybackSkill

**Module:** `ovos_workshop.skills.common_play.OVOSCommonPlaybackSkill`

Integrates with OCP (OpenVoiceOS [Common Play](ocp-pipeline.md)) for media playback. Uses `@ocp_search`, `@ocp_play`, and related decorators to respond to play requests and appear in the OCP media browser.

```python
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_utils.ocp import MediaType, PlaybackType, MediaEntry, Playlist

class MyMusicSkill(OVOSCommonPlaybackSkill):
    @ocp_search()
    def search_music(self, phrase: str, media_type: MediaType):
        if media_type == MediaType.MUSIC:
            yield MediaEntry(
                title="My Song",
                uri="https://example.com/song.mp3",
                playback=PlaybackType.AUDIO,
                media_type=MediaType.MUSIC,
                match_confidence=80,
            )

    @ocp_featured_media()
    def featured(self) -> Playlist:
        pl = Playlist(title="My Playlist", playback=PlaybackType.AUDIO,
                      media_type=MediaType.MUSIC, match_confidence=90)
        pl.add_entry(MediaEntry(uri="https://example.com/song.mp3",
                                title="My Song",
                                playback=PlaybackType.AUDIO,
                                media_type=MediaType.MUSIC,
                                match_confidence=90))
        return pl

```

---

## OVOSGameSkill

**Module:** `ovos_workshop.skills.game_skill.OVOSGameSkill`
**Source:** `ovos_workshop/skills/game_skill.py`

Extends `OVOSCommonPlaybackSkill`. Structured base for OCP-integrated voice games. Subclasses must implement all six abstract methods: `on_play_game`, `on_pause_game`, `on_resume_game`, `on_stop_game`, `on_save_game`, `on_load_game`.

```python
from ovos_workshop.skills.game_skill import OVOSGameSkill

class TriviaGameSkill(OVOSGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="trivia_game", *args, **kwargs)

    def on_play_game(self):
        self.speak("Starting trivia!")

    def on_pause_game(self):
        self._paused.set()

    def on_resume_game(self):
        self._paused.clear()

    def on_stop_game(self):
        self.speak("Game over.")

    def on_save_game(self):
        self.speak("Save is not supported.")

    def on_load_game(self):
        self.speak("Load is not supported.")

```

---

## ConversationalGameSkill

**Module:** `ovos_workshop.skills.game_skill.ConversationalGameSkill`
**Source:** `ovos_workshop/skills/game_skill.py`

Extends `OVOSGameSkill`. Adds a **converse loop**: every utterance that does not match a registered intent is piped to `on_game_command()` while the game is playing. Also adds auto-save support, default pause/resume dialogs, and `on_abandon_game()`.

Remaining abstract methods (you must implement these): `on_play_game`, `on_stop_game`,
`on_game_command`. `on_save_game` and `on_load_game` get a default implementation that just
speaks a "can't save/load" dialog. Override them if your game supports saving. `on_pause_game`,
`on_resume_game`, and `on_abandon_game` also get working default implementations (pause/resume
dialogs gated by the `pause_dialog` setting, and a no-op abandon hook) that you can leave alone or
override.

```python
from ovos_workshop.skills.game_skill import ConversationalGameSkill

class AdventureSkill(ConversationalGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="adventure_game", *args, **kwargs)

    def on_play_game(self):
        self.speak("You enter a dark room. What do you do?")

    def on_stop_game(self):
        self.speak("Adventure ends.")

    def on_game_command(self, utterance: str, lang: str):
        if "north" in utterance:
            self.speak("You walk north.")
        else:
            self.speak("I don't understand that command.")

```

---

## UniversalSkill

**Module:** `ovos_workshop.skills.auto_translatable.UniversalSkill`
**Source:** `ovos_workshop/skills/auto_translatable.py`

Extends `OVOSSkill`. Automatically translates incoming utterances to `self.internal_language` before the intent handler runs, and translates `self.speak()` output back to the user's language. Requires a translator plugin to be configured.

```python
from ovos_workshop.skills.auto_translatable import UniversalSkill
from ovos_workshop.decorators import intent_handler

class MySkill(UniversalSkill):
    def __init__(self, *args, **kwargs):
        # All handlers receive utterances in English regardless of user's language.
        super().__init__(internal_language="en-US", *args, **kwargs)

    @intent_handler("ask_weather.intent")
    def handle_weather(self, message):
        # Utterance is already in en-US here.
        self.speak("The weather is sunny.")  # auto-translated back to user's lang

```

---

## UniversalFallback

**Module:** `ovos_workshop.skills.auto_translatable.UniversalFallback`
**Source:** `ovos_workshop/skills/auto_translatable.py`

Combines `UniversalSkill` and `FallbackSkill`. [Fallback](fallback-pipeline.md) handlers receive utterances in `self.internal_language`. `self.speak()` translates output back to the user's language.

```python
from ovos_workshop.skills.auto_translatable import UniversalFallback
from ovos_workshop.decorators import fallback_handler

class MyUniversalFallback(UniversalFallback):
    def __init__(self, *args, **kwargs):
        super().__init__(internal_language="en-US", *args, **kwargs)

    @fallback_handler(priority=75)
    def handle_unknown(self, message) -> bool:
        utterance = message.data["utterances"][0]
        self.speak(f"I heard: {utterance}")
        return True

```

---

## OVOSAbstractApplication

**Module:** `ovos_workshop.app.OVOSAbstractApplication`
**Source:** `ovos_workshop/app.py`

Like `OVOSSkill` but designed to run **without** an intent service. Suitable for standalone GUI apps, [HiveMind](hivemind-agents.md)-attached services, or any program that needs [TTS](tts-plugins.md)/messagebus/settings but does not register intents with `ovos-core`. Creates its own bus connection if none is provided. Settings stored under `apps/<id>/` instead of `skills/<id>/`.

```python
from ovos_workshop.app import OVOSAbstractApplication

class MyApp(OVOSAbstractApplication):
    def __init__(self, **kwargs):
        super().__init__(skill_id="my-app.author", **kwargs)

    def initialize(self):
        self.speak("App is ready.")

app = MyApp()  # Creates its own bus connection automatically.

```

---

## Skill Launcher

**Module:** `ovos_workshop.skill_launcher.PluginSkillLoader`

`PluginSkillLoader` is used by `SkillManager` to load plugin-based skills:

```python
from ovos_workshop.skill_launcher import PluginSkillLoader

loader = PluginSkillLoader(bus, skill_id)
loader.load(MySkillClass)   # instantiates and calls _startup

```

Skills can also be run as standalone processes:

```bash
ovos-skill-launcher my_skill_package_name

```

This is the recommended approach for running skills in Docker containers.

---

## Decorators Quick Reference

All decorators are importable from `ovos_workshop.decorators`:

| Decorator | Description |
|---|---|
| `@intent_handler("file.intent")` | Register [Padatious](padatious-pipeline.md) or [Adapt](adapt-pipeline.md) intent handler |
| `@conversational_intent("file.intent")` | Register converse-only Padatious handler |
| `@fallback_handler(priority=50)` | Register fallback handler with priority |
| `@common_query()` | Register CommonQuery handler (return answer, confidence) |
| `@converse_handler` | Alias method as the skill's `converse` handler |
| `@adds_context("Context")` | Add context entity after method runs |
| `@removes_context("Context")` | Remove context entity after method runs |
| `@skill_api_method` | Expose method over the bus for inter-skill calls |
| `@killable_intent()` | Intent that can be interrupted mid-execution |
| `@homescreen_app(icon, name)` | Register as homescreen app launcher |
| `@ocp_search()` | Search for playable content |
| `@ocp_featured_media()` | Provide featured media for OCP GUI |
| `@layer_intent(intent, layer_name)` | Intent belonging to a named layer |
| `@enables_layer("layer")` | Activate a named intent layer after method |
| `@disables_layer("layer")` | Deactivate a named intent layer after method |

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Skill Classes](skill-classes.md) · [Decorators](decorators.md)
**Related:** [OVOSSkill](ovos-skill.md) · [Fallback Skill](fallbacks.md) · [Common Query Framework](common-query.md) · [OCP Skills](ocp-skills.md)
