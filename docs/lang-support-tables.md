# Language Support Tables

!!! abstract "In a nutshell"
    This page holds the per-language STT/TTS/parser coverage tables for OVOS: which languages have a bundled offline speech model, and which have a number/date parser module. Use it to look up one language. For the narrative on how language support works and how to improve it, see [Language Support](lang-support.md).

---

## Supported Languages

> The table below is a snapshot of the bundled recommendations. The authoritative list is whatever `recommends/offline_stt/*.conf`, `recommends/offline_female/*.conf`, and `recommends/offline_male/*.conf` files ship in your installed `ovos-config`. It grows as new models are added to the OVOS Hugging Face collections.

Offline STT is [`ovos-stt-plugin-onnx-asr`](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr) everywhere
it's listed. Where the table shows an offline TTS entry, it is always
[`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx), pinned to a specific male
and/or female voice. `int8` next to a model means a quantized CPU build is available and used
by default.

`--gpu` swaps the STT module to the best GPU model recommended for that language, with
`use_cuda: true`. That is `ovos-stt-plugin-fasterwhisper` for eleven of the twelve, but the
model varies: six (`da-dk`, `de-de`, `en-us`, `fr-fr`, `it-it`, `nl-nl`) get the generic
`whisper-large-v3-turbo`, while `ca-es`, `es-es`, `gl-es`, `pt-br`, and `pt-pt` get dedicated
finetunes. Basque (`eu-es`) uses a different plugin entirely, `ovos-stt-plugin-HiTZ`. Only the 12 languages with a
`recommends/gpu/*.conf` in `ovos-config` have a GPU tier at all. The others keep their
CPU recommendation.

!!! note "A TTS recommend needs a voice with a known gender"
    A bundled offline TTS recommendation pins one male voice and one female voice per
    language, wherever one is known. A single-speaker Facebook MMS voice counts as male.
    `autoconfigure` adds a language only once a phoonnx voice of known gender exists for it.
    A language without one is STT-only until such a voice appears. You can still point
    `ovos-tts-plugin-phoonnx` at any voice ID yourself, but it won't be auto-selected.

Several regional variants still have gaps. **EN-GB**, **PT-BR**, and the three ungapped
Catalan variants (**CA-BA**, **CA-NW**, **CA-VA**, alongside the already-covered **CA-ES**)
ship a TTS voice but no bundled offline STT recommendation. Configure a multilingual model by
hand until a dedicated recommendation lands: the practical picks are
[`ovos-stt-plugin-fasterwhisper`](stt-plugins-reference.md#ovos-stt-plugin-fasterwhisper)
(Whisper handles Catalan) locally, or
[`ovos-stt-plugin-server`](stt-plugins-reference.md#ovos-stt-server-plugin) pointed at a
[self-hosted STT server](stt-server.md) running one of those models.

| Language | Offline STT model | Offline TTS |
|----------|--------------------|:---:|
| **AR-SA** | `OpenVoiceOS/stt_ar_fastconformer_hybrid_large_pcd_v1.0_onnx` | yes |
| **CA-BA** | — | yes |
| **CA-ES** | `OpenVoiceOS/stt-ca-es-conformer-transducer-large-onnx` | yes |
| **CA-NW** | — | yes |
| **CA-VA** | — | yes |
| **DA-DK** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes (male only) |
| **DE-DE** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes |
| **EN-GB** | — | yes |
| **EN-US** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes |
| **ES-ES** | `OpenVoiceOS/parakeet-rnnt-1.1b-cv17-es-ep18-1270h-onnx` | yes |
| **EU-ES** | `OpenVoiceOS/stt-eu-conformer-transducer-large-onnx` | yes |
| **FR-FR** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes |
| **GL-ES** | `onnx-community/whisper-large-v3-turbo` (int8) | yes |
| **IT-IT** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes |
| **NL-NL** | `nemo-parakeet-tdt-0.6b-v3` (int8) | yes |
| **PT-BR** | — | yes |
| **PT-PT** | `OpenVoiceOS/whisper-medium-pt-onnx` | yes |

!!! note
    Where the STT column shows "—", the bundled recommendations don't cover offline speech
    recognition for that language yet. `autoconfigure` will skip that part of the
    configuration and tell you so. Use an online STT plugin instead. This table covers only
    the flagship set with a GPU tier; dozens more languages have a bundled offline STT and/or
    TTS recommendation without one — check the `recommends/` directories in your installed
    `ovos-config` for the current full list before relying on `autoconfigure`.

!!! note "Some TTS recommends cover only one gender"
    **DA-DK** ships only a male voice. The female slot falls back to no TTS configuration
    until a voice with that gender is confirmed. Pass the matching `--male`/`--female` flag
    per language. Every other language listed here has both genders bundled.

A language that does not appear in this table has no bundled STT/TTS recommendation yet.
This is not a deliberate exclusion. It just means nobody has added a `recommends/*.conf` file for it
so far. Thai is a widely requested example. `ovos-config` currently ships no `th-th` (or any other
`th-*`) recommends file, so `autoconfigure -l th-th` has nothing to select
and Thai support must be configured by hand until a recommendation is contributed.

---

## Per-language status matrix

STT/TTS columns summarize the auto-configuration table above (yes = a bundled offline
recommendation exists for at least one voice/gender, partial = only online/partial, no = no bundled
offline recommendation).

Number and date parsing come from the language modules actually
shipped in the installed `ovos-number-parser` / `ovos-date-parser`. A yes here means a
dedicated language module exists (`numbers_<code>.py` / `dates_<code>.py`), not that every
phrasing is covered.

This matrix tracks the original, longest-supported languages. See the
[Supported Languages](#supported-languages) table above for the full, larger set of
languages with a bundled offline STT and/or TTS recommendation.

| Language | Offline STT | Offline TTS | Number parser | Date parser |
|----------|:---:|:---:|:---:|:---:|
| en-US | yes | yes | yes | yes |
| en-GB | no | yes | yes | yes |
| en-AU | no | no | yes | yes |
| de-DE | yes | yes | yes | yes |
| fr-FR | yes | yes | yes | yes |
| es-ES | yes | yes | yes | yes |
| it-IT | yes | yes | yes | yes |
| nl-NL | yes | yes | yes | yes |
| pt-PT | yes | yes | yes | yes |
| pt-BR | no | yes | yes | yes |
| ca-ES | yes | yes | yes | yes |
| gl-ES | yes | yes | yes | yes |
| eu-ES | yes | yes | yes | yes |
| da-DK | yes | partial (male only) | yes | yes |

Both the number and date parsers already cover far more languages than this original matrix,
including several with no offline STT/TTS recommendation at all (e.g. Arabic, Hebrew, Turkish,
Ukrainian, and more). Adding a language module for parsing text is much cheaper than shipping
a full speech model, so this column tends to run ahead of STT/TTS.

!!! warning "pt-BR has no bundled offline STT"
    Brazilian Portuguese is a widely-spoken variant with **no bundled offline speech-to-text
    recommendation** at all. `ovos-config autoconfigure -l pt-br --offline` will skip STT
    entirely. Use an online STT plugin, or configure a multilingual offline model (such as
    Whisper) by hand until a dedicated recommendation is added.

A language absent from this matrix, like both tables above, has no bundled recommendation or
verified STT/TTS/parser coverage yet. Japanese is again a case in point: it has neither a
`recommends/` entry in `ovos-config` nor a `numbers_ja.py`/`dates_ja.py` module in
`ovos-number-parser`/`ovos-date-parser` today. That is an honest gap to fill, not a sign
Japanese was overlooked or excluded on purpose.

---
**Read next:** [Language Support](lang-support.md)
**Related:** [STT Plugins](stt-plugins.md) · [TTS Plugins](tts-plugins.md) · [Language Selection (internals)](lang-selection.md)
