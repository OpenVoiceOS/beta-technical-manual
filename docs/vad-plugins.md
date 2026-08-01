# Voice Activity Detection (VAD) Plugins

!!! abstract "In a nutshell"
    *Voice Activity Detection* (VAD) is how the assistant tells the difference between someone actually speaking and plain silence or background noise. It lets the system know when you have started talking. It also tells the system when you have finished, so it knows when to stop listening and respond. Without it, the assistant would not know where your command begins and ends. See the [Glossary](glossary.md) for related terms.

Voice Activity Detection (VAD) is a critical component in the OVOS listener pipeline. It identifies segments of audio that contain human speech, so the system can ignore silence and background noise.

!!! note "Audio format contract"
    Like STT and wake-word plugins, VAD plugins receive raw PCM from the [microphone plugin](mic-plugins.md#the-microphone-interface): **16 kHz sample rate, 16-bit samples, mono, little-endian**, delivered in **4096-byte chunks** by default.

## How it works

The VAD engine continuously monitors the microphone's audio stream. Its primary roles are:

1.  **Speech Start Detection**: Triggering the recording of a command after the wake word is detected.


2.  **Speech End Detection**: Identifying when the user has finished speaking, so the audio can be sent for processing (STT).

!!! tip "Recommended: silero"
    `ovos-vad-plugin-silero` uses a small neural model and gives the most accurate
    speech/silence boundary detection. It is the recommended default when you can afford
    the modest extra CPU cost of running it. `ovos-vad-plugin-webrtcvad` is a good lighter
    fallback: CPU-only and widely used, at somewhat lower accuracy. `ovos-vad-plugin-noise`
    trades the most accuracy for requiring no model download at all.

    **Relative footprint:** silero runs a small neural model, so it is heavier than the
    energy/noise or WebRTC VADs. It is still light next to a wake word or STT model, since
    VAD only has to classify one chunk as speech/silence, not decode it.

## Configuration

You can configure the VAD plugin in your `mycroft.conf`. The example below uses
`ovos-vad-plugin-webrtcvad` purely to show the shape of the config. See
[ovos-vad-plugin-silero](#ovos-vad-plugin-silero) below for the recommended plugin's config:

```json
{
 "listener": {
   "VAD": {
     "module": "ovos-vad-plugin-webrtcvad",
     "ovos-vad-plugin-webrtcvad": {
       "vad_mode": 3
     }
   }
 }
}

```

## Supported VAD Plugins

| Plugin | Description | Maturity |
|--------|-------------|----------|
| [ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad) | Based on Google's WebRTC VAD (`webrtcvad-wheels`). Lightweight, CPU-only, widely used. `vad_mode` (0 to 3) sets how aggressively it filters out non-speech. `0` is the least aggressive: most permissive, more likely to classify borderline audio as speech. `3` is the most aggressive at filtering out non-speech and is the plugin's default. | Stable |
| [ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero) | Uses the Silero deep-learning model for high-accuracy VAD, particularly in noisy environments. | Stable |
| [ovos-vad-plugin-noise](https://github.com/OpenVoiceOS/ovos-vad-plugin-noise) | Simple energy/noise-threshold VAD with no model download. | Stable |

--8<-- "snippets/maturity-disclaimer.md"

> Specification: audio capture and VAD are deployer-defined components feeding the listener. See [OVOS-AUDIO-IN-1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) for the audio-input service that consumes their output.

---

## Technical Explanation

All VAD plugins inherit from the `VADEngine` base class provided by `ovos-plugin-manager`.

### The VADEngine Interface

This is the actual base class shipped in `ovos_plugin_manager.templates.vad`:

```python
class VADEngine:
    def __init__(self, config: Optional[dict] = None,
                sample_rate: Optional[int] = None):
        # config keys: padding_duration_ms (default 300), frame_duration_ms
        # (default 30), thresh (default 0.8); sample_rate falls back to
        # listener.sample_rate in core config, then 16000
        self.config = config or {}
        self.sample_rate = sample_rate or 16000
        ...

    @abc.abstractmethod
    def is_silence(self, chunk) -> bool:
        """Return True if the chunk is silence, False if it is speech."""
        return False

    def reset(self):
        """Reset any internal state between utterances (optional)."""

```

Subclasses only need to implement `is_silence`. The base class provides
`extract_speech(audio)`, which uses `is_silence` over a sliding window to trim
leading/trailing silence from a buffer, and a `runtime_requirements` classproperty
(the deprecated [`RuntimeRequirements`](skill-runtime-requirements.md) mechanism)
used by the plugin manager to advertise network/offline behavior.

## Creating Your Own VAD Plugin

To create a new VAD plugin, subclass `VADEngine` and implement its one abstract method,
`is_silence(self, chunk) -> bool`. The base class handles everything else: `extract_speech`,
the padding/threshold bookkeeping in `__init__`, and `runtime_requirements`.

### 1. A minimal working plugin

Project layout:

```
ovos-vad-plugin-mymodel/
├── pyproject.toml
└── ovos_vad_plugin_mymodel/
    └── __init__.py
```

`ovos_vad_plugin_mymodel/__init__.py`:

```python
from ovos_plugin_manager.templates.vad import VADEngine


class MyCustomVAD(VADEngine):
    def is_silence(self, chunk) -> bool:
        # Implement your VAD logic here
        # Return True for silence, False for speech
        is_speech = self.my_model.predict(chunk)
        return not is_speech

```

### 2. Registration

`pyproject.toml`. The entry point is what makes it a plugin. The group must be `opm.VAD`
(note the uppercase `VAD`), and the entry-point name (left of `=`) is the string users put
in their `mycroft.conf`:

```toml
[project]
name = "ovos-vad-plugin-mymodel"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.VAD"]
ovos-vad-plugin-mymodel = "ovos_vad_plugin_mymodel:MyCustomVAD"

```

There is a parallel `opm.VAD.config` group for a dict of config metadata used by
installers and GUIs. It is optional. Add it once the plugin has settings worth
advertising.

> The legacy alias `ovos.plugin.VAD` is still accepted, but new plugins should use `opm.VAD`.

### 3. Test it without OVOS

`VADEngine` is a plain class with no messagebus connection, so a unit test needs no
running OVOS stack:

```python
from ovos_vad_plugin_mymodel import MyCustomVAD

vad = MyCustomVAD()
silence_chunk = b"\x00" * 640
assert vad.is_silence(silence_chunk) is True
```

### 4. Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.vad import find_vad_plugins

print(find_vad_plugins())
# {'ovos-vad-plugin-mymodel': <class '...MyCustomVAD'>}
```

`load_vad_plugin(name)` returns the same uninstantiated class for one plugin name. You
construct it yourself with your config dict.

### 5. Checklist before you publish

1. The class subclasses `VADEngine` and implements `is_silence(chunk) -> bool`.
2. `__init__` accepts `config=None` and `sample_rate=None` and works with an empty config
   (or call `super().__init__(config, sample_rate)` and add nothing new).
3. The entry-point group in `pyproject.toml` is `opm.VAD`.
4. Unit tests exercise `is_silence` directly, with no OVOS services running.
5. `find_vad_plugins()` discovers the installed plugin under the expected name.

## Standalone Usage

You can use the VAD engine in your own scripts:

```python
from ovos_plugin_manager.vad import find_vad_plugins

# Load the plugin
plugins = find_vad_plugins()
vad_class = plugins["ovos-vad-plugin-webrtcvad"]
vad = vad_class()

# Process an audio chunk
is_silence = vad.is_silence(audio_chunk)
if not is_silence:
    print("Speech detected!")

```

# VAD Plugins Reference

Detailed per-plugin configuration for the same roster listed in
[Supported VAD Plugins](#supported-vad-plugins) above.

## ovos-vad-plugin-webrtcvad

- **GitHub**: [OpenVoiceOS/ovos-vad-plugin-webrtcvad](https://github.com/OpenVoiceOS/ovos-vad-plugin-webrtcvad)


- **Description**: Voice activity detection using webrtcvad.

---

## ovos-vad-plugin-noise

- **GitHub**: [OpenVoiceOS/ovos-vad-plugin-noise](https://github.com/OpenVoiceOS/ovos-vad-plugin-noise)


- **Description**: simple VAD plugin extracted from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py)

---

## ovos-vad-plugin-silero

- **GitHub**: [OpenVoiceOS/ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero)


- **Description**: Silero Voice Activity Detection (VAD) plugin. The Silero ONNX
  model **ships inside the package**, so it runs fully offline with no first-run
  download. Requires 16 kHz audio (it raises rather than resampling).

### Default Configuration

```jsonc
{
    "listener": {
        "VAD": {
            "module": "ovos-vad-plugin-silero",
            "ovos-vad-plugin-silero": {
                // speech-probability cutoff; below this a chunk is treated as silence
                "threshold": 0.2,
                // optional: override the bundled model with a custom ONNX file
                "model": "/optional/path/to/model.onnx"
            }
        }
    }
}

```

| Config key | Default | Effect |
|---|---|---|
| `threshold` | `0.2` | Speech-probability cutoff. Chunks scoring below it are classified as silence |
| `model` | bundled `silero_vad.onnx` | Path to a custom ONNX model. Defaults to the model shipped in the package |

!!! tip "Same package also provides a pre-wake VAD verifier"
    `ovos-vad-plugin-silero` registers a second entry point, `ovos-ww-verifier-silero`
    (`opm.wake_word.verifier`), which re-checks that a wake word activation actually
    contains speech before waking. It works as a "noise filter" that cuts false wakes.
    It has its own `threshold` (default `0.1`). See the Pre-Wake VAD blog post below.

---

---
**Read next:** [Wake-word Plugins](wake-word-plugins.md)
**Related:** [Microphone Plugins](mic-plugins.md) · [STT Plugins](stt-plugins.md) · [Choosing Plugins](choosing-plugins.md) · [OVOS Just Got a Noise Filter (Pre-Wake VAD)](https://blog.openvoiceos.org/posts/2025-11-06-prewake-vad)
