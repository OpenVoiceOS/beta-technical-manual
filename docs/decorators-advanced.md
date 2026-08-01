# Advanced Decorators

!!! abstract "In a nutshell"
    Beyond the everyday intent and context decorators, three advanced families cover interruption handling, modal intent groups, and media playback. This page gathers the killable/abortable decorators, the intent layer decorators, and the OCP decorators. Looking for the everyday ones? See [Decorators](decorators.md).

---

## Killable / Abortable Decorators

### Exception Classes

`AbortEvent`: `ovos_workshop/decorators/killable.py`
`AbortIntent`: `ovos_workshop/decorators/killable.py`
`AbortQuestion`: `ovos_workshop/decorators/killable.py`

```python
class AbortEvent(StopIteration):
    """Base class — abort any bus event handler."""

class AbortIntent(AbortEvent):
    """Abort intent parsing; raised by @killable_intent."""

class AbortQuestion(AbortEvent):
    """Gracefully abort get_response queries."""

```

These exceptions are **raised inside the handler thread** when the kill message is received. They propagate through the call stack. Wrap long-running loops to catch and clean up:

```python
from ovos_workshop.decorators.killable import killable_intent, AbortIntent

@killable_intent()
def handle_long_task(self, message):
    for step in range(1000):
        try:
            self.speak(f"Step {step}")
        except AbortIntent:
            self.speak("Task was cancelled.")
            return

```

---

### `@killable_intent`

`killable_intent`: `ovos_workshop/decorators/killable.py`

Mark an intent handler that can be interrupted mid-execution. Spawns the handler in a daemon thread. When the kill message arrives:

1. Optionally emits `mycroft.audio.speech.stop` (if `stop_tts=True`).


2. Optionally calls `skill.stop()` (if `call_stop=True`).


3. Raises `AbortIntent` in the handler thread.


4. Calls `callback` if one was provided.

```python
from ovos_workshop.decorators import killable_intent

@killable_intent(
    msg="mycroft.skills.abort_execution",  # bus message that triggers abort
    callback=None,                          # optional cleanup callable
    react_to_stop=True,                     # also react to stop messages
    call_stop=True,                         # call skill.stop() on abort
    stop_tts=True,                          # stop TTS playback on abort
)
def handle_long_task(self, message):
    import time
    for i in range(60):
        self.speak(f"Counting {i}")
        time.sleep(1)

```

Default parameters:

| Parameter | Default |
|---|---|
| `msg` | `"mycroft.skills.abort_execution"` |
| `callback` | `None` |
| `react_to_stop` | `True` |
| `call_stop` | `True` |
| `stop_tts` | `True` |

**Abort flow:**

```text
Bus receives "mycroft.skills.abort_execution"
  └─► abort() called in main thread
      ├─► emit "mycroft.audio.speech.stop"  (if stop_tts=True)
      ├─► skill.stop()                       (if call_stop=True)
      ├─► t.raise_exc(AbortIntent)           ← raised inside handler thread
      └─► callback()                         (if provided)

```

---

### `@killable_event`

`killable_event`: `ovos_workshop/decorators/killable.py`

Like `@killable_intent` but for any bus event handler. Does **not** react to stop messages or call `skill.stop()` by default.

```python
from ovos_workshop.decorators.killable import killable_event, AbortEvent

@killable_event(
    msg="my.abort.signal",
    exc=AbortEvent,          # exception to raise (default AbortEvent)
    callback=None,
    react_to_stop=False,     # default False for events
    call_stop=False,         # default False for events
    stop_tts=False,
    check_skill_id=False,    # require skill_id match in message.data
)
def handle_background_task(self, message):
    # long-running work here
    pass

```

The `check_skill_id=True` option prevents accidental termination when another skill's abort message is received.

---

## Intent Layer Decorators

Intent layers let you enable or disable groups of intents at runtime, implementing modal/state-based flows.

### `@layer_intent`

`layer_intent`: `ovos_workshop/decorators/layers.py`

Register an intent handler that belongs to a named layer. The intent is disabled until the layer is activated.

