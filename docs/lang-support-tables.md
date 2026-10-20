# Language Support Tables

!!! abstract "In a nutshell"
    This page holds the per-language STT/TTS/parser coverage tables for OVOS: which languages have a bundled offline speech model, and which have a number/date parser module. Use it to look up one language. For the narrative on how language support works and how to improve it, see [Language Support](lang-support.md).

---

## Supported Languages

`ovos-config autoconfigure` reads the recommendation files in the `recommends/` directory of
your installed `ovos-config`. These files are the authoritative list. The tables below show
what each release channel ships.

### Stable channel

The stable channel installs `ovos-config` 1.2.2. It recommends offline speech recognition for
11 languages: `ca-es`, `da-dk`, `de-de`, `en-us`, `es-es`, `eu-es`, `fr-fr`, `gl-es`, `it-it`,
`nl-nl` and `pt-pt`. It has no `--gpu` tier.

| Offline STT plugin | Languages |
|---|---|
| `ovos-stt-plugin-citrinet` | `ca-es`, `de-de`, `fr-fr`, `it-it`, `nl-nl` |
| `ovos-stt-plugin-fasterwhisper` | `da-dk`, `en-us`, `pt-pt` |
| `ovos-stt-plugin-fasterwhisper-zuazo` | `es-es`, `eu-es`, `gl-es` |

### Testing channel

The testing channel installs `ovos-config` 2.1.1. It covers the same 11 languages and adds a
`--gpu` tier.

| Tier | STT plugin | Languages |
|---|---|---|
| Offline | `ovos-stt-plugin-citrinet` | `ca-es`, `de-de`, `en-us`, `es-es`, `fr-fr`, `it-it`, `nl-nl`, `pt-pt` |
| Offline | `ovos-stt-plugin-fasterwhisper` | `da-dk`, `eu-es`, `gl-es` |
| GPU | `ovos-stt-plugin-fasterwhisper` | every language except `eu-es` |
| GPU | `ovos-stt-plugin-HiTZ` | `eu-es` |

### Alpha channel

