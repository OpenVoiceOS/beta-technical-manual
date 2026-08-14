# STT Plugins Reference

!!! abstract "In a nutshell"
    This page holds the full technical entry for each STT plugin in the roster: repository link, license notes, and a default configuration snippet where one exists. Start at [STT Plugins](stt-plugins.md) to pick a plugin; come here for the exact settings.

## ovos-stt-plugin-wav2vec

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-wav2vec](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec) (aliased by
  [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2). A
  separate GitHub repo that installs the same package and module id, `ovos-stt-plugin-wav2vec`.
  the repo name differs but the entry point does not, so both resolve to the same plugin)


- **Description**: OVOS plugin for [Wav2Vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-wav2vec",
    "ovos-stt-plugin-wav2vec": {
        "model": "proxectonos/Nos_ASR-wav2vec2-large-xlsr-53-gl-with-lm"
    }
  }

```

There is no single hardcoded default model: the plugin picks a model from an internal
per-language table (keyed by BCP-47 language code) unless `model` is set explicitly, and
raises an error if the configured `lang` has no entry and no `model` is given. The
`proxectonos/Nos_ASR-...` model above is only the entry for Galician (`gl`). Other
languages resolve to different pretrained models.

---

## ovos-stt-plugin-azure

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-azure](https://github.com/OpenVoiceOS/ovos-stt-plugin-azure)


- **Description**: Microsoft Azure cloud speech-to-text.

---

## ovos-stt-plugin-chromium

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-chromium](https://github.com/OpenVoiceOS/ovos-stt-plugin-chromium)


- **Description**: Speech-to-text using the Google Chrome browser speech API.

!!! note
    This plugin talks to the same unofficial, undocumented endpoint used by the Chrome
    browser's speech recognition feature. It is not a published Google Cloud Speech-to-Text
    API with an API key. Google can change or revoke access to this endpoint at any time.

---

## ovos-stt-plugin-mms

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms)


- **Description**: OVOS plugin for [The Massively Multilingual Speech (MMS) project](https://huggingface.co/docs/transformers/main/en/model_doc/mms). Warning: archived. MMS models also run under [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2), which is not on PyPI yet — install it from source, or use [onnx-asr](#ovos-stt-plugin-onnx-asr), which covers the same wav2vec2 families.

### Default Configuration

```jsonc
"stt": {
    "module": "ovos-stt-plugin-mms",
    "ovos-stt-plugin-mms": {
      "model": "facebook/mms-1b-all"
    }
}

```

---

## ovos-stt-server-plugin

- **GitHub**: [OpenVoiceOS/ovos-stt-server-plugin](https://github.com/OpenVoiceOS/ovos-stt-server-plugin)


- **Description**: OpenVoiceOS companion plugin for [OpenVoiceOS STT Server](https://github.com/OpenVoiceOS/ovos-stt-http-server)

!!! warning "Talks to a public community server by default"
    Leaving `urls` unset falls back to a best-effort, publicly-run community STT server, not
    a private or guaranteed-available endpoint. Point it at your own self-hosted server (see
    [stt-server](stt-server.md#companion-plugin)) if you need privacy or reliability.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["https://0.0.0.0:8080/stt"],
      "verify_ssl": true
    },
 }

```

Leaving `urls` unset falls back to public community-run STT servers rather than failing. See
[stt-server](stt-server.md#companion-plugin) for a self-hosted alternative, or pick a fully
offline engine from the table above.

--8<-- "snippets/community-servers.md"

---

## ovos-stt-http-server

- **GitHub**: [OpenVoiceOS/ovos-stt-http-server](https://github.com/OpenVoiceOS/ovos-stt-http-server)


- **Description**: Turn any OVOS STT plugin into a micro service!

---

## ovos-stt-plugin-whisper

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-whisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper)


- **Description**: OpenVoiceOS STT plugin for [Whisper](https://github.com/guillaumekln/faster-whisper), using transformers library

### Recommended Configuration

Defaults when unset: `model` is `openai/whisper-large-v3-turbo` and `use_cuda` is off (CPU).

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whisper",
    "ovos-stt-plugin-whisper": {
        "model": "openai/whisper-large-v3-turbo",
        "use_cuda": true
    }
  }

```

---

## ovos-stt-plugin-whispercpp

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-whispercpp](https://github.com/OpenVoiceOS/ovos-stt-plugin-whispercpp)


- **Description**: OpenVoiceOS STT plugin for [whispercpp](https://github.com/ggerganov/whisper.cpp)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whispercpp",
    "ovos-stt-plugin-whispercpp": {
        "model": "base"
    }
  }
 

```

---

## ovos-stt-plugin-fasterwhisper

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper)


- **Description**: OpenVoiceOS STT plugin for [Faster Whisper](https://github.com/guillaumekln/faster-whisper)

CTranslate2 also supports `int8` / `int8_float16` compute types for lower-RAM CPU deployments. Change `compute_type` to use them.

### Recommended Configuration

Defaults when unset: `model` is `large-v3-turbo`, `compute_type` is `int8`, and `use_cuda`
is `false`.

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-fasterwhisper",
    "ovos-stt-plugin-fasterwhisper": {
        "model": "large-v3-turbo",
        "use_cuda": true,
        "compute_type": "float16",
        "beam_size": 5,
        "cpu_threads": 4
    }
  }

