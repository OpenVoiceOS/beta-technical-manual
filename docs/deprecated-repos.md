# Deprecated & Archived Repositories

!!! abstract "In a nutshell"
    A reference list of retired OVOS code projects, together with what replaced each one. If you run into a retired package name or an out-of-date guide online, look it up here, see that it is retired, and find the replacement. You do not need to read it top to bottom: treat it as a lookup table. See the [Glossary](glossary.md) for terms.

Looking for an answer to a skill-development question instead? Start at
[Your First Skill](first-skill.md) or the [Developer FAQ](skill-dev-faq.md). The list below covers only
retired repositories, not how to write skills.

!!! warning "These repositories are archived"
    The repositories below are **archived** in the [OpenVoiceOS GitHub organization](https://github.com/OpenVoiceOS). They are read-only and not maintained. Use the list to recognize them and find the replacement. Do **not** start new work against them.

The list covers **repo-level** deprecations (an entire repository retired). For
**entry-point-level** deprecations, an old OPM entry point group renamed to a
canonical one while the plugin itself keeps working, see
[Plugin Types Reference: Deprecated Types](plugin-types-reference.md#deprecated-types).

To list every archived repository, run `gh repo list OpenVoiceOS --archived --limit 400`. The repositories are grouped by area below. Each row gives the reason and the current replacement where one exists.


## Backend services (removed architecture) (5)

*OVOS uses no central backend. These are removed, not replaced.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-backend-client](https://github.com/OpenVoiceOS/ovos-backend-client) | client library for interaction with all compatible ovos-core backend services | Removed: OVOS is backendless |
| [ovos-backend-manager](https://github.com/OpenVoiceOS/ovos-backend-manager) | A simple web UI for personal backend, powered by PyWebIO | Removed: OVOS is backendless |
| [ovos-binary-shop](https://github.com/OpenVoiceOS/ovos-binary-shop) | Wheels and pre-compiled binaries for usage with ovos plugins / images | Removed: wheels are published on PyPI |
| [ovos-personal-backend](https://github.com/OpenVoiceOS/ovos-personal-backend) | personal backend - self-hosted backend to manage multiple OVOS devices | Removed: OVOS is backendless |
| [ovos-stt-plugin-selene](https://github.com/OpenVoiceOS/ovos-stt-plugin-selene) | STT plugin to use selene backend services | Removed: OVOS is backendless |

## Skills (renamed, or folded into pipelines/services) (22)

*Archived skills. Most Mycroft-era skills were renamed `skill-ovos-*` → `ovos-skill-*` or folded into core pipelines. The media skills were replaced by the `ovos-media-provider-*` plugins.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-skill-fallback-chatgpt](https://github.com/OpenVoiceOS/ovos-skill-fallback-chatgpt) | Fallback skill that answered unhandled utterances with ChatGPT | [ovos-persona](https://github.com/OpenVoiceOS/ovos-persona) |
| [ovos-skills](https://github.com/OpenVoiceOS/ovos-skills) | ovos-core metapackage for skills daemon | ovos-core (skills run in-process) |
| [skill-homescreen-lite](https://github.com/OpenVoiceOS/skill-homescreen-lite) | Minimal homescreen for remote client devices | [ovos-skill-homescreen](https://github.com/OpenVoiceOS/ovos-skill-homescreen) |
| [skill-ovos-alarm](https://github.com/OpenVoiceOS/skill-ovos-alarm) | Mycroft AI Alarm Skill - Set single and recurring alarms, with a choice of alarm sounds | [ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| [skill-ovos-common-play](https://github.com/OpenVoiceOS/skill-ovos-common-play) | Mycroft AI official Playback Control Skill - providing Intents for other Skills to use common playback functionality (via Common Play) | OCP pipeline (ovos-ocp-pipeline-plugin) |
| [skill-ovos-common-query](https://github.com/OpenVoiceOS/skill-ovos-common-query) | Skill Negotiating for the best source for an answer via Common QA | [ovos-common-query-pipeline-plugin](https://github.com/OpenVoiceOS/ovos-common-query-pipeline-plugin) |
| [skill-ovos-mycroftgui](https://github.com/OpenVoiceOS/skill-ovos-mycroftgui) | Mycroft skill to take control of the Mycroft GUI QT application. | GUI rework (ovos-gui) |
| [skill-ovos-settings](https://github.com/OpenVoiceOS/skill-ovos-settings) | Mycroft skill to take control of OpenVoiceOS it's functions and tools. | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [skill-ovos-setup](https://github.com/OpenVoiceOS/skill-ovos-setup) | OpenVoiceOS Setup Skill - configure your device and optionally connect it to a backend server | Removed, OVOS is backendless. Onboarding is via ovos-installer |
| [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop) | stop whatever the assistant is doing | Stop pipeline (ovos-stop-pipeline-plugin) |
| [skill-ovos-timer](https://github.com/OpenVoiceOS/skill-ovos-timer) | Timer Skill | [ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| [ovos-skill-bandcamp](https://github.com/OpenVoiceOS/ovos-skill-bandcamp) | OCP media skill | MediaProvider plugin [ovos-media-provider-bandcamp](https://github.com/OpenVoiceOS/ovos-media-provider-bandcamp), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-local-media](https://github.com/OpenVoiceOS/ovos-skill-local-media) | OCP media skill | MediaProvider plugin [ovos-media-provider-local](https://github.com/OpenVoiceOS/ovos-media-provider-local), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-music-assistant](https://github.com/OpenVoiceOS/ovos-skill-music-assistant) | OCP media skill | MediaProvider plugin [ovos-media-provider-mass](https://github.com/OpenVoiceOS/ovos-media-provider-mass), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-news](https://github.com/OpenVoiceOS/ovos-skill-news) | OCP media skill | MediaProvider plugin [ovos-media-provider-news](https://github.com/OpenVoiceOS/ovos-media-provider-news), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-pyradios](https://github.com/OpenVoiceOS/ovos-skill-pyradios) | OCP media skill | MediaProvider plugin [ovos-media-provider-pyradios](https://github.com/OpenVoiceOS/ovos-media-provider-pyradios), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-somafm](https://github.com/OpenVoiceOS/ovos-skill-somafm) | OCP media skill | MediaProvider plugin [ovos-media-provider-somafm](https://github.com/OpenVoiceOS/ovos-media-provider-somafm), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-soundcloud](https://github.com/OpenVoiceOS/ovos-skill-soundcloud) | OCP media skill | MediaProvider plugin [ovos-media-provider-soundcloud](https://github.com/OpenVoiceOS/ovos-media-provider-soundcloud), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-spotify](https://github.com/OpenVoiceOS/ovos-skill-spotify) | OCP media skill | MediaProvider plugin [ovos-media-provider-spotify](https://github.com/OpenVoiceOS/ovos-media-provider-spotify), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-tunein](https://github.com/OpenVoiceOS/ovos-skill-tunein) | OCP media skill | MediaProvider plugin [ovos-media-provider-tunein](https://github.com/OpenVoiceOS/ovos-media-provider-tunein), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-youtube](https://github.com/OpenVoiceOS/ovos-skill-youtube) | OCP media skill | MediaProvider plugin [ovos-media-provider-youtube](https://github.com/OpenVoiceOS/ovos-media-provider-youtube), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |
| [ovos-skill-youtube-music](https://github.com/OpenVoiceOS/ovos-skill-youtube-music) | OCP media skill | MediaProvider plugin [ovos-media-provider-youtube-music](https://github.com/OpenVoiceOS/ovos-media-provider-youtube-music), configured under `intents.ovos-ocp-pipeline-plugin.media_providers` |

## STT plugins (9)

*Superseded STT engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ) | STT plugin for Basque, using HiTZ Basque Center models | [ovos-stt-plugin-onnx-asr](https://github.com/TigreGotico/ovos-stt-plugin-onnx-asr) |
| [ovos-stt-plugin-fasterwhisper-zuazo](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper-zuazo) | STT plugin loading Xabier de Zuazo's FasterWhisper fine-tunes for Iberian-peninsula languages (`pt`, `es`, `gl`, `ca`, `eu`) | [ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper) |
| [ovos-stt-plugin-mms](https://github.com/OpenVoiceOS/ovos-stt-plugin-mms) | STT plugin for Meta's MMS (Massively Multilingual Speech) models | [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) |
| [ovos-stt-plugin-nos](https://github.com/OpenVoiceOS/ovos-stt-plugin-nos) | Galician STT plugin using Proxecto Nós models | [ovos-stt-plugin-wav2vec2](https://github.com/OpenVoiceOS/ovos-stt-plugin-wav2vec2) |
| [ovos-stt-plugin-projectAINA-remote](https://github.com/OpenVoiceOS/ovos-stt-plugin-projectAINA-remote) | STT plugin calling a remote demo server hosted by Project AINA (Catalan speech models) | Remote demo server is gone, but it served a Catalan **Whisper** model: run that model locally with [ovos-stt-plugin-fasterwhisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-fasterwhisper) or [ovos-stt-plugin-whisper](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper) |
| [ovos-stt-plugin-MyNorthAI](https://github.com/OpenVoiceOS/ovos-stt-plugin-MyNorthAI) | Whisper STT plugin that wraps ovos-stt-plugin-whisper | None named in the repository |
| [ovos-stt-plugin-whisper-projectAINA](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-projectAINA) | Whisper STT plugin that wraps ovos-stt-plugin-whisper | None named in the repository |
| [ovos-stt-plugin-whisper-turbo](https://github.com/OpenVoiceOS/ovos-stt-plugin-whisper-turbo) | Whisper STT plugin that wraps ovos-stt-plugin-whisper | None named in the repository |
| [ovos-stt-plugin-xabier-zuazo](https://github.com/OpenVoiceOS/ovos-stt-plugin-xabier-zuazo) | Whisper STT plugin that wraps ovos-stt-plugin-whisper | None named in the repository |

## TTS plugins (8)

*Superseded TTS engines.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-tts-plugin-cotovia-remote](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia-remote) | TTS plugin calling a remote demo server for Cotovia TTS (Galician) | Removed, unofficial demo server is offline. No replacement |
| [ovos-tts-plugin-matxa-multispeaker-cat](https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat) | TTS plugin for the Matxa multispeaker/multidialect Catalan voices | [phoonnx](https://github.com/TigreGotico/phoonnx): runs the same Matxa Catalan models |
| [ovos-tts-plugin-mimic2](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic2) | TTS plugin for Mimic2, MycroftAI's proprietary cloud-hosted Tacotron voice | Removed: proprietary cloud-hosted Tacotron model, never released. The `kusal` voice in [phoonnx](https://github.com/TigreGotico/phoonnx) was trained on the same dataset and can be used instead. |
| [ovos-tts-plugin-mimic3](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3) | Text to speech plugin for OVOS using Mimic 3 | [phoonnx](https://github.com/TigreGotico/phoonnx): directly supports the Mimic3 voices (as it does Larynx and Piper voices) |
| [ovos-tts-plugin-mimic3-server](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3-server) | Client plugin calling a remote Mimic3 TTS server | The Mimic3 server API is gone, but [phoonnx](https://github.com/TigreGotico/phoonnx) runs the Mimic3 voices directly |
| [ovos-tts-plugin-nos](https://github.com/OpenVoiceOS/ovos-tts-plugin-nos) | Galician TTS | [phoonnx](https://github.com/TigreGotico/phoonnx): runs the Proxecto Nós Galician voices |
| [ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper) | TTS plugin running Piper ONNX voices | [phoonnx](https://github.com/TigreGotico/phoonnx): runs Piper ONNX voices (incl. the `kusal` voice) |
| [ovos-tts-plugin-lux](https://github.com/OpenVoiceOS/ovos-tts-plugin-lux) | TTS plugin for LuxTTS, a ZipVoice-based voice-cloning model | None named in the repository |

## Wake-word & VAD plugins (8)

*Older wake word/VAD engines. The Precise family is superseded by the ONNX build.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-vad-plugin-precise](https://github.com/OpenVoiceOS/ovos-vad-plugin-precise) | tflite GRU VAD detector | [ovos-vad-plugin-silero](https://github.com/OpenVoiceOS/ovos-vad-plugin-silero) |
| [ovos-ww-plugin-nyumaya-legacy](https://github.com/OpenVoiceOS/ovos-ww-plugin-nyumaya-legacy) | wake-word plugin for mycroft-core | Removed: use [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) / openWakeWord |
| [ovos-ww-plugin-precise](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise) | mycroft plugin for detecting wake word with precise | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [ovos-ww-plugin-precise-lite](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-lite) | TFLite Precise wake-word plugin | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx). The bundled `mycroft.conf` does not use precise-lite. Its `hey_mycroft` chain is `ovos-ww-plugin-precise-onnx`, then `ovos-ww-plugin-wakeforge` with the streaming wakehubert model, then `ovos-ww-plugin-wakeforge` with the wakehubert model, then `ovos-ww-plugin-vosk` |
| [ovos-ww-plugin-snowboy](https://github.com/OpenVoiceOS/ovos-ww-plugin-snowboy) | snowboy plugin for mycroft | Removed: use [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) / openWakeWord |
| [precise-lite](https://github.com/OpenVoiceOS/precise-lite) | A lightweight, simple-to-use, RNN wake-word listener | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |
| [precise-lite-trainer](https://github.com/OpenVoiceOS/precise-lite-trainer) | train wake-word models | Archived: superseded by [WakeForge](https://github.com/TigreGotico/wakeforge) with [ovos-ww-plugin-wakeforge](https://github.com/OpenVoiceOS/ovos-ww-plugin-wakeforge); [openWakeWord](https://github.com/dscripka/openWakeWord)/[microWakeWord](https://github.com/kahrendt/microWakeWord) also train new phrases |
| [precise_lite_runner](https://github.com/OpenVoiceOS/precise_lite_runner) | Standalone runner library for using Precise Lite wake-word models outside OVOS | [ovos-ww-plugin-precise-onnx](https://github.com/OpenVoiceOS/ovos-ww-plugin-precise-onnx) |

## PHAL & GUI plugins (16)

*Hardware/GUI plugins superseded by the current PHAL set or the GUI rework.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-ovos_enclosure](https://github.com/OpenVoiceOS/ZZZ-ovos_enclosure) | Enclosure module | [ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL) |
| [mycroft-gui-qt5](https://github.com/OpenVoiceOS/mycroft-gui-qt5) | maintained version of the old QT5 mycroft-gui for OpenVoiceOS | [mycroft-gui-qt6](https://github.com/OpenVoiceOS/mycroft-gui-qt6) |
| [ovos-PHAL-plugin-balena-wifi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-balena-wifi) | PHAL plugin providing a Balena-based Wi-Fi setup interface | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-PHAL-plugin-brightness-control-rpi](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-brightness-control-rpi) | PHAL plugin controlling screen brightness on Raspberry Pi devices | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-color-scheme-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-color-scheme-manager) | OVOS Shell ColorScheme Manager Plugin for OVOS PHAL | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-configuration-provider](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-configuration-provider) | PHAL plugin to provide configuration in displayable GUI format | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-dashboard](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dashboard) | Dashboard PHAL plugin to handle Dashboard operations | Removed: community-maintained, no official replacement |
| [ovos-PHAL-plugin-display-manager-ipc](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-display-manager-ipc) | Legacy Mark 1 faceplate display-manager plugin, tracking which skill "owns" the display | Removed: folded into [ovos-gui](https://github.com/OpenVoiceOS/ovos-gui) |
| [ovos-PHAL-plugin-gui-network-client](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client) | A GUI Network Client For PHAL | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant) | HomeAssistant PHAL Plugin for OpenVoice OS | Removed: use a dedicated Home Assistant skill (e.g. OscillateLabsLLC/skill-homeassistant) |
| [ovos-PHAL-plugin-mk2](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2) | Monolithic Mark 2 hardware PHAL plugin (fan, LEDs, buttons together) | [ovos-PHAL-plugin-mk2-v6-fan-control](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) |
| [ovos-PHAL-plugin-notification-widgets](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-notification-widgets) | Notifications and Widgets PHAL plugin | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-PHAL-plugin-wifi-setup](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-wifi-setup) | Central Wi-Fi Setup Plugin for PHAL | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [ovos-gui-plugin-shell-companion](https://github.com/OpenVoiceOS/ovos-gui-plugin-shell-companion) | Bus-API companion plugin integrating with the legacy ovos-shell | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |
| [ovos-media-plugin-qt5](https://github.com/OpenVoiceOS/ovos-media-plugin-qt5) | default GUI implementation for OCP framework | GUI rework (ovos-gui adapters) |
| [ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) | The Qt5 (mycroft-gui-qt5-embedding) shell application for EGLFS display platforms | GUI rework: [pyhtmx-gui-client](https://github.com/OpenVoiceOS/pyhtmx-gui-client) |

## Core, libraries & tooling (18)

*Old metapackages/utilities, merged elsewhere or retired.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ovos-classifiers](https://github.com/OpenVoiceOS/ovos-classifiers) | Experimental, pre-alpha grab-bag of text/audio classifiers | Removed: split into focused libs (ovos-utterance-normalizer, ovos-lang-detector-*, ovos-*-parser) |
| [ovos-cli-client](https://github.com/OpenVoiceOS/ovos-cli-client) | Standalone debug CLI client, extracted from classic mycroft-core | Removed: use messagebus tooling (ovos-busmon) |
| [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener) | ovos-core metapackage for speech daemon | [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) |
| [ovos-translate-plugin-deepl](https://github.com/OpenVoiceOS/ovos-translate-plugin-deepl) | Translation plugin calling the (paid, API-key-gated) DeepL service | [ovos-translate-plugin-nllb](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb) |
| [ovos-translations](https://github.com/OpenVoiceOS/ovos-translations) | Machine-translated locale resources produced while awaiting human translation | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos_skill_installer](https://github.com/OpenVoiceOS/ovos_skill_installer) | A package extraction tool for Python | ovos-core / ovos-workshop |
| [ovos_skill_manager](https://github.com/OpenVoiceOS/ovos_skill_manager) | skill installer for OVOS | ovos-core / ovos-workshop |
| [ovos-lingua-franca](https://github.com/OpenVoiceOS/ovos-lingua-franca) | Mycroft's multilingual text parsing and formatting library | Split into focused libraries: [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser), [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser), and the other `ovos-*-parser` packages |
| [mycroft-legacy](https://github.com/OpenVoiceOS/mycroft-legacy) | Restored select deprecated mycroft-core functionality for installs that still depended on it | Archived, no replacement |
| [scripts](https://github.com/OpenVoiceOS/scripts) | Grab-bag of small helper scripts for OVOS maintenance tasks | Archived; log tooling lives in ovos-utils (`ovos-logs`) |
| [zzz-old-ovos-utils](https://github.com/OpenVoiceOS/zzz-old-ovos-utils) | collection of simple utilities for use across the mycroft ecosystem | [ovos-utils](https://github.com/OpenVoiceOS/ovos-utils) |
| [ovos-solver-personal-llm](https://github.com/OpenVoiceOS/ovos-solver-personal-llm) | Solver that stores user facts and answers questions about them with an LLM | None named in the repository |
| [ovos-solver-plugin-llamacpp](https://github.com/OpenVoiceOS/ovos-solver-plugin-llamacpp) | Solver that runs LLaMA models through llamacpp-python | None named in the repository |
| [ovos-rag-solver](https://github.com/OpenVoiceOS/ovos-rag-solver) | Retrieval-augmented generation solver | None named in the repository |
| [ovos-gguf-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-gguf-embeddings-plugin) | GGUF embeddings plugin | [ovos-gguf-plugin](https://github.com/OpenVoiceOS/ovos-gguf-plugin), which keeps the plugin name `ovos-gguf-embeddings-plugin` |
| [ovos-gguf-translate-plugin](https://github.com/OpenVoiceOS/ovos-gguf-translate-plugin) | GGUF translation plugin | [ovos-gguf-plugin](https://github.com/OpenVoiceOS/ovos-gguf-plugin) (translate wrapper) |
| [ovos-messagebus-cpp](https://github.com/OpenVoiceOS/ovos-messagebus-cpp) | Alternative messagebus service (WebSocket server) in C++ | None named in the repository. [ovos-messagebus](https://github.com/OpenVoiceOS/ovos-messagebus) is the maintained bus service |
| [ZZZZ_lingua_plus](https://github.com/OpenVoiceOS/ZZZZ_lingua_plus) | Copy of the Lingua Franca text parsing and formatting library | See ovos-lingua-franca above |

## Datasets, lists & images (9)

*Reference/data repos kept for history.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [ZZZ-raspOVOS](https://github.com/OpenVoiceOS/ZZZ-raspOVOS) | Run ovos ontop of RaspberryPiOS | [raspOVOS](https://github.com/OpenVoiceOS/raspOVOS): the current, actively maintained image |
| [awesome-ocp-skills](https://github.com/OpenVoiceOS/awesome-ocp-skills) | Media skills for OCP, music, movies, radio, audiobooks and more! | [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) |
| [awesome-ovos-plugins](https://github.com/OpenVoiceOS/awesome-ovos-plugins) | List of ovos-plugin-manager plugins and projects | [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) |
| [big-tts-cache](https://github.com/OpenVoiceOS/big-tts-cache) | cached utterances from the defunct mimic2 TTS from Mycroft AI | Removed (mimic2 retired) |
| [lang-support-tracker](https://github.com/OpenVoiceOS/lang-support-tracker) | Dashboard tracking per-language plugin/skill translation coverage | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-gitlocalize-intent-dataset](https://github.com/OpenVoiceOS/ovos-gitlocalize-intent-dataset) | Exported dataset of intent utterances collected via GitLocalize translation | [ovos-localize](https://github.com/OpenVoiceOS/ovos-localize) |
| [ovos-ww-auto-synth-dataset](https://github.com/OpenVoiceOS/ovos-ww-auto-synth-dataset) | Pipeline that auto-synthesized wake-word training audio from submitted configs | [ovos-ww-community-dataset](https://github.com/OpenVoiceOS/ovos-ww-community-dataset) |
| [raspovos-manual](https://github.com/OpenVoiceOS/raspovos-manual) | User manual for the raspOVOS image | raspOVOS README / ovos-installer |
| [precise-lite-models](https://github.com/OpenVoiceOS/precise-lite-models) | Free models for precise-lite | Archived, but the bundled `mycroft.conf` still downloads its `hey_mycroft.onnx` model from this repository for `ovos-ww-plugin-precise-onnx` |

## Test, template & internal repos (17)

*Scaffolding/test/dummy repos, not user-facing.*

| Repository | What it was | Replacement / status |
|---|---|---|
| [disable-msm-dummy-repo](https://github.com/OpenVoiceOS/disable-msm-dummy-repo) | A repository for sharing and collaboration for third-party Mycroft skills development. | Removed: MSM (Mycroft Skills Manager) test artifact |
| [hardware-mycroft-mark-1](https://github.com/OpenVoiceOS/hardware-mycroft-mark-1) | in-case-of-apocalypse archive of Mycroft Mark 1 repository | historical archive |
| [my-assistant](https://github.com/OpenVoiceOS/my-assistant) | template repo for derivative voice assistants | Removed: old assistant template scaffold |
| [ovos-skills-info](https://github.com/OpenVoiceOS/ovos-skills-info) | Skill information parser support skill | Removed: skill metadata folded into ovos-workshop |
| [ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin) | Heuristic yes/no answer classifier, under the old solver plugin type | [ovos-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-YesNo-plugin) (needs ovos-plugin-manager>=2.4.0) |
| [quiet.py](https://github.com/OpenVoiceOS/quiet.py) | Python Ctypes Bindings for libquiet | Removed: use [ovos-audio-transformer-plugin-ggwave](https://github.com/OpenVoiceOS/ovos-audio-transformer-plugin-ggwave) |
| [skill-abort-test](https://github.com/OpenVoiceOS/skill-abort-test) | internal test skill for an `ovos_utils` change | Removed: internal test skill |
| [skill-balena-wifi-setup](https://github.com/OpenVoiceOS/skill-balena-wifi-setup) | Skill-based Wi-Fi setup flow for Balena-managed devices | [ovos-PHAL-plugin-network-manager](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager) |
| [skill-monkey-patch-tester](https://github.com/OpenVoiceOS/skill-monkey-patch-tester) | test monkey patches | Removed: internal test skill |
| [skill-monkey-patcher](https://github.com/OpenVoiceOS/skill-monkey-patcher) | apply patches to mycroft-core at runtime | Removed, mycroft-core runtime patcher. No replacement |
| [skill-template-repo](https://github.com/OpenVoiceOS/skill-template-repo) | Starter template repo for scaffolding a new skill | [ovos-skill-hello-world](https://github.com/OpenVoiceOS/ovos-skill-hello-world) |
| [template-package-repo](https://github.com/OpenVoiceOS/template-package-repo) | Starter template repo for scaffolding a new plugin package | Removed: use [gh-automations](https://github.com/OpenVoiceOS/gh-automations) shared workflows |
| [tskill-ocp-cps](https://github.com/OpenVoiceOS/tskill-ocp-cps) | Internal test skill exercising the OCP common-play-service contract | Removed: internal test skill |
| [tskill-osm_parsing](https://github.com/OpenVoiceOS/tskill-osm_parsing) | Repository to test OSM parser testing | Removed: internal test skill |
| [ovos-intent-benchmark](https://github.com/OpenVoiceOS/ovos-intent-benchmark) | Paradigm-neutral benchmark spec for OVOS intent engines | None named in the repository |
| [ovos-site](https://github.com/OpenVoiceOS/ovos-site) | The OVOS Foundation web site | None named in the repository |
| [hugo-site](https://github.com/OpenVoiceOS/hugo-site) | WordPress-to-Hugo export of the web site, kept for its assets | None named in the repository |

---
**Read next:** [License](license.md)
**Related:** [OVOS Repository Index](ecosystem-index.md) · [Contributing](contributing.md) · [gh-automations Overview](gh-automations-overview.md)
