# TTS Transformers

!!! abstract "In a nutshell"
    After the assistant has turned its reply into spoken audio, these plugins can touch up that *sound* before you hear it. Like adding effects in a music app, they can sharpen clarity, apply audio effects, or change the voice. See [TTS Plugins](tts-plugins.md) for the voices themselves and the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    TTS transformers are the **`tts` chain** of **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §3.6** (a formal [architecture spec](architecture-specs.md)). The spec's post-TTS, pre-playback injection point receives a path/handle to the synthesized audio, an optional `lang`, and the full `Message.context`; it may replace the audio with a transformed version (pitch, reverb, EQ, tempo, super-resolution, watermarking, earcons). It **SHOULD NOT** re-synthesize speech in a different language or with different content — translation and rewriting are [dialog-transformer](dialog-transformers.md) concerns, done against the text before TTS. **Ordering:** the chain runs by **ascending** `priority` (lowest first), matching the spec.

**TTS Transformers** in OpenVoiceOS (OVOS) are plugins that process synthesized speech audio. They run after the [Text-to-Speech](tts-plugins.md) (TTS) engine generates it but before it's played back to the user.

They post-process audio to apply effects, enhance clarity, clone a voice, or tailor the output to specific needs.

---

## How They Work

The typical flow for speech output in OVOS is:

1. **Dialog Generation**: The assistant formulates a textual response.


2. **Dialog Transformation**: Optional plugins modify the text to adjust tone or style.


3. **Text-to-Speech (TTS)**: The text is converted into speech audio.


4. **TTS Transformation**: Plugins apply audio effects or modifications to the speech.


5. **Playback**: The final audio is played back to the user.

TTS Transformers operate in step 4. They add dynamic audio enhancements without altering the original TTS output.

They run inside the **ovos-audio** service, in the playback path. Once the TTS engine has written a wav file, each loaded transformer's `transform(wav_file, context)` is called. It is expected to return the path to the (possibly new) wav file to play. Transformers run in **ascending priority** order (lower `priority` first), each receiving the previous one's output path.

---

## Configuration

To enable TTS Transformers, add them to your `mycroft.conf` under the `tts_transformers` section:

```jsonc
"tts_transformers": {
  "plugin_name": {
    // plugin-specific configuration
  }
}

```

Replace `"plugin_name"` with the identifier of the desired plugin and provide any necessary configuration parameters.

---

## Available TTS [Transformer](transformer-plugins.md) Plugins

### **OVOS SoX TTS Transformer**

* **Purpose**: Applies various audio effects using SoX (Sound eXchange) to the TTS output.


* **Features**:


    * Pitch shifting


    * Reverb


    * Tempo adjustment


    * Equalization


    * Noise reduction


    * And many more


* **Installation**:

```bash
  pip install ovos-tts-transformer-sox-plugin

```

* **Configuration Example**:

```jsonc
  "tts_transformers": {
    "ovos-tts-transformer-sox-plugin": {
      "default_effects": {
        "reverb": {},
        "pitch": {"n_semitones": 1}
      }
    }
  }

```

  `default_effects` is a **dict** mapping an effect name to its parameter dict (each is
  forwarded as keyword arguments). Supported effects include `pitch`, `phaser`, `flanger`,
  `reverb`, `tempo`, `treble`, `tremolo`, `reverse`, `speed`, `chorus`, and `echo`.

* **Requirements**: Ensure SoX is installed and available in your system's PATH.


* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin)

---

!!! warning "Upcoming — unreleased"
    The following super-resolution transformers exist in their repos but are **not yet published to PyPI**, so `pip install` will not find them. They upsample/enhance the TTS audio before playback.

    * **OVOS FlashSR TTS Transformer** (`FlashSRTTSTransformer`): ONNX-based audio super-resolution, downloads its model from the Hugging Face Hub. Entry point `ovos-tts-transformer-FlashSR` under `opm.transformer.tts`. Source: [ovos_tts_transformer_FlashSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_FlashSR).
    * **OVOS NovaSR TTS Transformer** (`NovaSRTTSTransformer`): torch-based super-resolution upsampler. Entry point `ovos-tts-transformer-NovaSR` under `opm.transformer.tts`. Source: [ovos_tts_transformer_NovaSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_NovaSR).

