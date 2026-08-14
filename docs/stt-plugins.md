# STT Plugins

!!! abstract "In a nutshell"
    STT stands for *Speech-to-Text*: this is the part that listens to your spoken words and writes them down as text the assistant can read. It is the same idea as the dictation feature on a phone. Different STT plugins offer different trade-offs in speed, accuracy, and whether they run on your own device or in the cloud, so you can pick the one that suits you. See the [Glossary](glossary.md) for related terms.

Writing a plugin instead of choosing one? See [Writing an STT Plugin](stt-plugin-development.md).

??? info "Formal specification"
    STT sits inside the audio input service, specified by **[OVOS-AUDIO-IN-1: Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md)**: capture → audio-transformer chain → STT → utterance. The transcript is emitted on `ovos.utterance.handle` ([OVOS-PIPELINE-1 §9.1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)). See the [spec index](architecture-specs.md).

!!! note "Audio format contract"
    Everything upstream of an STT plugin, the [microphone plugin](mic-plugin-development.md#the-microphone-interface) and any audio transformers, hands over raw PCM in a fixed shape: **16 kHz sample rate, 16-bit samples, mono, little-endian**, delivered in **4096-byte chunks** by default (the `Microphone` template's `sample_rate`/`sample_width`/`sample_channels`/`chunk_size` defaults). A batch `STT.execute()` plugin gets this bundled into a `speech_recognition.AudioData` object. A `StreamingSTT` plugin receives it chunk-by-chunk, still at this same format, unless a deployment explicitly reconfigures the microphone.

    Neither the `STT` nor the `StreamingSTT` template resamples on the plugin's behalf. If the wrapped model expects a different native rate, converting the incoming 16 kHz PCM is the plugin's own job.

STT (Speech-to-Text) plugins convert spoken audio into text. They are the bridge
between the listener and the intent pipeline.

!!! tip "Recommended: onnx-asr"
    For offline, on-device recognition, `ovos-stt-plugin-onnx-asr` is the recommended
    starting point: it runs entirely through ONNX Runtime, with no PyTorch/transformers
    dependency, and covers NeMo Parakeet/Canary, Whisper and wav2vec2 model families. Cloud
    STT (e.g. `ovos-stt-plugin-azure`) is a fair choice when the local device doesn't have
    the compute budget for on-device recognition.

    `ovos-stt-plugin-onnx-asr` is rated **Beta** while several alternatives are Stable.
    It is recommended here for its offline quality and footprint. Per the
    [Maturity Scale](maturity.md), maturity is not the same as a recommendation.

    **Footprint:** as noted in the [plugin's own entry](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr), most models
    in the [OpenVoiceOS/stt-asr-onnx](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx)
    collection ship both `fp32` and `int8` weights. Pick `int8` for the lower-RAM, lower-compute
    option on constrained hardware. Beyond quantization, footprint is mostly driven by model
    family/size: a small Parakeet/wav2vec2-class model is far lighter than a large
    Whisper-class one, independent of the plugin wrapping it.

## Using an STT plugin

Install a plugin and point your `mycroft.conf` at it:

```bash
pip install ovos-stt-plugin-onnx-asr
```

```json
{
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr",
    "ovos-stt-plugin-onnx-asr": {
      "model": "nemo-parakeet-tdt-0.6b-v3"
    }
  }
}
```

The roster below lists available plugins with a recommended starting configuration for each. This may differ from a plugin's built-in default, noted where relevant.

## STT Plugins Reference

Code license is the SPDX license of the plugin's own repository. Where the plugin wraps a
separately-licensed model, that is called out under "model".

| Plugin | Description | License | Maturity |
|--------|-------------|---------|----------|
| [ovos-stt-plugin-wav2vec](stt-plugins-reference.md#ovos-stt-plugin-wav2vec) | OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/) | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-azure](stt-plugins-reference.md#ovos-stt-plugin-azure) | Microsoft Azure cloud speech-to-text. | Apache-2.0 (cloud service, separate Microsoft terms) | Stable |
| [ovos-stt-plugin-chromium](stt-plugins-reference.md#ovos-stt-plugin-chromium) | Speech-to-text using the Google Chrome browser speech API. | Apache-2.0 (cloud service, unofficial Google endpoint, separate Google terms) | Stable |
| [ovos-stt-plugin-mms](stt-plugins-reference.md#ovos-stt-plugin-mms) | OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms). Warning: archived. MMS models also run under [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2), which is not on PyPI yet — install it from source, or use [onnx-asr](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr), which covers the same wav2vec2 families. | Apache-2.0 (model: see model card) | Deprecated |
| [ovos-stt-plugin-server](stt-plugins-reference.md#ovos-stt-server-plugin) | Companion plugin for an [OVOS STT Server](https://github.com/OpenVoiceOS/ovos-stt-http-server). Install name is `ovos-stt-plugin-server`; the repo is `ovos-stt-server-plugin` (words swapped). **Sends audio to public community servers unless you set `urls`** | Apache-2.0 | Stable |
| [ovos-stt-http-server](stt-plugins-reference.md#ovos-stt-http-server) | Turn any OVOS STT plugin into a micro service! | Apache-2.0 | Stable |
| [ovos-stt-plugin-whisper](stt-plugins-reference.md#ovos-stt-plugin-whisper) | OpenVoiceOS STT plugin for [Whisper](https://github.com/openai/whisper), using the transformers library | Apache-2.0 (code default model: `base`. Configure a larger model such as [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) for higher accuracy) | Beta |
| [ovos-stt-plugin-whispercpp](stt-plugins-reference.md#ovos-stt-plugin-whispercpp) | OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp) | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-fasterwhisper](stt-plugins-reference.md#ovos-stt-plugin-fasterwhisper) | OpenVoiceOS STT plugin for [Faster Whisper](https://github.com/guillaumekln/faster-whisper) | Apache-2.0 (code default model: `large-v3-turbo`) | Stable |
| [ovos-stt-plugin-nemo](stt-plugins-reference.md#ovos-stt-plugin-nemo) | OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended** | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-whisper-lm](stt-plugins-reference.md#ovos-stt-plugin-whisper-lm) | OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library. | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-citrinet](stt-plugins-reference.md#ovos-stt-plugin-citrinet) | OpenVoiceOS STT plugin | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-nos](stt-plugins-reference.md#ovos-stt-plugin-nos) | Galician STT using Proxecto Nós wav2vec2 models. Warning: archived, superseded by [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2), which is not on PyPI yet — install it from source, or use [onnx-asr](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr), which covers the same wav2vec2 families. | Apache-2.0 (model: see model card) | Deprecated |
| [ovos-stt-plugin-HiTZ](stt-plugins-reference.md#ovos-stt-plugin-hitz) | OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ). Warning: archived, deprecated. | see repo (no license file) | Deprecated |
| [ovos-stt-plugin-vosk](stt-plugins-reference.md#ovos-stt-plugin-vosk) | Mycroft STT plugin for [Vosk](https://alphacephei.com/vosk/) | Apache-2.0 (model: see model card) | Stable |
| [ovos-stt-plugin-onnx-asr](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr) | Runs [onnx-asr](https://github.com/istupakov/onnx-asr) models (NeMo Parakeet/Canary, Whisper, wav2vec2, …) fully offline via ONNX Runtime, a strong default for on-device, offline recognition. | Apache-2.0 (model: see model card) | Beta |

--8<-- "snippets/maturity-disclaimer.md"

!!! note "License and Maturity are independent axes"
    The **License** column reports what the repository itself declares. "No
    license file" just means no SPDX license was found, not that the code is unmature.
    The **Maturity** column reports repository health (age, activity, issues/PRs, docs).
    A plugin can be **Mature** and still ship no license file. A plugin can be **Stable**
    with a permissive license but thin docs. Don't read one column as implying the other.


## Choosing an ASR model family

The plugins above wrap a handful of model families with very different trade-offs. Each
entry links the architecture paper and a canonical model card, which is where the
authoritative detail on training data and per-language accuracy lives.

**Whisper** (plugins: whisper, whispercpp, fasterwhisper, whisper-lm; also via onnx-asr).
The broadest language coverage and the best robustness to accents and noise, because it
trains on 680k hours of weakly supervised web audio
([Radford et al. 2022](https://arxiv.org/abs/2212.04356)). The `large-v3` checkpoint adds
millions of pseudo-labeled hours
([model card](https://huggingface.co/openai/whisper-large-v3)). The same weak supervision
causes its signature failure: hallucinated phrases on silence, which is why the listener
ships a [hallucination filter](speech-service.md). It is chunk-based, not streaming, and
the large checkpoints are the heaviest option here. Prefer `large-v3-turbo` and int8
quantization on CPU.

**NVIDIA NeMo Conformer / Parakeet / Canary** (plugins: nemo, citrinet; also via
onnx-asr). Best accuracy-per-parameter and much lower latency inside their trained
language set ([Conformer](https://arxiv.org/abs/2005.08100),
[Fast Conformer](https://arxiv.org/abs/2305.05084)). Parakeet checkpoints are single
language and ignore `lang`
([parakeet-tdt-0.6b-v2 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2), ~120k
hours English). Canary is the multilingual branch
([canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2), ~1.7M hours across 25
European languages). [Citrinet](https://arxiv.org/abs/2104.01721) is the older CTC-only
sibling, kept for specific languages such as the Catalan default.

**wav2vec 2.0 / XLS-R / MMS** (plugins: wav2vec, mms, nos, HiTZ; also via onnx-asr).
Self-supervised pretraining plus a thin fine-tune
([Baevski et al. 2020](https://arxiv.org/abs/2006.11477)), which is why this family
dominates low-resource languages. [XLS-R](https://arxiv.org/abs/2111.09296) pretrains on
~500k hours across 128 languages, and [MMS](https://arxiv.org/abs/2305.13516) reaches
1,100+ languages with per-language adapters
([mms-1b-all card](https://huggingface.co/facebook/mms-1b-all)). Lighter than Whisper,
but per-language quality tracks how much fine-tuning data that language got.

**Vosk / Kaldi** (plugin: vosk). Classical HMM-hybrid decoding with ~50MB per-language
models ([project page](https://alphacephei.com/vosk/),
[repo](https://github.com/alphacep/vosk-api)). The lightest footprint and true streaming,
at clearly lower accuracy than the neural families. The right choice for constrained
hardware and the wrong one for noisy rooms.

## Learn more

Full technical detail per plugin (repository link, license notes, default configuration) lives on the [STT Plugins Reference](stt-plugins-reference.md) page linked from the table above. Writing a plugin instead of choosing one? See [Writing an STT Plugin](stt-plugin-development.md).

---
**Read next:** [TTS Plugins](tts-plugins.md)
**Related:** [STT Plugins Reference](stt-plugins-reference.md) · [Writing an STT Plugin](stt-plugin-development.md) · [Wake-word Plugins](wake-word-plugins.md) · [STT Server](stt-server.md) · [Choosing Plugins](choosing-plugins.md) · [Real-Time Offline Speech Recognition on OVOS (ONNX ASR)](https://blog.openvoiceos.org/posts/2026-02-16-onnx-asr)
