# linguonnx Language Plugins

!!! abstract "In a nutshell"
    One package gives OVOS offline language detection and offline translation. It runs the models on your own machine, so text never leaves the device. It reaches 593 languages by routing a translation through one or two models instead of holding a single large one. This page shows how to install it, how to configure it, and which settings bound the memory it uses. See [Translation Plugins](translation-plugins.md) and the [Glossary](glossary.md).

`ovos-plugin-linguonnx` ships two plugins in one package:

| Plugin id (use this in config) | Entry-point group | Job |
|---|---|---|
| `ovos-lang-detect-plugin-linguonnx` | `opm.lang.detect` | Detect the language of a string |
| `ovos-translate-plugin-linguonnx` | `opm.lang.translate` | Translate a string between languages |

Both run on ONNX Runtime. Neither needs torch. Both work offline after the models are in the local cache.

## Installation

```bash
pip install --pre ovos-plugin-linguonnx
```

Models download from HuggingFace on first use. Constructing a plugin downloads nothing. The first `detect()` or `translate()` call does the download.

## Configuration

Select both plugins in the `language` section of `mycroft.conf`. Put each plugin's own settings in a sub-section named after the plugin id:

```json
{
  "language": {
    "detection_module": "ovos-lang-detect-plugin-linguonnx",
    "translation_module": "ovos-translate-plugin-linguonnx",
    "ovos-lang-detect-plugin-linguonnx": {
      "collapse_varieties": true
    },
    "ovos-translate-plugin-linguonnx": {
      "precision": "int8",
      "max_model_mb": 500,
      "oversize_fallback": true,
      "count_cached_as_free": false,
      "max_concurrent_translations": 2
    }
  }
}
```

The plugin id appears twice on purpose. `detection_module` and `translation_module` say *which* plugin to load. The sub-section of the same name holds the settings that plugin receives. A setting placed anywhere else never reaches the plugin.

Every setting is optional. A setting you leave out is not defaulted by the plugin. It is simply not passed, so the `linguonnx` library stays the single source of truth for the default.

## Translation Settings

| Setting | Default | What it does |
|---|---|---|
| `prefer` | `"fewest_hops"` | Route ranking. `"dedicated"` prefers a bilingual model over a multilingual one, even at the cost of an extra hop. |
| `max_hops` | `2` | How many models a route may chain. `1` allows direct models only. `2` allows one pivot language. |
| `precision` | `"int8"` | `"int8"` uses the quantized models. `"fp32"` uses the full ones, at roughly four times the disk and memory. `null` allows both. |
| `max_model_mb` | unset | Size cap, in MB, on a single model in the routing graph. |
| `oversize_fallback` | `false` | Turns `max_model_mb` from a filter into a preference. |
| `count_cached_as_free` | picked by the library | Whether a model already in the local cache is exempt from `max_model_mb`. |
| `model_cache_size` | `4` | How many loaded models stay in memory, least-recently-used evicted first. |
| `max_loaded_mb` | unset | Byte budget, in MB, for the loaded-model cache. |
| `max_concurrent_translations` | unset | How many translations may run at once. |
| `exclude_flagged` | `false` | Drops any model the `linguonnx` quality sweep flags. |
| `min_chrf` | unset | Drops any model scoring below this chrF against FLORES-200. |

### The size cap prefers small models

`max_model_mb` is a routing filter, not a download guard. On its own it is strict: a language that lives only inside an oversized model becomes unroutable.

Set `oversize_fallback: true` to make the cap a preference instead. Every pair a model under the cap can serve is still served by that small model. Only a pair that nothing under the cap covers escalates to the smallest sufficient model above the cap. The cap then shrinks load latency without deleting the long tail of languages.

With `max_model_mb: 500` and `count_cached_as_free: false`, `en -> ca` routes through a 157 MB `opus-mt` model instead of a 1.7 GB multilingual one. `en -> cv` (Chuvash) has no model under 500 MB at all, so the fallback escalates to the smallest model that covers it.

!!! warning "`LINGUONNX_MAX_DOWNLOAD_MB` ceilings the escalation"
    `LINGUONNX_MAX_DOWNLOAD_MB` is an environment variable, not a config key. It defaults to `8192` (MB) and caps how large a model the escalation may fetch. Set it at or near your `max_model_mb` value and the escalation collapses: routable languages on a 500 MB budget drop from 593 (with `oversize_fallback` escalating past the cap) to 251, the same result as no fallback at all. Leave it at the default unless you deliberately want to bound the fallback.

### Bounding memory

`max_concurrent_translations` is the only setting that bounds peak memory. A model that a thread is decoding with is resident because that thread holds it, not because the cache kept it, so no cache setting can reach it. Translation endpoints are commonly served from a threadpool, so peak memory otherwise scales with whatever that pool admits. Requests over the limit wait for a slot.

`model_cache_size` and `max_loaded_mb` bound what the cache *retains*. Four Marian models are about 1.4 GB. Four MADLAD-400-3B models are about 20 GB, so a count alone is a poor bound on a mixed graph. For the per-model sizes, see the [`linguonnx` model list](https://github.com/TigreGotico/linguonnx/blob/dev/docs/models.md).

## Detection Settings

| Setting | Default | What it does |
|---|---|---|
| `model` | `"glotlid-int8"` | Which GlotLID export to run. |
| `collapse_varieties` | `true` | Reports the macrolanguage instead of the detected variety. |
| `min_confidence` | `0.0` | Below this score, `detect()` returns the configured `lang` instead of a guess. |

`collapse_varieties` matters because OVOS resolves a language tag with the `langcodes` tag distance and accepts a candidate at distance 10 or less. That bound handles region and script subtags (`ar-SA` resolves to `ar` at distance 4) and even a member measured directly against its macrolanguage (`arz` sits at exactly 10 from `ar`, so it still resolves). It does not stretch to more distant varieties: `ajp` and `yue` sit at 64 from `ar` and `zh`, so an uncollapsed variety like these is discarded rather than degraded, and the session keeps its previous language.

Set `collapse_varieties: false` when the caller reads the dialect itself, for example to log it or to route on it.

## Public Instance

A community instance of [`ovos-translate-server`](translate-server.md) runs these plugins at `https://translate.openvoiceos.pt`. Point [`ovos-translate-plugin-server`](translation-plugins.md#configuring-ovos-translate-plugin-server) at that bare base URL with `host` (the server's root path serves no page of its own — check it is up via [`/status`](https://translate.openvoiceos.pt/status)).

--8<-- "snippets/community-servers.md"

## Further Reading

The plugin repository documents detection, translation, routing and error handling in full:

- [`ovos-plugin-linguonnx`](https://github.com/OpenVoiceOS/ovos-plugin-linguonnx) — the plugins.
- [`linguonnx`](https://github.com/TigreGotico/linguonnx) — the engine, the model list, and the routing rules.

---
**Read next:** [Translation Plugins](translation-plugins.md)
**Related:** [Bidirectional Translation](bidirectional-translation.md) · [Translate Server](translate-server.md) · [Configuration Management](config.md)
