# Transformer Plugins

!!! abstract "In a nutshell"
    Your voice travels through the assistant: from raw sound, to written words, to a matched
    request, to the spoken reply. Transformer plugins are optional helpers that can tidy or tweak
    the information at each step. Think of them as filters on an assembly line. One might clean
    up background noise. Another might fix a misheard word before the system tries to understand
    it. They don't take over any step. They just polish what passes between steps. See the
    [Glossary](glossary.md) for related terms.

??? info "Formal specification"
    The transformer subsystem is specified by **[OVOS-TRANSFORM-1: Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md)** (one of the formal [architecture specs](architecture-specs.md)). It defines **six ordered chains**: `audio`, `utterance`, `metadata`, `intent`, `dialog`, `tts`. These run at fixed points in the utterance lifecycle. It also defines the per-type input/output contract for each, the per-session ordering and denylist overrides, and the utterance-cancellation signal. A transformer is identified by its `(type, transformer_id)` pair. Where this manual or the current code diverges from the spec, the spec is canonical.

    **Ordering.** OVOS-TRANSFORM-1 §4 orders each chain by **ascending** `priority`. A lower number runs **earlier**, and the default is `50`. The current OVOS code follows this: a plugin with `priority=1` runs first, and later plugins see and may override its output. A legacy descending order is still available as an explicit opt-in (`sort_ascending=False`, marked deprecated in `ovos_plugin_manager/transformer_services.py`) for deployments that depend on the old behavior.

Transformer plugins let you intercept and modify data as it flows through the transformer chain. Each type is a small class with a `transform()` method that runs at a fixed stage. Examples are turning raw audio into cleaner audio, fixing transcribed text before intent matching, enriching a matched intent, or post-processing speech before playback.

A transformer never *replaces* a stage. It sits between two stages and reshapes what passes through. Several plugins of the same type can be active at once. They run in sequence, lowest `priority` first, so each one builds on the output of the previous.

!!! note "Synchronous contract: keep transformers fast"
    `transform()` (and `on_audio()`/`on_speech()`) are plain synchronous methods. The chain
    runner calls each one inline, in order, on the thread that owns the chain. A slow
    transformer blocks the owning service for its full duration. There is no background
    execution or timeout. This matters most for `AudioTransformer`, which sits on the
    real-time audio path. Keep its work fast, and offload anything heavy (model inference,
    network calls) to a background thread/process instead of doing it inside `transform()`.

    There is no async return path back into the chain. `transform()` is called inline and
    must return before the chain can proceed, so it cannot await a background job's result
    mid-chain. "Offload the heavy work" only helps if `transform()` can return
    cached/previous data immediately on each call, while the background thread/process
    updates that cache for the *next* call to pick up. The current call never blocks on
    the background job finishing.

## Transformer Types

All base classes live in `ovos_plugin_manager.templates.transformers` and share the same constructor: `__init__(self, name, priority=50, config=None)`, plus `bind(bus)` and `initialize()`. The loader (`TransformersService.load_plugins()` in `ovos_plugin_manager.transformer_services`) only ever instantiates a plugin as `plug(config=plugin_config)`. It does not pass `name` or `priority`. Since the base class has no default for `name`, every plugin must override `__init__` to supply its own `name` (and usually a default `priority`). Each plugin must call `super().__init__(name, priority, config)` so the base class still gets them.

A `"priority"` key in a plugin's `mycroft.conf` block is not applied automatically. The plugin must read it back out of `self.config` itself if it wants deployments to override priority (see [Utterance Transformers: Config-driven priority](utterance-transformers.md#config-driven-priority)).

| Type | Stage | Base Class | Entry-point group |
|------|-------|------------|-------------------|
| **Audio** | Before STT | `AudioTransformer` | `opm.transformer.audio` |
| **Utterance** | After STT, before Intent | `UtteranceTransformer` | `opm.transformer.text` |
| **Metadata** | After Utterance, before Intent | `MetadataTransformer` | `opm.transformer.metadata` |
| **Intent** | After Intent match, before Skill | `IntentTransformer` | `opm.transformer.intent` |
| **Dialog** | Before TTS | `DialogTransformer` | `opm.transformer.dialog` |
| **TTS** | After TTS, before Playback | `TTSTransformer` | `opm.transformer.tts` |

