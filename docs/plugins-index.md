# Plugins Index

!!! abstract "In a nutshell"
    OpenVoiceOS is built from interchangeable building blocks called *plugins*: small add-ons that each handle one job, like turning speech into text or text into speech. This works much like browser extensions. You can mix and match the pieces you want and swap them out later. This page is a map of every plugin **type**, each linking to its catalog of available plugins. See the [Glossary](glossary.md) for related terms, or the [Plugin Manager](plugin-manager.md) for how they are discovered and loaded.

Every plugin registers under an **entry-point group** (the `opm.*` name below) so the
[Plugin Manager](plugin-manager.md) can find it. Pick a type to see the available plugins,
their config, and install commands.

!!! tip "Too many choices? Start with **[Choosing Plugins](choosing-plugins.md)**"
    A side-by-side comparison of every plugin type: the recommended default, each option's
    maturity, offline/cloud, and licence, plus a copy-paste fully-offline stack and
    scenario-based picks. This page is the *map of types*. That page helps you *pick one*.

## Which plugin type do I need?

- I want to hear the assistant on speakers or a headset → [Microphone](mic-plugins.md) is the
  input side; for the output voice see [TTS](tts-plugins.md).
- I want it to stop listening to background noise → [VAD](vad-plugins.md).
- I want to change the activation phrase or engine → [Wake Word](wake-word-plugins.md).
- I want fewer false wake-ups → [Wake Word Verifiers](ww-verifier.md).
- I want more accurate transcription → [STT](stt-plugins.md).
- I want a different voice → [TTS](tts-plugins.md).
- I want mouth/viseme animation on a Mark 1-style face → [G2P](g2p-plugins.md).
- I want the assistant to detect or translate another language → [Translation & Language
  Detection](translation-plugins.md).
- I want to clean up or correct recognized text before intent matching → [Utterance
  Transformers](utterance-transformers.md).
- I want to change how utterances get routed to skills → [Pipeline matchers](pipelines-overview.md).
- I want to hook into the text/metadata/dialog/TTS stages → [Transformers](transformer-plugins.md).
- I want "play X" to find YouTube, a podcast, or a playlist → [OCP Stream
  Extractors](ocp-plugins.md).