```

---

## ovos-stt-plugin-nemo

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-nemo](https://github.com/OpenVoiceOS/ovos-stt-plugin-nemo)


- **Description**: OpenVoiceOS STT plugin for [Nemo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html), GPU is **strongly recommended**

CPU is the shipped default (`use_cuda: false`). Set `use_cuda: true` for acceptable throughput on supported GPUs. The GPU recommendation is about speed, not a required default.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-nemo",
    "ovos-stt-plugin-nemo": {
        "model": "stt_eu_conformer_ctc_large",
        "use_cuda": false
    }
  }

```

---

## ovos-stt-plugin-whisper-lm

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-whisper-lm](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-lm)


- **Description**: OpenVoiceOS STT plugin for [Whisper-LM-transformers](https://github.com/hitz-zentroa/whisper-lm-transformers), KenLM and Large language model integration with Whisper ASR models implemented in Hugging Face library.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-whisper-lm",
    "ovos-stt-plugin-whisper-lm": {
        "model": "zuazo/whisper-medium-eu",
        "lm_repo": "HiTZ/whisper-lm-ngrams",
        "lm_model": "5gram-eu.bin",
        "lm_alpha": 0.33582369,
        "lm_beta": 0.68825565,
        "use_cuda": true
    }
  }

```

---

## ovos-stt-plugin-citrinet

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-citrinet](https://github.com/OpenVoiceOS/ovos-stt-plugin-citrinet)


- **Description**: OpenVoiceOS STT plugin

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-citrinet",
    "ovos-stt-plugin-citrinet": {
      "lang": "ca"
    }
  }

```

---

## ovos-stt-plugin-nos

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos)


- **Description**: Galician STT using [Proxecto Nós](https://github.com/proxectonos) wav2vec2 models. Warning: archived. Superseded by [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2).

### Default Configuration

```jsonc
"stt": {
    "module": "ovos-stt-plugin-nos"
}

```

---

## ovos-stt-plugin-HiTZ

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ)


- **Description**: OpenVoiceOS STT plugin for **Basque** models trained by [HiTZ](https://huggingface.co/HiTZ). Warning: archived, deprecated.

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-HiTZ",
    "ovos-stt-plugin-HiTZ": {
        "model": "stt_eu_conformer_transducer_large"
    }
  }

```

---

## ovos-stt-plugin-vosk

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-vosk](https://github.com/OpenVoiceOS/ovos-stt-plugin-vosk)


- **Description**: Mycroft STT plugin for [Vosk](https://alphacephei.com/vosk/)

### Default Configuration

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "ovos-stt-plugin-vosk": {
        "model": "/path/to/unzipped/model/folder"
    }
  }
 

```

---

## ovos-stt-plugin-onnx-asr

- **GitHub**: [OpenVoiceOS/ovos-stt-plugin-onnx-asr](https://github.com/OpenVoiceOS/ovos-stt-plugin-onnx-asr)


- **Description**: Runs [onnx-asr](https://github.com/istupakov/onnx-asr) models via ONNX Runtime with no PyTorch/transformers dependency. Inference is fully offline. Models are downloaded from Hugging Face on first load, so it runs offline **after the model has been fetched once** (there is currently no plugin-level option to pin a purely-local model directory). Supports NeMo Parakeet and Canary, Whisper, and wav2vec2 model families.

### Recommended Configuration

If `model` is omitted, the plugin loads its **built-in default `nemo-canary-1b-v2`**, a ~1B-parameter model with strong accuracy but a heavier footprint. For typical offline devices we recommend setting the lighter `nemo-parakeet-tdt-0.6b-v3` explicitly:

```jsonc
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr",
    "ovos-stt-plugin-onnx-asr": {
        "model": "nemo-parakeet-tdt-0.6b-v3"
    }
  }

```

| Config key | Default | Effect |
|---|---|---|
| `model` | `nemo-canary-1b-v2` | Built-in alias or any Hugging Face ONNX ASR repo id |
| `quantization` | unset | Set `"int8"` to load int8 weights where a model ships them (smaller/faster) |
| `use_cuda` | `false` | Select the CUDA execution provider (with a CPU fallback) |
| `providers` | unset | Explicit list of onnxruntime execution providers, takes precedence over `use_cuda` |

!!! note "Language handling is model-family-gated"
    The configured/utterance language is only passed to the ASR call for **Whisper** and **Canary** (NeMo Conformer AED) families. Other families (Parakeet, GigaAM, Vosk, wav2vec2, T-one) ignore `lang`. For those, pick a language-specific model instead of relying on a `lang` setting to steer a multilingual one.

Besides the built-in aliases and the `onnx-asr` repository's own model hub, the plugin loads any repo id from the [OpenVoiceOS/stt-asr-onnx](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx) collection. This collection holds curated single-language and regional ONNX conversions of NeMo Conformer/Parakeet and Whisper checkpoints, grouped roughly by family: AI4Bharat/Vaani models for Indian languages, NVIDIA Conformer/Parakeet models for major European languages (plus Kabyle, Belarusian, Esperanto, Kinyarwanda), Iberian-language Conformer models, and per-language Whisper finetunes. Most ship both fp32 and int8 weights (`quantization: "int8"` works). A few large models are fp32-only. See the collection itself for the exhaustive, current list. It grows independently of this plugin's release cycle.


---

---
**Read next:** [STT Plugins](stt-plugins.md)
**Related:** [Writing an STT Plugin](stt-plugin-development.md) · [Wake-word Plugins](wake-word-plugins.md) · [STT Server](stt-server.md)