The runner classes that load and chain these plugins live in `ovos-plugin-manager` (`ovos_plugin_manager.transformer_services`): `UtteranceTransformersService`, `MetadataTransformersService`, `IntentTransformersService`, `AudioTransformersService`, `DialogTransformersService`, `TTSTransformersService`. Each consumer imports the one it needs. `ovos-core` runs the utterance/metadata/intent chains, the listener runs the audio chain, and the audio/TTS stacks run the dialog/TTS chains.

---

## 1. Audio Transformers
**Entry point:** `opm.transformer.audio`

Used to process or transform raw audio before it reaches the STT engine. Common use cases include noise reduction, volume normalization, or streaming language detection.

### Template

```python
from ovos_plugin_manager.templates.transformers import AudioTransformer

class MyAudioTransformer(AudioTransformer):
    def on_audio(self, audio_data):
        # Process non-speech chunks
        return audio_data

    def on_speech(self, audio_data):
        # Process speech chunks during recording
        return audio_data

    def transform(self, audio_data):
        # Final transformation and optional context injection
        return audio_data, {"extra_metadata": "value"}

```

---

## 2. Utterance Transformers
**Entry point:** `opm.transformer.text`

Used to modify the transcribed text (utterances) before they are sent to the intent service. Common use cases include spelling correction, filtering, or expansion. See [Utterance Transformers](utterance-transformers.md) for details.

### Template

```python
from ovos_plugin_manager.templates.transformers import UtteranceTransformer

class MyUtteranceTransformer(UtteranceTransformer):
    def transform(self, utterances, context=None):
        # utterances is a list of strings
        transformed = [u.upper() for u in utterances]
        return transformed, context

```

---

## 3. Metadata Transformers
**Entry point:** `opm.transformer.metadata`

Used to inject or modify metadata in the message context. This runs after utterance transformers but before intent matching. `transform(context)` returns a (possibly modified) context dict.

---

## 4. Intent Transformers
**Entry point:** `opm.transformer.intent`

Used to modify the `IntentHandlerMatch` object. This runs after a pipeline match is found but before the skill is triggered. See [Intent Transformers](intent-transformers.md) for details.

---

## 5. Dialog Transformers
**Entry point:** `opm.transformer.dialog`

Used to modify the text that OVOS is about to speak, just before it is sent to the TTS engine.

---

## 6. TTS Transformers
**Entry point:** `opm.transformer.tts`

Used to process the generated WAV file after TTS synthesis but before it is played back.

---

## Standalone Usage

You can use transformers independently of the full OVOS stack. Here is an example with an `UtteranceTransformer`:

```python
from ovos_plugin_manager.text_transformers import find_utterance_transformer_plugins

# Find and load the plugin (returns {plugin_name: class})
plugins = find_utterance_transformer_plugins()
transformer_class = plugins["ovos-utterance-normalizer"]
transformer = transformer_class()  # base __init__ supplies the name

# Transform an utterance (utterances is a list of strings)
utterances = ["hello world"]
transformed, context = transformer.transform(utterances)
print(f"Transformed: {transformed}")

```

The discovery helpers (`find_*_transformer_plugins`, `load_*_transformer_plugin`) live in
`ovos_plugin_manager.text_transformers`, `.intent_transformers`, `.metadata_transformers`,
`.audio_transformers`, and `.dialog_transformers`.

`find_tts_transformer_plugins` / `load_tts_transformer_plugin` live in their own
`ovos_plugin_manager.tts_transformers` module. `ovos_plugin_manager.dialog_transformers`
re-exports both names for backwards compatibility, but that module is not their canonical
home.

## Creating a Plugin

1.  **Inherit** from the appropriate base class.


2.  **Implement** the `transform` method (or specific audio hooks).