- I want media requests recognized by intent (artist, title, station) → [OCP Media
  Classifiers](media-plugins.md#ovos-media-classifier).
- I want the actual audio/video to play → [Media Playback](media-plugins.md).
- I want a custom GUI render backend → [GUI Adapters](gui-adapters.md) (unreleased).
- I want an LLM answering when no skill matches → [Agent Engines](agent-plugins.md) and
  [Personas](personas.md).
- I want the assistant to remember earlier turns → [Persona Memory](persona-memory.md).
- I want an agent to call external functions (weather, search, …) → [Agent
  Tools](tool-plugins.md).
- I want hardware or platform integration (LEDs, buttons, displays) → [PHAL](phal.md).

## Speech & Audio

!!! tip "Recommended offline defaults"
    For a fully offline, on-device speech stack: TTS → [phoonnx](tts-plugins.md) · STT →
    [onnx-asr](stt-plugins.md) · VAD → [silero](vad-plugins.md) · Wake word →
    [precise-onnx](wake-word-plugins.md) (or [openWakeWord](wake-word-plugins.md) as a
    strong alternative). Each linked page explains the reasoning and lists the cloud
    alternatives that are a fair choice when local compute or coverage needs push you
    that way.

| Type | Entry point | What it does |
|---|---|---|
| [Microphone](mic-plugins.md) | `opm.microphone` | Captures audio from a microphone or audio source |
| [VAD](vad-plugins.md) (Voice Activity Detection) | `opm.VAD` | Detects when speech starts and stops |
| [Wake Word](wake-word-plugins.md) | `opm.wake_word` | Listens for the activation phrase (e.g. "hey Mycroft") |
| [Wake Word Verifiers](ww-verifier.md) | `opm.wake_word.verifier` | Second-stage check to reject false wake-word triggers |
| [STT](stt-plugins.md) (Speech-to-Text) | `opm.stt` | Transcribes captured speech into text |
| [TTS](tts-plugins.md) (Text-to-Speech) | `opm.tts` | Turns reply text back into spoken audio |
| [G2P](g2p-plugins.md) (Grapheme-to-Phoneme) | `opm.g2p` | Converts text to phonemes (e.g. for mouth/visemes) |

## Language

| Type | Entry point | What it does |
|---|---|---|
| [Translation & Language Detection](translation-plugins.md) | `opm.lang.translate` / `opm.lang.detect` | Detect a text's language and translate between languages |
| [Utterance Transformers](utterance-transformers.md) | `opm.transformer.text` | Modify the recognized text before intent matching |

## Intent & Dialog Pipeline

| Type | Entry point | What it does |
|---|---|---|
| [Pipeline matchers](pipelines-overview.md) | `opm.pipeline` | Decide which skill handles an utterance (Adapt, Padatious, …) |
| [Transformers](transformer-plugins.md) | `opm.transformer.*` | Hook into the text / metadata / dialog / TTS stages |

## Media & GUI

| Type | Entry point | What it does |
|---|---|---|
| [OCP Stream Extractors](ocp-plugins.md) | `opm.ocp.extractor` | Resolve a playable stream from a URL (YouTube, RSS, …) |
| [OCP Media Classifiers](media-plugins.md#ovos-media-classifier) | none yet **(experimental)** | Recognize media intent + entities (artist, title, station, …) in an utterance. Not yet built or released as an OPM entry-point group. See the [Media Playback](media-plugins.md#ovos-media-classifier) page. |
| [Media Playback](media-plugins.md) | `opm.media.audio` / `.video` / `.web` | Backend players for [ovos-media](ovos-media.md) |
| [GUI Adapters](gui-adapters.md) | `opm.gui_adapter` **(unreleased)** | Render backends for the GUI. Not yet built or released. See the [GUI Adapters](gui-adapters.md) page. |

## AI Agents & Personas

| Type | Entry point | What it does |
|---|---|---|
| [Agent Engines](agent-plugins.md) | `opm.agents.*` | Chat / retrieval / summarizer / reranker brains |
| [Persona Memory](persona-memory.md) | `opm.agents.memory` | What a persona remembers between turns |
| [Agent Tools](tool-plugins.md) | `opm.agents.toolbox` | Give an agent callable tools |
| [Personas](personas.md) | `opm.plugin.persona` | Bundle engines into a conversational identity |

## System & Hardware

| Type | Entry point | What it does |
|---|---|---|
| [PHAL](phal.md) (Platform/Hardware Abstraction Layer) | `opm.phal` | Hardware and platform integrations |

## Other plugin types

These plugin types are defined by the Plugin Manager but don't yet have a dedicated catalog
page here. See [Plugin Manager → Plugin Types](plugin-manager.md#plugin-types) for their
entry-point group and template base class:

- **Voice Clone** (`opm.vc`): clones a voice for TTS synthesis
- **Audio→IPA** (`opm.audio2ipa`): transcribes audio directly to phonemes (IPA)
- **Embeddings** (`opm.embeddings`, plus `opm.embeddings.text` / `.voice` / `.image` / `.face`):
  generic and modality-specific embedding backends
- **Knowledge Triples** (`opm.triples`): extracts subject-predicate-object triples from text

For the full machine-readable list of plugin types and template base classes, see the
**[Plugin Manager → Plugin Types](plugin-manager.md#plugin-types)** table. To create your own
plugin, each catalog page above includes a template and entry-point example.

---
**Read next:** [Choosing Plugins](choosing-plugins.md)
**Related:** [Plugin Arena](plugin-arena.md) · [Plugin Manager](plugin-manager.md) · [Maturity Scale](maturity.md) · [Glossary](glossary.md)
