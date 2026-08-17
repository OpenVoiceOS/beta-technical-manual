# Choosing Plugins — Comparison & Recommendations

!!! abstract "In a nutshell"
    OVOS ships **dozens** of interchangeable plugins for each job. That's useful, but
    it's easy to feel lost picking one. This page is the shortcut: for every plugin type
    it names a **recommended default**, then a small **comparison table** so you can see at
    a glance which option fits your situation (offline vs cloud, hardware budget, licence,
    maturity). Want the full config and every option? Each section links to its detailed
    catalog. New here? Start with the [Plugins Index](plugins-index.md).

!!! tip "Don't want to choose? Use the recommended offline stack"
    Every ⭐ below is a sensible, **fully-offline, on-device** default. It forms a complete
    private stack: no cloud, no account. First install them:

    ```bash
    pip install ovos-microphone-plugin-alsa ovos-vad-plugin-silero \
                ovos-stt-plugin-onnx-asr phoonnx
    ```

    then drop this into `~/.config/mycroft/mycroft.conf`:

    ```json
    {
      "listener": {
        "microphone": { "module": "ovos-microphone-plugin-alsa" },
        "VAD": { "module": "ovos-vad-plugin-silero" }
      },
      "stt": { "module": "ovos-stt-plugin-onnx-asr" },
      "tts": { "module": "ovos-tts-plugin-phoonnx" }
    }
    ```

    The wake word is **not** in the snippet because it already defaults to **precise-onnx**
    (`hey_mycroft`). See [Wake word](#wake-word) to change the phrase. Prefer one command?
    `ovos-config autoconfigure -l en-us --offline` writes the language + these defaults for
    you (it needs `ovos-config` already installed, and configures rather than installs plugins).

**In a hurry with a specific constraint** (low-power Pi, GPU accuracy, thin satellite, cloud
OK)? Jump straight to **[Pick by scenario](#pick-by-scenario)**.

**How to read the tables.** ⭐ marks the recommended default. **Maturity** rates
[repository health](maturity.md) (Proof-of-concept → Alpha → Beta → Stable → Mature), *not* how good the
plugin is. A Beta default can be the right pick. **Offline** means it runs on-device with
no network. **Online** calls a cloud service (separate terms). **Hybrid** talks to a server
you can self-host. Pick the row whose *"choose this if"* matches you, then open the catalog
page for its config.

---

## Speech input

### Microphone

Captures audio. See the [Microphone catalog](mic-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-microphone-plugin-alsa** | Stable | offline | Linux/ALSA hardware — lowest latency, best performance |
| ovos-microphone-plugin-sounddevice | Stable | offline | Cross-platform (Linux/macOS/Windows) capture |
| ovos-microphone-plugin-pyaudio | Beta | offline | You want PortAudio bindings directly, no `speech_recognition` dep |
| ovos-microphone-plugin-files | Stable | offline | Automated testing — feed audio files instead of a live mic |

### VAD (Voice Activity Detection)

Detects when speech starts/stops. See the [VAD catalog](vad-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-vad-plugin-silero** | Stable | offline | Best accuracy, esp. in noise; small neural model ships in the package (16 kHz) |
| ovos-vad-plugin-webrtcvad | Stable | offline | Lighter CPU-only fallback with tunable aggressiveness |
| ovos-vad-plugin-noise | Stable | offline | Lightest possible — energy threshold, no model at all |

### Wake word

Listens for the activation phrase. See the [Wake word catalog](wake-word-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-ww-plugin-precise-onnx** | Beta | offline | The default `hey_mycroft` engine — accurate, lightweight always-on ONNX |
| ovos-ww-plugin-openWakeWord | Stable | offline | Better accuracy than Vosk from open pre-trained models, no training |
| ovos-ww-plugin-vosk | Stable | offline | Fastest setup for an arbitrary phrase, no model training (good for dev) |
| ovos-ww-plugin-wakewordlab | Alpha | offline | Very compact (~240 KB) models with a Silero pre-filter (install from source) |
| ovos-ww-plugin-wakeforge | Alpha | offline | Train a custom detector from a single phrase |
| ovos-ww-plugin-server | Alpha | hybrid | Thin satellite offloading detection to a self-hosted ww-server. **Not available yet** — repos still private |

*`ovos-ww-plugin-precise-lite` is **deprecated**. It is the TFLite predecessor of precise-onnx,
kept working as a fallback but not a pick for new setups.*

### STT (Speech-to-Text)

Transcribes speech to text. See the [STT catalog](stt-plugins.md) (16 plugins, top picks shown).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-stt-plugin-onnx-asr** | Beta | offline | Recommended default: ONNX Runtime, no PyTorch, int8 weights for low-RAM devices |
| ovos-stt-plugin-fasterwhisper | Stable | offline | Whisper accuracy via CTranslate2 int8/float16, CPU or GPU |
| ovos-stt-plugin-whispercpp | Stable | offline | Lightweight Whisper via whisper.cpp (tiny/small models) on modest CPUs |
| ovos-stt-plugin-nemo | Stable | offline | NVIDIA NeMo Conformer models, GPU strongly recommended |
| ovos-stt-plugin-vosk | Stable | offline | Long-established lightweight engine from a local model folder |
| ovos-stt-plugin-server | Stable | hybrid | Offload STT to an OVOS STT server. **Set `urls`** — unset, it sends audio to public community servers |
| ovos-stt-plugin-azure | Stable | online | No on-device compute budget; accept cloud STT (Microsoft terms) |

---

## Speech output

### TTS (Text-to-Speech)

Turns replies into speech. See the [TTS catalog](tts-plugins.md) (20 plugins, top picks shown).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-tts-plugin-phoonnx** | Stable | offline | Recommended default: small multilingual ONNX voices, auto model fetch |
| ovos-tts-plugin-coqui | Stable | offline | Higher-quality neural synthesis, heavier local compute |
| ovos-tts-plugin-espeakNG | Mature | offline | Very broad language coverage, tiny footprint, robotic voice |
| ovos-tts-plugin-pico | Mature | offline | Lightest possible offline voice on constrained hardware |
| ovos-tts-plugin-server | Mature | hybrid | Offload synthesis to an OVOS/Piper server. **Set `host`** — unset, it uses public community servers |
| ovos-tts-plugin-edge-tts | Stable | online | Free high-quality Microsoft Edge cloud voices, no subscription |
| ovos-tts-plugin-polly | Mature | online | A specific commercial cloud voice (Amazon Polly) |

!!! note "Licence watch"
    Most speech plugins are Apache-2.0, but a few differ. For example, **espeakNG is
    GPL-3.0**, and cloud engines (Azure, Polly, and others) add the vendor's separate terms.
    The catalog pages carry the exact licence per plugin.

### G2P (Grapheme-to-Phoneme)

Converts text to phonemes to drive **mouth-movement / viseme animation** (e.g. a Mark 1
face). This is an **alpha-quality, Mark 1-era** capability. Most TTS voices don't emit phoneme timing,
so a G2P plugin *estimates* it from the text. Only **Mimic 1** provides phoneme timing
natively. For any other voice the G2P plugin simulates the timing. **If you don't drive a
mouth/face, you don't need a G2P plugin at all.** See the [G2P catalog](g2p-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-tts-plugin-mimic** | Beta | offline | The PyPI-published default — ships the `ovos-g2p-plugin-mimic` entry point, ARPA phonemes via the Mimic 1 engine |

---

## Language

### Translation & Language Detection

Detect a text's language and translate. See the [Translation catalog](translation-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-translate-plugin-nllb** | Stable | offline | Recommended offline translation (NLLB-200 via CTranslate2) |
| ⭐ **ovos-lang-detector-fasttext-plugin** | Stable | offline | Recommended offline detection, pairs with NLLB |
| ovos-lang-detector-classics-plugin | Stable | offline | Offline detection voting across classic detectors |
| ovos-translate-server-plugin | Stable | hybrid | Self-/community-hosted translate server with public failover (talks to an `ovos-translate-server` instance) |
| ovos-google-translate-plugin | Stable | online | Free cloud translate+detect when coverage beats keeping text local |

---

## Media playback

Backend players for [ovos-media](ovos-media.md). See the [Media catalog](media-plugins.md).
Note: the `ovos-media` service itself is alpha and not officially released. Stock installs
play audio through `ovos-audio` (`enable_old_audioservice: true`, the default), so these
backends only apply once you opt in to `ovos-media`. The maturity column below rates each
backend plugin, not the service.

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-media-plugin-mpv** | Stable | offline | General-purpose local audio+video; works on both media backends |
| ovos-media-plugin-mplayer | Stable | offline | MPlayer as the local audio+video backend |
| ovos-media-plugin-ffplay | Stable | offline | Lightweight ffplay audio-only playback |
| ovos-media-plugin-vlc | Beta | offline | Headless VLC audio+video, ovos-media-ready package |
| ovos-media-plugin-spotify | Stable | online | Spotify Connect streaming |
| ovos-media-plugin-chromecast | Stable | online | Cast audio+video to a Chromecast on the network |

---

## Media & OCP

### OCP Stream Extractors

Turn a URL or search request into a playable stream for [OCP](ocp-plugins.md). See the
[OCP catalog](ocp-plugins.md) for the full descriptions. None of the entries there state a
maturity rating.

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-ocp-youtube-plugin** | not rated | online | Recommended default: resolves the most common "play X" request, YouTube/YouTube Music |
| ovos-ocp-files-plugin | not rated | offline | Playing local files (`file://` URIs), always available, no network |
| ovos-ocp-rss-plugin | not rated | online | Podcast/RSS feeds, always plays the newest episode |
| ovos-ocp-bandcamp-plugin | not rated | online | Bandcamp pages |
| ovos-ocp-news-plugin | not rated | online | A known spoken-news provider URL |
| ovos-ocp-m3u-plugin | not rated | online | Resolving a `.m3u`/`.pls` playlist URL |
| ovos-media-classifier | not rated | offline | Experimental: routes a request to the right `MediaProvider` by intent, not yet deployed |

---

## Embeddings stores

Backends for `EmbeddingsDB`, the vector store an [agent engine](agent-plugins.md) uses for
retrieval or memory. See the [Agent Plugins catalog](agent-plugins.md). None of the entries
there state a maturity rating.

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-chromadb-embeddings-plugin** | not rated | offline | Recommended default: local persistent client, no separate server to run |
| ovos-qdrant-embeddings-plugin | not rated | hybrid | Scaling to a self-hosted Qdrant server for a larger vector store |
| ovos-gguf-embeddings-plugin | not rated | offline | Already running [ovos-gguf-plugin](gguf-plugin.md), reuse it for text embeddings too, no extra service |

---

## AI Agents & LLM Chat Backends

The "brain" behind a [persona](personas.md): a chat engine answers when no skill handles the
utterance. See [Agent Plugins](agent-plugins.md), [OpenAI Plugin](openai-plugin.md), [GGUF
Plugin](gguf-plugin.md), and [Personas](personas.md) for the full catalogs and config. None of
those pages state a maturity rating for these plugins.

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-gguf-plugin** | not rated | offline | Recommended default: fully local GGUF model via `llama-cpp-python`, no account, no network, private |
| ovos-openai-plugin | not rated | online | Pointing at OpenAI or any OpenAI-compatible endpoint (cloud, Ollama, vLLM, LocalAI, `ovos-persona-server`) |
| ovos-messagebus-chat-plugin | not rated | offline | Answering through the existing skills/intent stack instead of an LLM |
| ovos-solver-rivescript-plugin / ovos-solver-aiml-plugin | not rated | offline | A lightweight scripted chatbot, no model weights at all. The repos put the words in a different order (`ovos-solver-plugin-rivescript`, `ovos-solver-plugin-aiml`), but the package and handler names are the ones shown here |
| ovos-wikipedia-plugin | not rated | online | Factual questions answered from Wikipedia |
| ovos-wolfram-alpha-plugin | not rated | online | Computational/factual questions (math, unit conversion, …) |
| ovos-ddg-plugin | not rated | online | General web-search-style answers via DuckDuckGo |

!!! note "Privacy of the demo persona"
    `ovos-openai-plugin` ships a `Remote Llama` demo persona pointed at a public third-party
    server. For privacy, point `api_url` at your own server, or use `ovos-gguf-plugin` instead.

---

## Text & audio transformers

Hook into the text / audio / dialog / TTS stages. See the [Transformers catalog](transformer-plugins.md).

| Plugin | Maturity | Runs | Choose this if |
|---|---|---|---|
| ⭐ **ovos-utterance-normalizer** | Stable | offline | Standard utterance cleanup before intent parsing (the default) |
| ovos-utterance-corrections-plugin | Stable | offline | Correct STT outputs for better intent matching |
| ovos-utterance-plugin-cancel | Stable | offline | Cancel an utterance ending in "nevermind that" |
| ovos-dialog-normalizer-plugin | Stable | offline | Normalize dialog text before TTS |
| ovos-bidirectional-translation-plugin | Stable | hybrid | Understand + speak in *any* language via paired transformers |
| ovos-audio-transformer-plugin-ggwave | Mature | offline | Data-over-sound encode/decode on the audio path |

---

## Pick by scenario

- **Fully offline / private (Raspberry Pi or mini-PC):** the ⭐ stack: alsa mic, silero VAD,
  precise-onnx wake word, onnx-asr STT, phoonnx TTS. Everything runs on-device.
- **Lowest-power / tiny device:** swap TTS to **pico** or **espeakNG**, VAD to **webrtcvad**,
  STT to **vosk** (small model). Accept lower accuracy for a smaller footprint.
- **Best accuracy, GPU available:** STT **fasterwhisper** with `use_cuda: true` — what
  `ovos-config autoconfigure --gpu` configures for the languages that have a GPU
  recommendation, using `whisper-large-v3-turbo` where no dedicated finetune exists for the
  language (see [Language Support Tables](lang-support-tables.md)) — or **nemo**. TTS **coqui**. Still fully
  offline.
- **Thin satellite / shared backend:** offload with the `*-server` plugins so the heavy models
  live on one machine. STT and TTS are available today (`ovos-stt-plugin-server`,
  `ovos-tts-plugin-server` — set `urls`/`host`, or they use public community servers); the
  wake-word one is not released yet, so keep wake-word detection on the satellite.
- **Cloud is acceptable (coverage/quality first):** STT **azure**, TTS **edge-tts**/**polly**,
  translation **google**. Each adds the vendor's separate terms.

Maturity here is a **repository-health** signal, not a quality score. See the
[Maturity scale](maturity.md). For discovery/loading internals see the
[Plugin Manager](plugin-manager.md). For head-to-head benchmark data see the
[Plugin Arena](plugin-arena.md).

---
**Read next:** [Plugin Arena](plugin-arena.md) · [Microphone Plugins](mic-plugins.md)
**Related:** [Plugins Index](plugins-index.md) · [Maturity Scale](maturity.md) · [Plugin Manager](plugin-manager.md)
