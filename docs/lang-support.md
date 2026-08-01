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
text.

This document outlines the current state of language support, known limitations, and
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

- Translations (intents, dialogs, settings, etc.)


- STT ([Speech-to-Text](stt-plugins.md)) plugins trained on the target language


- TTS ([Text-to-Speech](tts-plugins.md)) plugins capable of generating speech in the selected language


- Language-specific intent adaptation and fallback logic

Without these, many core features, such as voice commands, speech output, and skill
interactions, may not work as expected.

---

## Adding a New Language

Adding a new language to OVOS touches four separate repositories. Work through them in this
order:

1. **Translate dialog and intent files.** Use [OVOS Localize](https://openvoiceos.github.io/ovos-localize/)
   to add and translate the skill-side `.dialog`/`.intent`/`.voc` files for the language. See
   [Contributing Translations](ovos-localize-tutorial.md) for the step-by-step guide.
   **Deliverable:** a translated set of skill resource files, submitted through OVOS Localize.

2. **Add number and date parsing.** Open a pull request against
   [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser) and
   [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser). Each language gets its
   own module, following the existing naming convention: `numbers_<code>.py` in
   `ovos-number-parser` (for example `numbers_pt.py`, `numbers_de.py`) and `dates_<code>.py` in
   `ovos-date-parser` (for example `dates_pt.py`, `dates_de.py`). **Deliverable:** a
   `numbers_<code>.py` and/or `dates_<code>.py` module, wired into that repo's dispatch table.

3. **Add STT/TTS coverage.** Configure a working STT and TTS plugin for the language (see
   [STT Plugins](stt-plugins.md) and [TTS Plugins](tts-plugins.md)), then open a pull request
   against [ovos-config](https://github.com/OpenVoiceOS/ovos-config) adding a `*.conf` file
   under `ovos_config/recommends/` (for example `recommends/offline_female/<lang>.conf`) so
   `autoconfigure` can pick it up automatically for every install. **Deliverable:** a
   `recommends/**/<lang>.conf` file bundled with `ovos-config`.

4. **Validate with real usage.** Once STT/TTS plugins exist for the language, get it benchmarked
   and human-rated on the [Plugin Arena](plugin-arena.md), and test real speech end-to-end.
   **Deliverable:** the language's plugins entered into the arena's STT/TTS/wake word leagues.

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

### Translation Progress

OVOS Localize scans skill data and exports a language × skill coverage matrix to
[`data/coverage.json`](https://openvoiceos.github.io/ovos-localize/data/coverage.json),
refreshed alongside the translation app. This is the current source of translation progress.

> Warning: the older [lang-support-tracker](https://github.com/OpenVoiceOS/lang-support-tracker)
> is a **frozen GitLocalize-era snapshot** (superseded by OVOS Localize). Its percentages
> are no longer updated and should not be treated as current.

> Note: if your language is missing from [OVOS Localize](https://openvoiceos.github.io/ovos-localize/), [open an issue](https://github.com/OpenVoiceOS/lang-support-tracker/issues) to request it. Currently, languages must be added manually.

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

The bundled offline STT recommendation is [`ovos-stt-plugin-onnx-asr`](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr)
for every covered language, running a per-language ONNX model picked from the
[OpenVoiceOS STT ONNX](https://huggingface.co/collections/OpenVoiceOS/stt-asr-onnx) collection.
On CPU it prefers `int8`-quantized weights where the model ships them, for a smaller
footprint and faster load.

TTS uses [`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx)
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

**The full per-language STT/TTS/parser coverage tables live on their own page: see
[Language Support Tables](lang-support-tables.md).** It has the bundled-recommendation
table (which offline STT model and TTS voice each language code gets from
`autoconfigure`) and the per-language status matrix (STT, TTS, number parser, date
parser, side by side for the original, longest-supported languages).

Briefly: offline STT comes from [`ovos-stt-plugin-onnx-asr`](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr)
and offline TTS from [`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx)
wherever a recommendation is bundled. Several regional variants, including **EN-GB**,
**PT-BR**, **AR-SA**, and three of the four Catalan variants, ship a TTS voice but no
bundled offline STT recommendation yet. A language absent from both tables, such as
Japanese, has no bundled recommendation at all: that is an honest gap to fill, not a
deliberate exclusion. See [Language Support Tables](lang-support-tables.md) for the
exact per-language breakdown.

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

> Note: you can self-host the reporting server: [ovos-opendata-server on GitHub](https://github.com/OpenVoiceOS/ovos-opendata-server)

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

- [Cloning Voices for Endangered Languages: Asturian & Aragonese](https://blog.openvoiceos.org/posts/2025-12-09-ast): OVOS blog
- [Reflections on Our Collaboration: an Open Arabic Voice](https://blog.openvoiceos.org/posts/2025-10-01-arabic_tts_collaboration): OVOS blog
- [Introducing the First Phonemizer for Barranquenho](https://blog.openvoiceos.org/posts/2025-12-14-barranquenho): OVOS blog

---
**Read next:** [Language Support Tables](lang-support-tables.md) · [Language Selection (internals)](lang-selection.md)
**Related:** [Customizing Language Resources](lang-customization.md) · [Translation Plugins](translation-plugins.md) · [Contributing Translations](ovos-localize-tutorial.md) · [Transformers Overview](transformer-plugins.md)
