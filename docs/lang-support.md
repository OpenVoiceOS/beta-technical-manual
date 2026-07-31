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

The bundled offline STT recommendations use [`ovos-stt-plugin-citrinet`](stt-plugins.md#ovos-stt-plugin-citrinet)
or [`ovos-stt-plugin-fasterwhisper`](stt-plugins.md#ovos-stt-plugin-fasterwhisper), depending on
the language. TTS uses [`ovos-tts-plugin-phoonnx`](tts-plugins.md#ovos-tts-plugin-phoonnx) for
every language. The table below shows the exact per-language plugin/model and voice picked
for each.

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

> The table below is a snapshot of the bundled recommendations. The authoritative list is whatever `recommends/base/*.conf`, `recommends/offline_stt/*.conf`, and related files ship in your installed `ovos-config`.

Plainly: a few widely-spoken variants still have real gaps in the bundled recommendations.
**en-GB** and **pt-BR** have no bundled offline STT recommendation at all. You'll need to
configure an online plugin or pick a multilingual offline model (e.g. Whisper) by hand.
**en-AU** has no bundled offline recommendation on either side. Some regional voices are
one-gender-only offline (e.g. **da-DK** ships no offline female voice). The missing gender
still works, just via an online plugin or a manually configured model.

The table shows the exact offline STT plugin and model, and the offline TTS voice, each
language is configured with.

| Language | Offline STT plugin (model) | Offline TTS voice (Male) | Offline TTS voice (Female) |
|----------|-------------|---------------------|---------------------|
| **en-US** | `ovos-stt-plugin-citrinet` (`lang=en`) | `OpenVoiceOS/pipertts_en-US_miro` | `OpenVoiceOS/pipertts_en-GB_dii` |
| **en-GB** | — | `OpenVoiceOS/pipertts_en-GB_miro` | `OpenVoiceOS/pipertts_en-GB_dii` |
| **de-DE** | `ovos-stt-plugin-citrinet` (`lang=de`) | `OpenVoiceOS/pipertts_de-DE_miro` | `OpenVoiceOS/pipertts_de-DE_dii` |
| **fr-FR** | `ovos-stt-plugin-citrinet` (`lang=fr`) | `OpenVoiceOS/pipertts_fr-FR_miro` | `piper/fr_FR-siwis-medium` |
| **es-ES** | `ovos-stt-plugin-citrinet` (`lang=es`) | `OpenVoiceOS/pipertts_es-ES_miro` | `OpenVoiceOS/phoonnx_es-ES_dii_espeak` |
| **it-IT** | `ovos-stt-plugin-citrinet` (`lang=it`) | `OpenVoiceOS/pipertts_it-IT_miro` | `OpenVoiceOS/pipertts_it-IT_dii` |
| **nl-NL** | `ovos-stt-plugin-citrinet` (`lang=nl`) | `OpenVoiceOS/pipertts_nl-NL_miro` | `OpenVoiceOS/pipertts_nl-NL_dii` |
| **pt-PT** | `ovos-stt-plugin-citrinet` (`lang=pt`) | `OpenVoiceOS/pipertts_pt-PT_miro` | `OpenVoiceOS/pipertts_pt-PT_dii` |
| **pt-BR** | — | `OpenVoiceOS/pipertts_pt-BR_miro` | `OpenVoiceOS/pipertts_pt-BR_dii` |
| **ca-ES** | `ovos-stt-plugin-citrinet` (`lang=ca`) | `OpenVoiceOS/matxa-cat-multiaccent-wavenext` (speaker 2) | `OpenVoiceOS/matxa-cat-multiaccent-wavenext` (speaker 3) |
| **gl-ES** | `ovos-stt-plugin-fasterwhisper` (`Jarbas/faster-whisper-base-gl-cv13`) | `OpenVoiceOS/phoonnx_gl-ES_miro_unicode` | `proxectonos/celtia` |
| **eu-ES** | `ovos-stt-plugin-fasterwhisper` (`Jarbas/faster-whisper-base-eu-cv16`) | `OpenVoiceOS/phoonnx_eu-ES_miro_espeak` | `OpenVoiceOS/phoonnx_eu-ES_dii_espeak` |
| **da-DK** | `ovos-stt-plugin-fasterwhisper` (`base`) | `OpenVoiceOS/phoonnx_da-DK_miro_espeak` | — |
| **en-AU** | — | — | — |

!!! note
    Where a cell shows "—", the bundled recommendations don't cover that combination yet.
    `autoconfigure` will skip that part of the configuration and tell you so.

### Per-language status matrix

STT/TTS columns summarize the auto-configuration table above (✅ = a bundled offline
recommendation exists for at least one voice/gender, ⚠️ = only online/partial, ❌ = no bundled
offline recommendation). Number and date parsing come from the language modules actually
shipped in the installed `ovos-number-parser` / `ovos-date-parser`. A ✅ here means a
dedicated language module exists (`numbers_<code>.py` / `dates_<code>.py`), not that every
phrasing is covered.

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

Both the number and date parsers already cover far more languages than the bundled
auto-configuration table above, including several with no offline STT/TTS recommendation yet
(e.g. Arabic, Hebrew, Polish, Turkish, Ukrainian, Russian, and more). Adding a language module
for parsing text is much cheaper than shipping a full speech model, so this column tends to
run ahead of STT/TTS.

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