!!! warning "Alpha channel only"
    The alpha `ovos-config` recommends offline speech recognition for 69 languages and a GPU
    tier for 60. Both tiers use [`ovos-stt-plugin-onnx-asr`](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr),
    one plugin that runs every model architecture in the table.

    `int8` next to a model means
    the recommendation uses a quantized CPU build. The GPU tier sets `use_cuda: true`.

    Where the table shows offline TTS voices, the recommendation is
    [`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx) with one pinned
    voice for each gender listed. A single-speaker Facebook MMS voice counts as male.
    `autoconfigure` adds a voice only when its gender is known.

    "none" means the release has no recommendation for that tier. `autoconfigure` skips that
    part of the configuration and tells you so. Use an online STT plugin, or configure a
    multilingual model by hand, for example
    [`ovos-stt-plugin-server`](stt-plugins-reference.md#ovos-stt-server-plugin) pointed at a
    [self-hosted STT server](stt-server.md).

    | Language | Offline STT model | GPU STT model | Offline TTS voices |
    |---|---|---|---|
    | **arb** | `OpenVoiceOS/stt_ar_fastconformer_hybrid_large_pcd_v1.0_onnx` | none | female, male |
    | **arg** | none | none | female, male |
    | **as-IN** | `OpenVoiceOS/ai4bharat-indicconformer-as-onnx` | `OpenVoiceOS/ai4bharat-indicconformer-as-onnx` | male |
    | **ast** | none | none | female, male |
    | **be-BY** | `OpenVoiceOS/nvidia-be-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-be-conformer-transducer-large-onnx` | none |
    | **bn-IN** | `OpenVoiceOS/ai4bharat-indicconformer-bn-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-bn-onnx` | male |
    | **brx-IN** | `OpenVoiceOS/ai4bharat-indicconformer-brx-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-brx-onnx` | none |
    | **ca-ba** | none | none | female, male |
    | **ca-ES** | `OpenVoiceOS/stt-ca-es-conformer-transducer-large-onnx` | `OpenVoiceOS/whisper-large-v3-ca-punctuated-3370h-onnx` | female, male |
    | **ca-nw** | none | none | female, male |
    | **ca-va** | none | none | female, male |
    | **da-DK** | `OpenVoiceOS/nvidia-parakeet-rnnt-110m-da-dk-onnx` (int8) | `nemo-canary-1b-v2` | male |
    | **de-DE** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `nemo-canary-1b-v2` | female, male |
    | **doi-IN** | `OpenVoiceOS/ai4bharat-indicconformer-doi-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-doi-onnx` | none |
    | **en-GB** | none | none | female, male |
    | **en-US** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `nemo-canary-1b-v2` | female, male |
    | **eo** | `OpenVoiceOS/nvidia-eo-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-eo-conformer-transducer-large-onnx` | none |
    | **es-ES** | `OpenVoiceOS/parakeet-rnnt-1.1b-cv17-es-ep18-1270h-onnx` (int8) | `OpenVoiceOS/parakeet-rnnt-1.1b-cv17-es-ep18-1270h-onnx` | female, male |
    | **et-EE** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-et-onnx` (int8) | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-et-onnx` | none |
    | **eus** | `OpenVoiceOS/stt-eu-conformer-transducer-large-onnx` | `OpenVoiceOS/hitz-eu-conformer-transducer-large-v2-onnx` | female, male |
    | **fa-IR** | `OpenVoiceOS/nvidia-fa-fastconformer-hybrid-large-onnx` (int8) | `OpenVoiceOS/nvidia-fa-fastconformer-hybrid-large-onnx` | female, male |
    | **fo-FO** | `OpenVoiceOS/carlosdanielhernandezmena-stt_fo_quartznet15x5_sp_ep163_100h_onnx` | none | none |
    | **fon-BJ** | `OpenVoiceOS/misterkissi-whisper-small-fongbe-onnx` | `OpenVoiceOS/misterkissi-whisper-small-fongbe-onnx` | male |
    | **fr-FR** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `nemo-canary-1b-v2` | female, male |
    | **fy-NL** | none | none | female, male |
    | **ga-IE** | `OpenVoiceOS/misterkissi-w2v2-lg-xls-r-300m-ga-onnx` | `OpenVoiceOS/misterkissi-w2v2-lg-xls-r-300m-ga-onnx` | none |
    | **gl-ES** | `OpenVoiceOS/proxectonos-gl-conformer-ctc-large-onnx` | `onnx-community/whisper-large-v3-turbo` | female, male |
    | **gu-IN** | `OpenVoiceOS/ai4bharat-indicconformer-gu-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-gu-onnx` | male |
    | **hi-IN** | `OpenVoiceOS/ai4bharat-indicconformer-hi-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-hi-onnx` | female, male |
    | **hr-HR** | `OpenVoiceOS/nvidia-hr-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-hr-conformer-transducer-large-onnx` | none |
    | **ht-HT** | `OpenVoiceOS/misterkissi-whisper-small-haitian-creole-onnx` | `OpenVoiceOS/misterkissi-whisper-small-haitian-creole-onnx` | male |
    | **hy-AM** | `OpenVoiceOS/stt_hy_fastconformer_hybrid_large_pc_onnx` | none | none |
    | **is-IS** | `OpenVoiceOS/carlosdanielhernandezmena-stt_is_quartznet15x5_ft_ep56_875h_onnx` | none | none |
    | **it-IT** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `nemo-canary-1b-v2` | female, male |
    | **ja-JP** | `OpenVoiceOS/nvidia-parakeet-tdt_ctc-0.6b-ja-onnx` (int8) | `OpenVoiceOS/nvidia-parakeet-tdt_ctc-0.6b-ja-onnx` | female, male |
    | **ka-GE** | `OpenVoiceOS/stt_ka_fastconformer_hybrid_large_pc_onnx` | none | none |
    | **kab** | `OpenVoiceOS/nvidia-kab-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-kab-conformer-transducer-large-onnx` | male |
    | **kk-KZ** | `OpenVoiceOS/stt_kk_ru_fastconformer_hybrid_large_onnx` | none | none |
    | **kn-IN** | `OpenVoiceOS/ai4bharat-indicconformer-kn-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-kn-onnx` | male |
    | **ko-KR** | `OpenVoiceOS/stt_kr_citrinet1024_PublicCallCenter_1000H_onnx` | none | none |
    | **kok-IN** | `OpenVoiceOS/ai4bharat-indicconformer-kok-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-kok-onnx` | none |
    | **kpo-TG** | `OpenVoiceOS/misterkissi-whisper-small-kposo-onnx` | `OpenVoiceOS/misterkissi-whisper-small-kposo-onnx` | none |
    | **ks-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ks-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-ks-onnx` | none |
    | **mai-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mai-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-mai-onnx` | male |
    | **mg-MG** | `OpenVoiceOS/misterkissi-whisper-small-malagasy-onnx` | `OpenVoiceOS/misterkissi-whisper-small-malagasy-onnx` | male |
    | **ml-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ml-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-ml-onnx` | male |
    | **mni-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mni-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-mni-onnx` | none |
    | **mr-IN** | `OpenVoiceOS/ai4bharat-indicconformer-mr-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-mr-onnx` | male |
    | **mt-MT** | `OpenVoiceOS/carlosdanielhernandezmena-stt_mt_quartznet15x5_sp_ep255_64h_onnx` | none | none |
    | **ne-NP** | `OpenVoiceOS/ai4bharat-indicconformer-ne-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-ne-onnx` | none |
    | **ngl-MZ** | `OpenVoiceOS/misterkissi-whisper-small-lomwe-onnx` | `OpenVoiceOS/misterkissi-whisper-small-lomwe-onnx` | male |
    | **nl-NL** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `nemo-canary-1b-v2` | female, male |
    | **oci** | none | none | female, male |
    | **or-IN** | `OpenVoiceOS/ai4bharat-indicconformer-or-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-or-onnx` | none |
    | **pa-IN** | `OpenVoiceOS/ai4bharat-indicconformer-pa-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-pa-onnx` | male |
    | **pl-PL** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-pl-onnx` | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-pl-onnx` | female, male |
    | **pt-BR** | none | `OpenVoiceOS/whisper-large-v3-pt-onnx` | female, male |
    | **pt-PT** | `nemo-parakeet-tdt-0.6b-v3` (int8) | `OpenVoiceOS/whisper-large-v3-pt-onnx` | female, male |
    | **ru-RU** | `OpenVoiceOS/nvidia-ru-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-ru-conformer-transducer-large-onnx` | female, male |
    | **rw-RW** | `OpenVoiceOS/nvidia-rw-conformer-transducer-large-onnx` (int8) | `OpenVoiceOS/nvidia-rw-conformer-transducer-large-onnx` | male |
    | **sa-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sa-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-sa-onnx` | none |
    | **sat-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sat-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-sat-onnx` | none |
    | **sd-IN** | `OpenVoiceOS/ai4bharat-indicconformer-sd-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-sd-onnx` | none |
    | **sl-SI** | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-sl-onnx` (int8) | `OpenVoiceOS/yuriyvnv-parakeet-tdt-0.6b-sl-onnx` | female |
    | **sn-ZW** | `OpenVoiceOS/misterkissi-whisper-small-shona-onnx` | `OpenVoiceOS/misterkissi-whisper-small-shona-onnx` | male |
    | **st-ZA** | `OpenVoiceOS/misterkissi-whisper-small-sesotho-onnx` | `OpenVoiceOS/misterkissi-whisper-small-sesotho-onnx` | none |
    | **ta-IN** | `OpenVoiceOS/ai4bharat-indicconformer-ta-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-ta-onnx` | male |
    | **te-IN** | `OpenVoiceOS/ai4bharat-indicconformer-te-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-te-onnx` | male |
    | **tig-ER** | `OpenVoiceOS/misterkissi-whisper-small-tigre-onnx` | `OpenVoiceOS/misterkissi-whisper-small-tigre-onnx` | none |
    | **tl-PH** | `OpenVoiceOS/stt-tl-fastconformer-hybrid-large-onnx` | `OpenVoiceOS/stt-tl-fastconformer-hybrid-large-onnx` | male |
    | **tn-ZA** | `OpenVoiceOS/misterkissi-whisper-small-setswana-onnx` | `OpenVoiceOS/misterkissi-whisper-small-setswana-onnx` | none |
    | **uk-UA** | `OpenVoiceOS/stt_ua_fastconformer_hybrid_large_pc_onnx` | none | none |
    | **umb-AO** | `OpenVoiceOS/misterkissi-whisper-small-umbundu-onnx` | `OpenVoiceOS/misterkissi-whisper-small-umbundu-onnx` | none |
    | **ur-PK** | `OpenVoiceOS/ai4bharat-indicconformer-ur-onnx` (int8) | `OpenVoiceOS/ai4bharat-indicconformer-ur-onnx` | male |
    | **uz-UZ** | `OpenVoiceOS/asr-uz-fastconformer-large-onnx` | `OpenVoiceOS/asr-uz-fastconformer-large-onnx` | none |
    | **vai-LR** | `OpenVoiceOS/misterkissi-whisper-small-vai-onnx` | `OpenVoiceOS/misterkissi-whisper-small-vai-onnx` | none |
    | **vi-VN** | `OpenVoiceOS/nvidia-parakeet-ctc-0.6b-vietnamese-onnx` (int8) | `OpenVoiceOS/nvidia-parakeet-ctc-0.6b-vietnamese-onnx` | male |
    | **zh-CN** | `OpenVoiceOS/stt_zh_citrinet_1024_gamma_0_25_onnx` | none | none |

A language that is in neither table has no bundled recommendation. Thai is one example:
`ovos-config` ships no `th-*` recommendation file, so `autoconfigure -l th-th` has nothing to
select. Configure Thai by hand until somebody contributes a recommendation.

---

## Per-language status matrix

The STT and TTS columns summarize the alpha-channel table above. "yes" means a bundled
offline recommendation exists for at least one voice or gender. "partial" means only some of
it exists. "no" means the release has no bundled offline recommendation.

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

Both the number and date parsers cover far more languages than this original matrix,
including several with no offline STT or TTS recommendation, for example Hebrew and Turkish. Adding a language module for parsing text is much cheaper than shipping
a full speech model, so this column tends to run ahead of STT/TTS.

!!! warning "pt-BR has no bundled offline STT"
    Brazilian Portuguese has **no bundled offline CPU speech-to-text recommendation**.
    `ovos-config autoconfigure -l pt-br --offline` skips STT. On the alpha channel,
    `--gpu` recommends a Whisper model for `pt-br`. Without a GPU, use an online STT plugin,
    or configure a multilingual offline model by hand.

A language can have speech support and no parser module. Japanese is one example. The alpha
`ovos-config` recommends offline STT and TTS for `ja-jp`, but `ovos-number-parser` and
`ovos-date-parser` have no Japanese module. Spoken numbers and dates in Japanese are not
parsed until somebody contributes one.

---
**Read next:** [Language Support](lang-support.md)
**Related:** [STT Plugins](stt-plugins.md) · [TTS Plugins](tts-plugins.md) · [Language Selection (internals)](lang-selection.md)