```python
from ovos_workshop.decorators.layers import layer_intent
from ovos_workshop.intents import IntentBuilder

@layer_intent(IntentBuilder("MoveIntent").require("Move"), layer_name="game_active")
def handle_move(self, message): ...

```

---

### `@enables_layer` / `@disables_layer`

`enables_layer`: `ovos_workshop/decorators/layers.py`
`disables_layer`: `ovos_workshop/decorators/layers.py`

Activate or deactivate a named intent layer **after** the decorated method runs.

```python
from ovos_workshop.decorators.layers import enables_layer, disables_layer

@enables_layer("game_active")
def start_game(self, message):
    self.speak("Game started!")

@disables_layer("game_active")
def stop_game_intent(self, message):
    self.speak("Game stopped!")

```

---

### `@replaces_layer`

`replaces_layer`: `ovos_workshop/decorators/layers.py`

Replace the intent list of a named layer after the method runs.

```python
from ovos_workshop.decorators.layers import replaces_layer

@replaces_layer("my_layer", intent_list=["NewIntent1", "NewIntent2"])
def transition(self, message): ...

```

---

### `@removes_layer`

`removes_layer`: `ovos_workshop/decorators/layers.py`

Remove a named layer entirely (and disable its intents) after the method runs.

```python
from ovos_workshop.decorators.layers import removes_layer

@removes_layer("temporary_layer")
def finish_flow(self, message): ...

```

---

### `@resets_layers`

`resets_layers`: `ovos_workshop/decorators/layers.py`

Disable **all** intent layers after the method runs.

```python
from ovos_workshop.decorators.layers import resets_layers

@resets_layers()
def reset_everything(self, message):
    self.speak("All modes cleared.")

```

---

## OCP Decorators

!!! warning "Media search is moving out of skills"
    The **media search/provider** role (a skill implementing `@ocp_search` to
    return media results) is being deprecated. A new class of **media-search
    plugins**, consumed directly by the [OCP pipeline plugin](ocp-pipeline.md), is
    replacing it (PRs in progress). Other OCP skill uses are **not** going away.
    Voice games (`OVOSGameSkill`), ebook readers, and playback handlers remain
    supported. The decorators below still work today. New media-search
    integrations should target the upcoming media-search plugin type rather than an
    `@ocp_search` skill.

OCP (OpenVoiceOS [Common Play](ocp-pipeline.md)) decorators are used with `OVOSCommonPlaybackSkill` and `OVOSGameSkill`.

**Source:** `ovos_workshop/decorators/ocp.py`

| Decorator | Attribute set | Description | Source line |
|---|---|---|---|
| `@ocp_search()` | `is_ocp_search_handler` | Search for playable content; yield/return `MediaEntry` results. | `ocp.py` |
| `@ocp_play()` | `is_ocp_playback_handler` | Handle a play request (start playback). | `ocp.py` |
| `@ocp_pause()` | `is_ocp_pause_handler` | Handle a pause request. | `ocp.py` |
| `@ocp_resume()` | `is_ocp_resume_handler` | Handle a resume request. | `ocp.py` |
| `@ocp_next()` | `is_ocp_next_handler` | Handle skip-forward. | `ocp.py` |
| `@ocp_previous()` | `is_ocp_prev_handler` | Handle skip-backward. | `ocp.py` |
| `@ocp_featured_media()` | `is_ocp_featured_handler` | Provide featured/recommended media for the OCP GUI. | `ocp.py` |

```python
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_utils.ocp import MediaType, PlaybackType, MediaEntry, Playlist


class MyMusicSkill(OVOSCommonPlaybackSkill):

    @ocp_search()
    def search_music(self, phrase: str, media_type: MediaType):
        if media_type == MediaType.MUSIC:
            yield MediaEntry(
                uri="https://example.com/song.mp3",
                title="My Song",
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

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Skill Settings](skill-settings.md)
**Related:** [Decorators](decorators.md) · [Skill Classes](skill-classes.md) · [OCP Pipeline](ocp-pipeline.md) · [Intent Layers](layers.md)