---

### **OVOS AudioSR TTS Transformer**

!!! warning "Not yet on PyPI"
    Like FlashSR and NovaSR above, `ovos-tts-transformer-audiosr` has no PyPI release yet
    (only prerelease tags on GitHub) — the config below is for when it ships, or a
    from-source install.

Engine-agnostic ONNX audio super-resolution transformer (`opm.transformer.tts`). It upscales
**any** TTS engine's output to 48 kHz just before playback, rather than being tied to one voice
or engine. It wraps [`audiosronnx`](https://github.com/TigreGotico/audiosronnx) (pure ONNX, no
Torch at runtime) and picks between `novasr` (default), `lavasr`, `hifiganbwe`, and `apbwe` engines
via config. If audio is already 48 kHz, or the model/weights are unavailable, it returns the
original audio unchanged so synthesis never breaks.

```jsonc
"tts_transformers": {
  "ovos-tts-transformer-audiosr": {"engine": "novasr"}
}
```

* **Source**: [ovos-tts-transformer-audiosr](https://github.com/OpenVoiceOS/ovos-tts-transformer-audiosr)

---

## Writing your own TTS Transformer

Subclass `TTSTransformer` (`ovos_plugin_manager.templates.transformers`) and override
its `transform(wav_file, context=None) -> Tuple[str, dict]` method. Register the class
under the `opm.transformer.tts` entry-point group.

**Create a Python Class**:

```python
from typing import Tuple
from ovos_plugin_manager.templates.transformers import TTSTransformer


class MyCustomTTSTransformer(TTSTransformer):
    def __init__(self, name="my-custom-tts-transformer", priority=10, config=None):
        super().__init__(name, priority, config)

    def transform(self, wav_file: str, context: dict = None) -> Tuple[str, dict]:
        """Transform passed wav_file and return path to transformed file"""
        # Apply custom audio processing to wav_file, write the result,
        # and return the path to the file that should be played
        modified_wav_file = wav_file  # replace with your processed file path
        return modified_wav_file, context
```


A lower `priority` runs earlier in the chain; the default is 50, and each
transformer receives the previous one's output path.

**Register as a Plugin**. A full `pyproject.toml` for a standalone plugin package:

```toml
[project]
name = "ovos-tts-transformer-mycustom"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.transformer.tts"]
"my-custom-tts-transformer" = "my_module:MyCustomTTSTransformer"
```

An `opm.transformer.tts.config` group is also available, for a dict of config
metadata an installer or GUI can read. It is optional; add it once the plugin has
settings worth advertising.

**Install and Configure**:
After installation, add your transformer to the `mycroft.conf`:

```jsonc
"tts_transformers": {
 "my-custom-tts-transformer": {}
}

```

### Test it without OVOS

`TTSTransformer` subclasses are plain classes, so a unit test needs no bus. Pass an
explicit `config` though: when it is omitted, the base `__init__` reads the plugin's section
from the `Configuration()` singleton, which touches the on-disk config layers:

```python
from my_module import MyCustomTTSTransformer

transformer = MyCustomTTSTransformer(config={})
wav_path, context = transformer.transform("/tmp/speech.wav")
assert wav_path == "/tmp/speech.wav"
```

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.tts_transformers import find_tts_transformer_plugins

print(find_tts_transformer_plugins())
# {'my-custom-tts-transformer': <class 'my_module.MyCustomTTSTransformer'>}
```

### Checklist before you publish

1. `transform()` accepts a `wav_file: str` and returns `(wav_file, context)`.
2. `__init__` hardcodes the plugin `name` and forwards `name`, `priority`, `config`
   to `super().__init__()`.
3. The entry-point group in `pyproject.toml` is `opm.transformer.tts`.
4. A unit test calls `transform()` directly, with no OVOS services running.
5. `find_tts_transformer_plugins()` discovers the installed plugin under the
   expected name.

---

TTS Transformers let you enhance the sound of your OVOS assistant, tailoring speech output to your preferences or application requirements.

---
**Read next:** [Language Support Overview](lang-support.md)
**Related:** [Audio Transformers](audio-transformers.md) · [TTS Plugins](tts-plugins.md) · [TTS Server](tts-server.md)