3.  **Register** the entry point in your `pyproject.toml`, using the group for your transformer type (here, an utterance transformer):

```toml
[project.entry-points."opm.transformer.text"]
my-transformer = "my_package.module:MyTransformer"

```

!!! note "No config-discovery entry point for transformers"
    TTS and STT plugins can register a second entry point (`opm.tts.config`, `opm.stt.config`)
    that exposes sample configurations for UI discovery. See
    [TTS Plugins: Entry point](tts-plugins.md#entry-point). `ovos-plugin-manager`'s
    `PluginConfigTypes` enum has no matching entry for any transformer type (audio, utterance,
    metadata, intent, dialog, or tts transformers). A transformer plugin only registers under
    its `opm.transformer.*` group; there is no equivalent `opm.transformer.text.config` group to
    advertise its settings.

## Package and publish

1. **Pin the dependency version.** Put a floor and a ceiling on `ovos-plugin-manager` in
   `pyproject.toml`, for example `ovos-plugin-manager>=0.5.0,<1.0.0`, so a future breaking
   release does not silently pull in.

2. **Install for local development.** Run `pip install -e .` from the plugin's own repository.
   See [OVOS Plugin Manager: Install and verify](plugin-manager.md#3-install-and-verify) for the
   check that confirms the plugin is discoverable.

3. **Publish to PyPI.** The Plugin Arena's benchmark sweep installs competitors from PyPI, so a
   transformer plugin needs a PyPI release before it can be entered. See
   [Plugin Arena: Getting Your Plugin Ranked](plugin-arena.md#getting-your-plugin-ranked) and
   [TTS Plugins: Package and publish](tts-plugins.md#package-and-publish) for the shared steps.

## Test your plugin locally

Instantiate the class directly and call `transform()` on it:

```python
from my_transformer_package import MyCustomTransformer

transformer = MyCustomTransformer()
utterances, context = transformer.transform(["HELLO WORLD"])
assert utterances == ["hello world"]
```

Turn that into a pytest test that checks both return values:

```python
from my_transformer_package import MyCustomTransformer

def test_transform_lowercases_utterances():
    transformer = MyCustomTransformer()
    utterances, context = transformer.transform(["HELLO WORLD"], context={})
    assert utterances == ["hello world"]
    assert isinstance(context, dict)
```

To exercise the plugin inside a full OVOS install, `pip install -e .` it into the same virtual
environment or container `ovos-core` runs in, then add its name under the matching section of
`mycroft.conf` (for example `"utterance_transformers": {"my-custom-transformer": {}}`) and
restart OVOS.

# Transformer plugins Reference

| Plugin | Description | Maturity |
|--------|-------------|-------|
| [ovos-dialog-normalizer-plugin](#ovos-dialog-normalizer-plugin) | a dialog transformer plugins for OVOS | Stable |
| [ovos-bidirectional-translation-plugin](#ovos-bidirectional-translation-plugin) | This package includes a UtteranceTransformer plugin and a DialogTransformer plugin, they work together to allow OVOS to speak in ANY language | Stable |
| [ovos-audio-transformer-plugin-speechbrain-langdetect](#ovos-audio-transformer-plugin-speechbrain-langdetect) | spoken language detector for ovos | Stable |
| [ovos-utterance-corrections-plugin](#ovos-utterance-corrections-plugin) | This plugin provides tools to correct or adjust speech-to-text (STT) outputs for better intent matching or improved user experience. | Stable |
| [ovos-utterance-normalizer](#ovos-utterance-normalizer) | normalizes utterances before intent parsing | Stable |
| [ovos-utterance-plugin-cancel](#ovos-utterance-plugin-cancel) | looks at the end of the transcribed phrase and ignores it if it ends with "nevermind that", "cancel it", or "ignore that". | Stable |
| [ovos-audio-transformer-plugin-ggwave](#ovos-audio-transformer-plugin-ggwave) | plugin for [ggwave](https://github.com/ggerganov/ggwave) | Mature |
| [ovos-tts-transformer-sox-plugin](#ovos-tts-transformer-sox-plugin) | A Text-to-Speech (TTS) transformer that uses SoX (Sound eXchange) for audio processing. The transformer applies various effects to the generated audio before playback. | Beta |
| [ovos_tts_transformer_FlashSR](#ovos_tts_transformer_flashsr) | ONNX-based audio super-resolution that upsamples synthesized TTS audio before playback (not yet on PyPI). | Proof-of-concept |
| [ovos_tts_transformer_NovaSR](#ovos_tts_transformer_novasr) | torch-based audio super-resolution upsampler for synthesized TTS audio (not yet on PyPI). | Proof-of-concept |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).

## ovos-dialog-normalizer-plugin

- **GitHub**: [OpenVoiceOS/ovos-dialog-normalizer-plugin](https://github.com/OpenVoiceOS/ovos-dialog-normalizer-plugin)


- **Description**: a dialog transformer plugins for OVOS

---

## ovos-bidirectional-translation-plugin

- **GitHub**: [OpenVoiceOS/ovos-bidirectional-translation-plugin](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)


- **Description**: This package includes a UtteranceTransformer plugin and a DialogTransformer plugin, they work together to allow OVOS to speak in ANY language

---

## ovos-audio-transformer-plugin-speechbrain-langdetect

- **GitHub**: [OpenVoiceOS/ovos-audio-transformer-plugin-speechbrain-langdetect](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-speechbrain-langdetect)


- **Description**: spoken language detector for ovos

---

## ovos-utterance-corrections-plugin

- **GitHub**: [OpenVoiceOS/ovos-utterance-corrections-plugin](https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin)


- **Description**: This plugin provides tools to correct or adjust speech-to-text (STT) outputs for better intent matching or improved user experience.

---

## ovos-utterance-normalizer

- **GitHub**: [OpenVoiceOS/ovos-utterance-normalizer](https://github.com/OpenVoiceOS/ovos-utterance-normalizer)


- **Description**: normalizes utterances before intent parsing

---

## ovos-utterance-plugin-cancel

- **GitHub**: [OpenVoiceOS/ovos-utterance-plugin-cancel](https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel)


- **Description**: looks at the end of the transcribed phrase and ignores it if it ends with "nevermind that", "cancel it", or "ignore that".

---

## ovos-audio-transformer-plugin-ggwave

- **GitHub**: [OpenVoiceOS/ovos-audio-transformer-plugin-ggwave](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave)


- **Description**: plugin for [ggwave](https://github.com/ggerganov/ggwave)

---

## ovos-tts-transformer-sox-plugin

- **GitHub**: [OpenVoiceOS/ovos-tts-transformer-sox-plugin](https://github.com/OpenVoiceOS/ovos-tts-transformer-sox-plugin)


- **Description**: A Text-to-Speech (TTS) transformer that uses SoX (Sound eXchange) for audio processing. The transformer applies various effects to the generated audio before playback.

---

## ovos_tts_transformer_FlashSR

- **GitHub**: [OpenVoiceOS/ovos_tts_transformer_FlashSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_FlashSR)


- **Description**: ONNX-based audio super-resolution TTS transformer (`FlashSRTTSTransformer`). It upsamples synthesized audio before playback, downloading its model from the Hugging Face Hub. Entry point `ovos-tts-transformer-FlashSR` under `opm.transformer.tts`. **Upcoming**: not yet published to PyPI.

---

## ovos_tts_transformer_NovaSR

- **GitHub**: [OpenVoiceOS/ovos_tts_transformer_NovaSR](https://github.com/OpenVoiceOS/ovos_tts_transformer_NovaSR)


- **Description**: torch-based super-resolution upsampler TTS transformer (`NovaSRTTSTransformer`). Entry point `ovos-tts-transformer-NovaSR` under `opm.transformer.tts`. **Upcoming**: not yet published to PyPI.

---
**Read next:** [Utterance Transformers](utterance-transformers.md)
**Related:** [Pipelines Overview](pipelines-overview.md) · [Dialog Transformers](dialog-transformers.md) · [LLM Transformers](llm-transformers.md)

---

