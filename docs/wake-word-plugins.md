# Wake Word Plugins

!!! abstract "In a nutshell"
    A *wake word* is the special phrase that gets your assistant's attention, like "Hey Mycroft". It only starts paying attention when you mean to talk to it, instead of listening all the time. Wake word plugins are the different tools that listen for that phrase. Some are more accurate for a fixed phrase. Others let you pick your own wake word with less setup. See the [Glossary](glossary.md) and the [listener service](speech-service.md) for related details.

Wake Word plugins let Open Voice OS detect specific words or sounds, typically the assistant's name (for example "Hey Mycroft"). You can customize them for other use cases. These plugins let the system listen for and react to activation commands or phrases.

!!! note "Audio format contract"
    Wake-word plugins receive raw PCM from the [microphone plugin](mic-plugins.md#the-microphone-interface): **16 kHz sample rate, 16-bit samples, mono, little-endian**, delivered in **4096-byte chunks** by default.

## Change your wake word

1. Open `~/.config/mycroft/mycroft.conf` (create it if it doesn't exist).
2. Add or edit the `listener.wake_word` key and a matching entry under `hotwords`:
   ```json
   {
     "listener": { "wake_word": "hey_computer" },
     "hotwords": {
       "hey_computer": { "module": "ovos-ww-plugin-vosk", "listen": true }
     }
   }
   ```
3. Save the file. It is JSON (comments are allowed, `mycroft.conf` is parsed as JSONC).
4. Restart OVOS for the change to take effect:

--8<-- "snippets/restart-ovos.md"

5. Say the new phrase. The assistant now wakes on it instead of "hey mycroft".

## Available Plugins

OVOS supports different wake word detection plugins, each with its own strengths and use cases.
The full roster with descriptions and licenses lives in one place: the
[WW Plugins Reference](#ww-plugins-reference) table below. The default OVOS plugin for
`hey_mycroft` is `ovos-ww-plugin-precise-onnx`. Its fallback chain goes to
`ovos-ww-plugin-precise-lite` (TFLite), then `ovos-ww-plugin-precise` (classic Precise), then
`ovos-ww-plugin-vosk`, then `ovos-ww-plugin-pocketsphinx` if a plugin further up the chain is
not installed. Vosk offers the fastest setup for an arbitrary wake phrase without model training.

The default `hey_mycroft` engine `ovos-ww-plugin-precise-onnx` is rated **Beta**. Its
fallback `ovos-ww-plugin-vosk` is Stable, and `ovos-ww-plugin-precise-lite` is Deprecated.
The default is chosen for accuracy. Per the [Maturity Scale](maturity.md), maturity is
separate from the recommendation.

!!! note "Relative footprint"
    The default `ovos-ww-plugin-precise-onnx` models are small, purpose-built for a single
    wake phrase, and meant to run continuously on-device. They are much lighter than a general
    STT or TTS model. This is why wake-word detection is the one always-on inference step in
    the listener pipeline.

> Specification: wake-word detection is one of the deployer-defined capture mechanisms that trigger the audio-input service (referenced in [OVOS-AUDIO-IN-1 §5.1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) as the source of a `request_lang` hint).

!!! tip "Alternative: openWakeWord"
    `ovos-ww-plugin-openWakeWord` runs open, pre-trained neural wake-word models and is a
    strong alternative when you want better accuracy than Vosk without training your own
    Precise model.

## Wake Word Configuration

!!! tip "Too many false alarms, or not hearing you at all?"
    - **It wakes up on its own too often (false alarms)?** Raise `trigger_level`. This gives
      fewer false positives, but needs a longer, more sustained match. Or lower `sensitivity`.
    - **It doesn't hear you when you say the wake word?** Raise `sensitivity`, so each chunk of
      audio is easier to trigger. Or lower `trigger_level`.

    Both live under `hotwords.<name>` in `mycroft.conf`, next to each other. Nudge one at a
    time and test before changing the other. The full technical breakdown of what each number
    actually does is below.

The `hotwords` section in your `mycroft.conf` allows you to configure the wake word detection parameters for each plugin. For instance:

```jsonc
"hotwords": {
  "hey_mycroft": {
    "module": "ovos-ww-plugin-precise-onnx",
    "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.onnx",
    "trigger_level": 3,
    "sensitivity": 0.5,
    "listen": true
  }
}

```

> See the full docs for the [listener service](speech-service.md)

### Hotword types and per-hotword keys

Each entry under `hotwords` is one of four types, set by a boolean key. `active: null` (the
default) auto-enables the main wake word (`listener.wake_word`) and the stand-up word
(`listener.stand_up_word`); every other hotword stays disabled until you set `active: true`.

| Type | Config key | Effect when detected |
|---|---|---|
| Listen word | `listen: true`, or matches `listener.wake_word` | Starts the VAD/STT recording pipeline |
| Wakeup word | `wakeup: true`, or matches `listener.stand_up_word` | Exits sleep mode |
| Stop word | `stopword: true` | Ends free `RECORDING` mode |
| Plain hotword | none of the above, `active: true` | Plays a sound and/or emits a bus event, without starting STT |

Beyond `module`, `active`, `listen`, `wakeup`, `stopword`, and `sensitivity`/`trigger_level`,
each hotword accepts:

| Key | Type | Description |
|---|---|---|
| `sound` | `str` \| `list` | Sound file played on detection. |
| `bus_event` | `str` | Bus message type emitted on detection. |
| `utterance` | `str` | Hard-coded utterance text, bypassing STT entirely for this hotword. |
| `stt_lang` | `str` | Overrides the STT language for the command that follows this hotword. |

```jsonc
"hotwords": {
  "hey_mycroft": {
    "module": "ovos-ww-plugin-precise-lite",
    "listen": true,
    "sound": "snd/start_listening.wav",
    "active": null
  },
  "wake_up": {
    "module": "ovos-ww-plugin-vosk",
    "wakeup": true,
    "active": null
  },
  "stop_recording": {
    "module": "ovos-ww-plugin-vosk",
    "stopword": true,
    "active": true
  },
  "hey_computer": {
    "module": "ovos-ww-plugin-precise-lite",
    "bus_event": "my.custom.event",
    "sound": "snd/ding.wav",
    "active": true
  },
  "hola_mycroft": {
    "module": "ovos-ww-plugin-precise-lite",
    "listen": true,
    "stt_lang": "es-es",
    "active": true
  }
}
```

### Wake word verifiers

After a wake word engine fires, optional *verifier* plugins can inspect the raw wake-word
audio and suppress false detections before any callback runs. Verifiers implement the
`HotWordVerifier` interface (from `ovos-plugin-manager`) and are configured under
`listener.ww_verifiers`:

```jsonc
"listener": {
  "ww_verifiers": {
    "ovos-ww-verifier-silero": {"threshold": 0.1}
  }
}
```

Verifiers fail open: if a verifier plugin raises an unexpected exception, the exception is
logged and the detection is **not** suppressed. Only an explicit `False` return from
`HotWordVerifier.verify()` discards the wake. Disable a verifier without removing it from
config with `"enabled": false`.

!!! warning "Double VAD with `ovos-ww-verifier-silero`"
    Enabling `ovos-ww-verifier-silero` together with `"vad_pre_wake_enabled": true` applies
    Silero VAD twice on the same audio. Use one or the other.

## Tips and Caveats

- **Vosk Plugin**: The Vosk plugin is useful when you need a simple setup that doesn't require training a wake word model. It's great for quickly gathering data during the development stage.


- **Precision and Sensitivity**: Adjust the `sensitivity` and `trigger_level` settings carefully. Too high a sensitivity can lead to false positives, while too low may miss detection.

### `sensitivity` vs `trigger_level`: the technical breakdown

These two settings work together in the model-based Precise plugins (`ovos-ww-plugin-precise-lite`, `ovos-ww-plugin-precise-onnx`):

- **`sensitivity`** (float, 0.0-1.0, default `0.5`) sets how close a single audio chunk's model output has to be to "yes" before it counts as a match. A chunk counts as activated when its probability exceeds `1.0 - sensitivity`. Raising `sensitivity` makes each individual chunk easier to trigger: more false positives, more sensitive to the word.
- **`trigger_level`** (int, default `3`) is a debounce counter. It is the number of consecutive activated chunks required before the wake word actually fires, so a single lucky chunk isn't enough. Raising `trigger_level` requires a longer sustained match: fewer false positives, but slower and stricter detection.

In short, `sensitivity` controls how easily *one* chunk counts as a hit. `trigger_level` controls how many hits in a row are needed to confirm the wake word.

## Plugin Development

All wake word plugins inherit from the `HotWordEngine` base class provided by
`ovos-plugin-manager`.

### The HotWordEngine Interface

This is the actual base class shipped in `ovos_plugin_manager.templates.hotwords`:

```python
class HotWordEngine:
    def __init__(self, key_phrase: str, config: Optional[Dict[str, Any]] = None):
        self.key_phrase = str(key_phrase).lower()
        self.config = config or Configuration().get("hotwords", {}).get(self.key_phrase, {})

    @abc.abstractmethod
    def found_wake_word(self) -> bool:
        """Check if wake word has been found, and reset internal tracking state."""
        raise NotImplementedError()

    def reset(self):
        """Reset the WW engine to prepare for a new detection (optional)."""

    @abc.abstractmethod
    def update(self, chunk: bytes):
        """Update the hotword engine with new audio data."""
        raise NotImplementedError()

    def stop(self):
        """Perform any actions needed to shut down the wake word engine (optional)."""

```

`self.config` is the plugin's own sub-dict from `hotwords.<name>` in `mycroft.conf`,
already resolved by the base `__init__` when a subclass doesn't pass its own `config`.

### Key Methods

- **`found_wake_word()`**: Required (abstract). Returns whether the wake word has been
  detected, and resets any internal tracking of the wake word state. It takes no audio
  argument: real-time audio only reaches the plugin through `update(chunk)`, on the
  current `dev` contract.
- **`update(chunk)`**: Required (abstract). Processes one raw PCM audio chunk (see the
  audio format contract near the top of this page) and updates the engine's internal
  trigger state.
  Runs once per captured chunk on the mic thread, so it must stay well under the
  per-chunk time budget: do heavy inference work on a background thread and only feed
  results into `update`, the same real-time cadence constraint a
  [streaming STT plugin's `stream_data()`](stt-plugins.md#chunk-semantics) runs under.
- **`reset()`**: Optional. Resets internal state to prepare for a new detection. The base
  implementation is a no-op.
- **`stop()`**: Optional. Shuts down the plugin: unloading data, halting external
  processes. The base implementation is a no-op, so an override does not need to call
  `super().stop()`.

### 1. A minimal working plugin

Project layout:

```
ovos-ww-plugin-mymodel/
├── pyproject.toml
└── ovos_ww_plugin_mymodel/
    └── __init__.py
```

`ovos_ww_plugin_mymodel/__init__.py`:

```python
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from threading import Event


class MyWWPlugin(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None):
        super().__init__(key_phrase, config)
        # self.config is the plugin's own sub-dict from `hotwords.<name>` in
        # mycroft.conf — read your plugin-specific settings out of it here
        threshold = self.config.get("sensitivity", 0.5)
        self.detection = Event()
        self.engine = MyWW(key_phrase, threshold=threshold)

    def found_wake_word(self):
        # inference happens via the self.update method
        detected = self.detection.is_set()
        if detected:
            self.detection.clear()
        return detected

    def update(self, chunk):
        if self.engine.found_it(chunk):
            self.detection.set()

    def stop(self):
        self.engine.bye()


# sample valid configuration
MyWWConfig = {
    "hey mycroft": [{"module": "ovos-ww-plugin-mymodel",
                      "sensitivity": 0.5,
                      "display_name": "MyWW",
                      "priority": 70}]
}

```

### 2. Registration

`pyproject.toml`. The entry-point name (left of `=`) is the string users put in the
`hotwords.<name>.module` key of `mycroft.conf`:

```toml
[project]
name = "ovos-ww-plugin-mymodel"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.wake_word"]
ovos-ww-plugin-mymodel = "ovos_ww_plugin_mymodel:MyWWPlugin"

[project.entry-points."opm.wake_word.config"]
ovos-ww-plugin-mymodel = "ovos_ww_plugin_mymodel:MyWWConfig"

```

> **Backward Compatibility**: `ovos-plugin-manager` still supports legacy
> `mycroft.plugin.wake_word` entry points, but new plugins should use the `opm.*`
> namespace.

### 3. Test it without OVOS

`HotWordEngine` is a plain class with no messagebus connection, so a unit test needs no
running OVOS stack:

```python
from ovos_ww_plugin_mymodel import MyWWPlugin

ww = MyWWPlugin(key_phrase="hey mycroft", config={"sensitivity": 0.5})
silence_chunk = b"\x00" * 4096
ww.update(silence_chunk)
assert ww.found_wake_word() is False
```

### 4. Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.wakewords import find_wake_word_plugins

print(find_wake_word_plugins())
# {'ovos-ww-plugin-mymodel': <class '...MyWWPlugin'>}
```

`load_wake_word_plugin(name)` returns the same uninstantiated class for one plugin name.
You construct it yourself with a `key_phrase` and config dict.

### 5. Checklist before you publish

1. The class subclasses `HotWordEngine` and implements `found_wake_word() -> bool` and
   `update(chunk)`.
2. `__init__` accepts `key_phrase` and `config=None`, and calls
   `super().__init__(key_phrase, config)` (or otherwise sets `self.key_phrase` and
   `self.config`).
3. `found_wake_word()` takes no arguments and resets its own detection state before
   returning.
4. `update(chunk)` returns promptly; slow inference runs on a background thread.
5. The entry-point group in `pyproject.toml` is `opm.wake_word`, with a matching
   `opm.wake_word.config` entry once the plugin has settings worth advertising in UIs.
6. Unit tests exercise `update`/`found_wake_word` directly, with no OVOS services
   running.
7. `find_wake_word_plugins()` discovers the installed plugin under the expected name.

## WW Plugins Reference

Code license is the SPDX license of the plugin's own repository. Where the plugin wraps a
separately-licensed model, that is called out under "model".

| Plugin | Description | License | Maturity |
|--------|-------------|---------|----------|
| [ovos-ww-plugin-precise-lite](#ovos-ww-plugin-precise-lite) | First fallback below the default: a trained Precise wake-word model exported to TFLite. Warning: archived, kept working as installed. `ovos-ww-plugin-precise-onnx` is the maintained successor. | Apache-2.0 | Deprecated |
| [ovos-ww-plugin-openWakeWord](#ovos-ww-plugin-openwakeword) | Wake-word detection using the open-source openWakeWord neural models. | Apache-2.0 (model: see model card) | Stable |
| [ovos-ww-plugin-vosk](#ovos-ww-plugin-vosk) | Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/) | Apache-2.0 (model: see model card) | Stable |
| [ovos-ww-plugin-precise-onnx](#ovos-ww-plugin-precise-onnx) | Default plugin for `hey_mycroft`: a Precise wake-word model exported to ONNX. | Apache-2.0 | Beta |
| [ovos-ww-plugin-wakewordlab](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakewordlab) | Compact (~240 KB) neural wake-word models with a Silero VAD pre-filter (`.wkw`/`.onnx`). **Not yet on PyPI**, install from source. | Apache-2.0 | Alpha |
| [ovos-ww-plugin-wakeforge](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakeforge) | Runs custom wake-word models trained with [wakeforge](https://github.com/TigreGotico/wakeforge): train a detector from a single phrase, export a two-file model. **Not yet on PyPI**, install from source. | Apache-2.0 | Alpha |
| [ovos-ww-plugin-server](https://github.com/OpenVoiceOS/ovos-ww-plugin-server) | Remote wake-word detection: streams audio to an [ovos-ww-server](https://github.com/OpenVoiceOS/ovos-ww-server) instance (offload detection from a thin satellite). **Not yet on PyPI**, install from source. | Apache-2.0 | Alpha |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).

## ovos-ww-plugin-precise-lite

- **GitHub**: [OpenVoiceOS/ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite). Warning: archived.


- **Description**: Trained Precise wake-word model exported to TFLite. The bundled default `mycroft.conf` ships it as `hey_mycroft_tflite`, the first fallback below the ONNX default.

### Default Configuration

```jsonc
"hotwords": {
  "hey_mycroft_tflite": {
    "module": "ovos-ww-plugin-precise-lite",
    "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite",
    "trigger_level": 3,
    "sensitivity": 0.5,
    "listen": true
  }
}

```

---

## ovos-ww-plugin-openWakeWord

- **GitHub**: [OpenVoiceOS/ovos-ww-plugin-openWakeWord](https://github.com/OpenVoiceOS/ovos-ww-plugin-openWakeWord)


- **Description**: Wake-word detection using the open-source openWakeWord neural models.

---

## ovos-ww-plugin-vosk

- **GitHub**: [OpenVoiceOS/ovos-ww-plugin-vosk](https://github.com/OpenVoiceOS/ovos-ww-plugin-vosk)


- **Description**: Mycroft wake word plugin for [Vosk](https://alphacephei.com/vosk/)

### Default Configuration

```jsonc
  "listener": {
    "wake_word": "hey_computer"
  },
  "hotwords": {
    "hey_computer": {
        "module": "ovos-ww-plugin-vosk",
        "listen": true
    }
  }

```

---

## ovos-ww-plugin-precise-onnx

- **GitHub**: [OpenVoiceOS/ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx)


- **Description**: Runs Precise wake word models exported to ONNX. It is the plugin the bundled default `mycroft.conf` ships for `hey_mycroft`.

### Default Configuration

```jsonc
"listener": {
  "wake_word": "hey_mycroft"
},
"hotwords": {
  "hey_mycroft": {
    "module": "ovos-ww-plugin-precise-onnx",
    "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.onnx",
    "trigger_level": 3,
    "sensitivity": 0.5
   }
}

```

!!! tip "Donating wake-word samples"
    The listener can optionally upload wake-word audio samples to an open-data server to help improve detection accuracy. This is opt-in and off by default. See [Privacy & Security](privacy-security.md#opt-in-wake-word-and-stt-sample-donation).

---

## Further reading

- [Precise Wake Word Engine Goes ONNX!](https://blog.openvoiceos.org/posts/2025-11-03-precise-onnx), OVOS blog
