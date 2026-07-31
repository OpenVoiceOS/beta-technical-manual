# Language Support in OpenVoiceOS

!!! abstract "In a nutshell"
    Making OVOS truly work in a given language takes more than translating menu text. It
    needs translated skill phrases, a speech-to-text engine that understands that language,
    and a text-to-speech voice that can speak it. This page explains the current state of
    language support, how to get a working setup quickly with the `ovos-config autoconfigure`
    command, and how you can help improve your language by translating phrases or testing
    real speech. If you just want it running now, jump to
    [Auto-Configuration](#auto-configuration). See also
    [Customizing Language Resources](lang-customization.md) and the [Glossary](glossary.md).

OpenVoiceOS (OVOS) aims to support multiple languages across its components, including intent
recognition, speech-to-text ([STT](stt-plugins.md)), text-to-speech ([TTS](tts-plugins.md)),
and skill dialogs. However, full language support requires more than translation of interface
text. This document outlines the current state of language support, known limitations, and
how contributors can help improve multilingual performance in OVOS.

**Want it working now?** Jump to [Auto-Configuration](#auto-configuration).
`ovos-config autoconfigure -l <lang> ...` sets up recommended STT/TTS plugins in one command.
**Want to make your language work better?** See [How to Improve Language Support](#how-to-improve-language-support).

Related pages:

- [Language Selection](lang-selection.md): how OVOS picks a language per utterance.
- [Customizing Language Resources](lang-customization.md): override or translate skill text.
- [Bidirectional Translation](bidirectional-translation.md): use a single-language skill in any language.

!!! note "How language selection works"
    Setting the global `lang` key in [`mycroft.conf`](config.md) is sufficient on its own to
    switch the assistant's language: STT, TTS, and every other language-aware plugin follow
    the global `lang` automatically. A per-plugin `lang` setting exists only to *override*
    that default for one plugin (e.g. running a second voice in another language).
    `ovos-config autoconfigure` (below) is a convenience that additionally picks the
    *recommended* plugins/voices for a language (offline/online, gender). It optionally
    swaps in better defaults. It is not required just to switch languages.

!!! note "Language codes are case-insensitive"
    OVOS normalizes language codes internally (e.g. `en-us`, `EN-US`, and `en_US` all become
    `en-US`), so it doesn't matter which case you type them in on the command line or in
    `mycroft.conf`. This manual writes codes in lower-case (`en-us`) by convention.

---

The OVOS installer lets users select a preferred language, but **selecting a language does not guarantee full support across all subsystems**. True multilingual support requires dedicated:

- ✅ Translations (intents, dialogs, settings, etc.)


- ✅ STT ([Speech-to-Text](stt-plugins.md)) plugins trained on the target language


- ✅ TTS ([Text-to-Speech](tts-plugins.md)) plugins capable of generating speech in the selected language


- ✅ Language-specific intent adaptation and fallback logic

Without these, many core features, such as voice commands, speech output, and skill
interactions, may not work as expected.

---

## Adding a New Language

Adding support for a new language in OVOS is a multi-step process requiring:

- Translations of assistant dialog and intent files


- A compatible STT plugin with reliable speech recognition


- A natural-sounding TTS voice


- Validation using real-world user data

We welcome and encourage community participation to improve language support. Every contribution helps make OVOS more accessible to speakers around the world.

---

## Technical Language Handling

OVOS handles languages dynamically throughout the interaction cycle. To look closer at how the system picks which language to use for an utterance, see **[Language Selection and Disambiguation](lang-selection.md)**.

### STT and TTS Requirements

For a language to function correctly in a voice assistant environment, it must have **dedicated STT and TTS plugins** that support the language reliably.

### STT (Speech-to-Text)

- STT plugins must be able to recognize speech in the target language with high accuracy.


- Some plugins are multilingual (e.g., Whisper, MMS), but accuracy varies across languages.


- For production use, **language-specific tuning or models are recommended**.

### TTS (Text-to-Speech)

- The TTS engine must generate clear, natural-sounding speech in the selected language.


- Not all TTS plugins support all languages.


- Quality varies significantly by model and backend.

---

## Translation Coverage

OVOS uses [**OVOS Localize**](https://openvoiceos.github.io/ovos-localize/), a GitHub-native,
in-browser translation tool built for OVOS, to manage translation files across its
repositories. It replaces the retired third-party *GitLocalize* service. This includes:

- [Skill](skill-design-guidelines.md) dialog files


- Intent files (used by [Padatious](padatious-pipeline.md)/[Adapt](adapt-pipeline.md))


- Configuration metadata

### 📊 Translation Progress

OVOS Localize scans skill data and exports a language × skill coverage matrix to
[`data/coverage.json`](https://openvoiceos.github.io/ovos-localize/data/coverage.json),
refreshed alongside the translation app. This is the current source of translation progress.

> ⚠️ The older [lang-support-tracker](https://github.com/OpenVoiceOS/lang-support-tracker)
> is a **frozen GitLocalize-era snapshot** (superseded by OVOS Localize). Its percentages
> are no longer updated and should not be treated as current.

> ❗ If your language is missing from [OVOS Localize](https://openvoiceos.github.io/ovos-localize/), [open an issue](https://github.com/OpenVoiceOS/lang-support-tracker/issues) to request it. Currently, languages must be added manually.

See **[Contribute Translations with OVOS Localize](ovos-localize-tutorial.md)** for the step-by-step translator guide.

### Open-data ML datasets

OVOS Localize also auto-generates **machine-learning-ready JSONL datasets** from the scanned
skill data (hosted statically, refreshed daily), under `data/datasets/`:

- **Intent classification** (`classification/{lang}.jsonl`): `.intent`/`.voc` phrases mapped
  to their skill domain and intent name, for training NLU / small language models.
- **Parallel corpora** (`translation/{lang_pair}.jsonl`): English keys paired with their
  translations from `.dialog`/`.intent` files, for machine translation.

These load directly via HuggingFace `datasets.load_dataset(...)`.

---

## Known Limitations

- Selecting a language during installation only automatically configures a compatible STT/TTS plugin for **some languages**. Manual action might be required for full support


- Many skills contain only partial translations or outdated strings.

!!! note "The recommendations are a living registry"
    `ovos-config`'s bundled recommendations are not a fixed list. They track the current best
    known model per language, drawn from the [OpenVoiceOS STT ONNX](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx)
    and TTS Hugging Face collections. As better models appear for a language, the bundled
    recommendation is updated to point at them. Low-resource languages start with the best
    model available at the time (often a general-purpose Whisper or wav2vec2 finetune) and
    move to a dedicated model as one becomes available.


- Skills may be partially translated, with only a subset of intents available for your language


- Skills may have translated intents but missing dialog translations. The assistant typically speaks the dialog filename if it is not translated


- STT/TTS plugin coverage is uneven per language variant. Some regional variants have no bundled offline recommendation at all (see the gaps called out below the auto-configuration table). A language can be "installed" without actually being able to hear or speak yet.

---

## Auto-Configuration

The fastest way to get a working setup for your language is `ovos-config autoconfigure`. It writes recommended STT and TTS plugin settings into your user config:

```bash
ovos-config autoconfigure -l en-us --offline --female
ovos-config autoconfigure -l de-de --offline --male
ovos-config autoconfigure -l fr-fr --hybrid --female
```

!!! note
    These three commands illustrate the three *modes* (`--offline`/`--online`/`--hybrid`),
    not a per-language recommendation. Check the [Supported Languages](#supported-languages)
    table below for what's actually bundled for a given language before picking a mode.

The recommendations are data-driven: they come from per-language `*.conf` files bundled in `ovos-config` (`recommends/`), so the exact models depend on your installed version. See [`ovos-config`](config.md) for full options.

The bundled offline STT recommendation is [`ovos-stt-plugin-onnx-asr`](stt-plugins.md#ovos-stt-plugin-onnx-asr)
for every covered language, running a per-language ONNX model picked from the
[OpenVoiceOS STT ONNX](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx) collection.
On CPU it prefers `int8`-quantized weights where the model ships them, for a smaller
footprint and faster load. TTS uses [`ovos-tts-plugin-phoonnx`](tts-plugins.md#ovos-tts-plugin-phoonnx)
for every language, auto-selecting a default voice. The table below shows the exact
per-language model and voice picked for each.

Passing `--gpu` selects the GPU tier instead: the same model family at full `fp32` precision
with `use_cuda: true`, or, for languages with enough training data, a larger and more accurate
model than the CPU default (for example a full Whisper or Canary model instead of a
lighter Conformer). `--gpu` needs a CUDA-capable GPU and implies `--offline`.

### Flags

| Flag | Meaning |
|------|---------|
| `-l`, `--lang` | **Required.** Language code (e.g. `en-us`). Standardized internally (e.g. `en-US`). |
| `--offline` / `-off` | Offline STT + TTS. |
| `--online` / `-on` | Online (public-server) STT + TTS. |
| `--hybrid` / `-hy` | Offline TTS with online STT. |
| *(none of the three)* | **Defaults to hybrid.** |
| `--male` / `-m`, `--female` / `-f` | Pick a voice. Pass exactly one. If you pass **neither**, TTS configuration is skipped. |

After writing the config it lists the installed STT/TTS plugins and warns about any recommended plugin you still need to `pip install`.

Two more flags tune the result for your hardware:

- `--platform` / `-p` picks a hardware preset, one of `rpi3`, `rpi4`, `rpi5`, `linux`, `mac`,
  or `termux`, and optimizes the configuration for it.
- `--gpu` / `-g` selects GPU-accelerated plugins. It implies `--offline`, so it cannot be
  combined with `--online` or `--hybrid`, and it is rejected on the Raspberry Pi platforms.

### Supported Languages

> The table below is a snapshot of the bundled recommendations. The authoritative list is whatever `recommends/offline_stt/*.conf`, `recommends/offline_female/*.conf`, and `recommends/offline_male/*.conf` files ship in your installed `ovos-config`. It grows as new models are added to the OVOS Hugging Face collections.

Offline STT is [`ovos-stt-plugin-onnx-asr`](stt-plugins.md#ovos-stt-plugin-onnx-asr) everywhere
it's listed. Where the table shows an offline TTS entry, it is always
[`ovos-tts-plugin-phoonnx`](tts-plugins.md#ovos-tts-plugin-phoonnx), pinned to a specific male
and/or female voice. `int8` next to a model means a quantized CPU build is available and used
by default. `--gpu` switches to the full-precision model with `use_cuda: true`. For the most
widely-spoken languages (English, French, German, Italian, Dutch) it swaps in a larger model
entirely (`nemo-canary-1b-v2`) instead of just requantizing.

!!! note "A TTS recommend needs a gender-evidenced voice"
    A bundled offline TTS recommendation pins one male voice and one female voice per
    language. `autoconfigure` adds a language only once a phoonnx voice with a confirmed
    gender exists for it. A language without one is STT-only until such a voice appears; you
    can still point `ovos-tts-plugin-phoonnx` at any voice ID yourself, but it won't be
    auto-selected.

Several regional variants still have gaps. **EN-GB**, **PT-BR**, **AR-SA**, and the four
Catalan variants (**CA-BA**, **CA-NW**, **CA-VA**, plus the already-covered **CA-ES**) ship a
TTS voice but no bundled offline STT recommendation. **EN-AU** has no bundled offline
recommendation on either side. Configure an online STT plugin, or a multilingual offline model
(Whisper, MMS) by hand, until a dedicated recommendation lands for these.

Many low-resource languages have no fine-tuned Conformer or Parakeet model yet. Their
recommendation falls back to the best general-purpose model available: a Whisper-small
finetune (Fon, Haitian Creole, Kposo, Malagasy, Lomwe, Shona, Sesotho, Tigre, Setswana,
Umbundu, Vai) or a wav2vec2 finetune (Irish). These move to a dedicated model as one becomes
available.

| Language | Offline STT model | Offline TTS |
|----------|--------------------|:---:|
| **AR-SA** | — | ✅ |
| **AS-IN** | `OpenVoiceOS/ai4bharat-indicconformer-as-onnx` | — |
| **BE-BY** | `OpenVoiceOS/nvidia-be-conformer-transducer-large-onnx` (int8) | — |
| **BN-IN** | `OpenVoiceOS/ai4bharat-indicconformer-bn-onnx` (int8) | ✅ |
| **BRX-IN** | `OpenVoiceOS/ai4bharat-indicconformer-brx-onnx` (int8) | — |
| **CA-BA** | — | ✅ |
| **CA-ES** | `OpenVoiceOS/stt-ca-es-conformer-transducer-large-onnx` | ✅ |
| **CA-NW** | — | ✅ |
| **CA-VA** | — | ✅ |
| **DA-DK** | `OpenVoiceOS/nvidia-parakeet-rnnt-110m-da-dk-onnx` (int8) | ✅ |
| **DE-DE** | `nemo-parakeet-tdt-0.6b-v3` (int8) | ✅ |
| **DOI-IN** | `OpenVoiceOS/ai4bharat-indicconformer-doi-onnx` (int8) | — |
| **EN-GB** | — | ✅ |
| **EN-US** | `nemo-parakeet-tdt-0.6b-v3` (int8) | ✅ |
| **EO** | `OpenVoiceOS/nvidia-eo-conformer-transducer-large-onnx` (int8) | — |
| **ES-ES** | `OpenVoiceOS/parakeet-rnnt-1.1b-cv17-es-ep18-1270h-onnx` | ✅ |
| **ET-EE** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-et-onnx` (int8) | — |
| **EU-ES** | `OpenVoiceOS/stt-eu-conformer-transducer-large-onnx` | ✅ |
| **FA-IR** | `OpenVoiceOS/nvidia-fa-fastconformer-hybrid-large-onnx` (int8) | ✅ |
| **FON-BJ** | `OpenVoiceOS/misterkissi-whisper-small-fongbe-onnx` | — |
| **FR-FR** | `nemo-parakeet-tdt-0.6b-v3` (int8) | ✅ |
| **GA-IE** | `OpenVoiceOS/misterkissi-w2v2-lg-xls-r-300m-ga-onnx` | — |
| **GL-ES** | `onnx-community/whisper-large-v3-turbo` (int8) | ✅ |
| **GU-IN** | `OpenVoiceOS/ai4bharat-indicconformer-gu-onnx` (int8) | — |
| **HI-IN** | `OpenVoiceOS/ai4bharat-indicconformer-hi-onnx` (int8) | ✅ |
| **HR-HR** | `OpenVoiceOS/nvidia-hr-conformer-transducer-large-onnx` (int8) | — |
| **HT-HT** | `OpenVoiceOS/misterkissi-whisper-small-haitian-creole-onnx` | — |
| **IT-IT** | `nemo-parakeet-tdt-0.6b-v3` (int8) | ✅ |
| **JA-JP** | `OpenVoiceOS/nvidia-parakeet-tdt_ctc-0.6b-ja-onnx` (int8) | ✅ |
| **KAB-DZ** | `OpenVoiceOS/nvidia-kab-conformer-transducer-large-onnx` (int8) | — |
| **KN-IN** | `OpenVoiceOS/ai4bharat-indicconformer-kn-onnx` (int8) | — |
| **KOK-IN** | `OpenVoiceOS/ai4bharat-indicconformer-kok-onnx` (int8) | — |
| **KPO-TG** | `OpenVoiceOS/misterkissi-whisper-small-kposo-onnx` | — |
| **KS-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ks-onnx` (int8) | — |
| **MAI-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mai-onnx` (int8) | — |
| **MG-MG** | `OpenVoiceOS/misterkissi-whisper-small-malagasy-onnx` | — |
| **ML-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ml-onnx` (int8) | — |
| **MNI-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mni-onnx` (int8) | — |
| **MR-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mr-onnx` (int8) | — |
| **NE-NP** | `OpenVoiceOS/ai4bharat-indicconformer-ne-onnx` (int8) | — |
| **NGL-MZ** | `OpenVoiceOS/misterkissi-whisper-small-lomwe-onnx` | — |
| **NL-NL** | `nemo-parakeet-tdt-0.6b-v3` (int8) | ✅ |
| **OR-IN** | `OpenVoiceOS/ai4bharat-indicconformer-or-onnx` (int8) | — |
| **PA-IN** | `OpenVoiceOS/ai4bharat-indicconformer-pa-onnx` (int8) | — |
| **PL-PL** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-pl-onnx` | ✅ |
| **PT-BR** | — | ✅ |
| **PT-PT** | `OpenVoiceOS/whisper-medium-pt-onnx` | ✅ |
| **RU-RU** | `OpenVoiceOS/nvidia-ru-conformer-transducer-large-onnx` (int8) | — |
| **RW-RW** | `OpenVoiceOS/nvidia-rw-conformer-transducer-large-onnx` (int8) | — |
| **SA-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sa-onnx` (int8) | — |
| **SAT-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sat-onnx` (int8) | — |
| **SD-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sd-onnx` (int8) | — |
| **SL-SI** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-sl-onnx` (int8) | ✅ |
| **SN-ZW** | `OpenVoiceOS/misterkissi-whisper-small-shona-onnx` | — |
| **ST-ZA** | `OpenVoiceOS/misterkissi-whisper-small-sesotho-onnx` | — |
| **TA-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ta-onnx` (int8) | — |
| **TE-IN** | `OpenVoiceOS/ai4bharat-indicconformer-te-onnx` (int8) | — |
| **TIG-ER** | `OpenVoiceOS/misterkissi-whisper-small-tigre-onnx` | — |
| **TL-PH** | `OpenVoiceOS/stt-tl-fastconformer-hybrid-large-onnx` | — |
| **TN-ZA** | `OpenVoiceOS/misterkissi-whisper-small-setswana-onnx` | — |
| **UMB-AO** | `OpenVoiceOS/misterkissi-whisper-small-umbundu-onnx` | — |
| **UR-PK** | `OpenVoiceOS/ai4bharat-indicconformer-ur-onnx` (int8) | — |
| **UZ-UZ** | `OpenVoiceOS/asr-uz-fastconformer-large-onnx` | — |
| **VAI-LR** | `OpenVoiceOS/misterkissi-whisper-small-vai-onnx` | — |
| **VI-VN** | `OpenVoiceOS/nvidia-parakeet-ctc-0.6b-vietnamese-onnx` (int8) | — |

!!! note
    Where the STT column shows "—", the bundled recommendations don't cover offline speech
    recognition for that language yet. `autoconfigure` will skip that part of the
    configuration and tell you so. Use an online STT plugin instead.

!!! note "Some TTS recommends cover only one gender"
    **BN-IN** ships a male voice only, and **SL-SI** ships a female voice only. Pass the
    matching `--male`/`--female` flag for these; the other gender falls back to no TTS
    configuration until a voice with that gender is confirmed.

### Per-language status matrix

STT/TTS columns summarize the auto-configuration table above (✅ = a bundled offline
recommendation exists for at least one voice/gender, ⚠️ = only online/partial, ❌ = no bundled
offline recommendation). Number and date parsing come from the language modules actually
shipped in the installed `ovos-number-parser` / `ovos-date-parser`. A ✅ here means a
dedicated language module exists (`numbers_<code>.py` / `dates_<code>.py`), not that every
phrasing is covered. This matrix tracks the original, longest-supported languages. See the
[Supported Languages](#supported-languages) table above for the full, larger set of
languages with a bundled offline STT and/or TTS recommendation.

| Language | Offline STT | Offline TTS | Number parser | Date parser |
|----------|:---:|:---:|:---:|:---:|
| en-US | ✅ | ✅ | ✅ | ✅ |
| en-GB | ❌ | ✅ | ✅ | ✅ |
| en-AU | ❌ | ❌ | ✅ | ✅ |
| de-DE | ✅ | ✅ | ✅ | ✅ |
| fr-FR | ✅ | ✅ | ✅ | ✅ |
| es-ES | ✅ | ✅ | ✅ | ✅ |
| it-IT | ✅ | ✅ | ✅ | ✅ |
| nl-NL | ✅ | ✅ | ✅ | ✅ |
| pt-PT | ✅ | ✅ | ✅ | ✅ |
| pt-BR | ❌ | ✅ | ✅ | ✅ |
| ca-ES | ✅ | ✅ | ✅ | ✅ |
| gl-ES | ✅ | ✅ | ✅ | ✅ |
| eu-ES | ✅ | ✅ | ✅ | ✅ |
| da-DK | ✅ | ⚠️ (male only) | ✅ | ✅ |

Both the number and date parsers already cover far more languages than this original matrix,
including several with no offline STT/TTS recommendation at all (e.g. Arabic, Hebrew, Turkish,
Ukrainian, and more). Adding a language module for parsing text is much cheaper than shipping
a full speech model, so this column tends to run ahead of STT/TTS.

!!! warning "pt-BR has no bundled offline STT"
    Brazilian Portuguese is a widely-spoken variant with **no bundled offline speech-to-text
    recommendation** at all. `ovos-config autoconfigure -l pt-br --offline` will skip STT
    entirely. Use an online STT plugin, or configure a multilingual offline model (such as
    Whisper) by hand until a dedicated recommendation is added.

---

## How to Improve Language Support

### 1. **Contribute Translations**

Use [OVOS Localize](https://openvoiceos.github.io/ovos-localize/) to translate dialog and intent files right in your browser:

- [OVOS Localize translation app](https://openvoiceos.github.io/ovos-localize/)


- [Translator Tutorial](ovos-localize-tutorial.md)

Live per-language translation stats are available from OVOS Localize:

- [`data/coverage.json`](https://openvoiceos.github.io/ovos-localize/data/coverage.json): language × skill coverage matrix with display names

---

### 2. **Test in Real-World Usage**

Translation coverage alone does not ensure accuracy. Native speakers are encouraged to test OVOS with real speech input and report issues with:

- Intent matching failures


- Mispronunciations or robotic speech


- Incorrect or unnatural translations

You can help by **enabling open data collection** in your OVOS instance by pointing `intent_urls` at a reporting server:

```jsonc
"open_data": {
  "intent_urls": [
    "https://your-opendata-server.example.com/intents"
  ]
}

```

> 💡 You can self-host the reporting server: [ovos-opendata-server on GitHub](https://github.com/OpenVoiceOS/ovos-opendata-server)

---

## Benchmark Projects (Open Data)

Explore public benchmark tools for evaluating model performance:

| Project                                                         | Description |
|-----------------------------------------------------------------|-------------|
| [OVOS Localize](https://openvoiceos.github.io/ovos-localize/)   | Browse intent translation coverage per language and skill |


---

## Tips for Contributors

- Translators: Use [OVOS Localize](https://openvoiceos.github.io/ovos-localize/)'s side-by-side editor, which shows the skill code behind each phrase, to keep intent logic intact.


- Developers: Review user-submitted errors on the dashboard to improve skill performance.


- Curious users: Explore benchmark results to see how well OVOS handles your language.

## Further reading

- [Cloning Voices for Endangered Languages: Asturian & Aragonese](https://blog.openvoiceos.org/posts/2025-12-09-ast) — OVOS blog
- [Reflections on Our Collaboration: an Open Arabic Voice](https://blog.openvoiceos.org/posts/2025-10-01-arabic_tts_collaboration) — OVOS blog
- [Introducing the First Phonemizer for Barranquenho](https://blog.openvoiceos.org/posts/2025-12-14-barranquenho) — OVOS blog
