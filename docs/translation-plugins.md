# Language Detection and Translation Plugins

!!! abstract "In a nutshell"
    These add-ons give OVOS two related abilities. They work out *what language* some text is in, and they *rewrite* text from one language into another. They power features like [Bidirectional Translation](bidirectional-translation.md), so your assistant can understand and reply across languages. Some run entirely offline on your device. Others call an online service. You pick which ones to use in the configuration file. See the [Glossary](glossary.md) for terms.

!!! tip
    Just want translation to work? See [Bidirectional Translation](bidirectional-translation.md). This page covers the plugin internals.

Language detection and translation plugins let OVOS identify the language of a piece of text and translate it between languages. They are the building blocks used by features like [Bidirectional Translation](bidirectional-translation.md), and they can also be called directly from your own code.

**New here?** Two separate jobs are involved:

- **Detection** decides *what language* a string is in (e.g. `"Hola"` → `es`).
- **Translation** rewrites a string *into another language* (e.g. `"Hola"` → `"Hello"`).

A single package may ship one or both. In `mycroft.conf` you select them under the `"language"` section with `"detection_module"` (a detect plugin) and `"translation_module"` (a translate plugin).

!!! tip "Recommended: NLLB + fastText (offline)"
    For offline translation, the recommended default is `ovos-translate-plugin-nllb` (NLLB-200)
    paired with `ovos-lang-detector-fasttext-plugin` for offline detection. Both run fully
    on-device once their models are downloaded. Use `ovos-google-translate-plugin` or
    `ovos-translate-plugin-server` when translation coverage or quality matters more than
    keeping text off the network. They are also a good choice when the device lacks the
    compute budget to run NLLB locally.

## Available Language Plugins

| Plugin (entry-point name) | Detect | Translate | Type | License | Notes | Maturity |
|--------|--------|-----------|------|---------|-------|-------|
| `ovos-translate-plugin-server` ([repo](https://github.com/OpenVoiceOS/ovos-translate-server-plugin)) | yes | yes | API (self/community hosted) | Apache-2.0 | Client for [ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server). Ships a built-in public-server list with failover. Detection is a separate entry-point, `ovos-lang-detector-plugin-server`. | Stable |
| `ovos-translate-plugin-nllb` ([repo](https://github.com/OpenVoiceOS/ovos-translate-plugin-nllb)) | no | yes | FOSS (Offline) | Apache-2.0 | NLLB-200 via CTranslate2. Downloads a model the first time. | Stable |
| `ovos-lang-detector-fasttext-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-lang-detector-fasttext-plugin)) | yes | no | FOSS (Offline) | Apache-2.0 | fastText language identification. | Stable |
| `ovos-lang-detector-classics-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-lang-detector-classics-plugin)) | yes | no | FOSS (Offline) | no license file | A *voter* (`ovos-lang-detector-plugin-voter`) that averages classic detectors. By default it uses cld2, langdetect and fastlang. cld3 is also available as a separate sub-plugin. | Stable |
| `ovos-google-translate-plugin` ([repo](https://github.com/OpenVoiceOS/ovos-google-translate-plugin)) | yes | yes | API (free) | Apache-2.0 (cloud service, separate Google terms) | Translate (`ovos-google-translate-plugin`) and detect (`ovos-google-lang-detector-plugin`) are separate entry-points. | Stable |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).

!!! note "License and Maturity are independent axes"
    The **License** column reports what the repository itself declares. "No
    license file" just means no SPDX license was found, not that the code is unmature.
    The **Maturity** column reports repository health (age, activity, issues/PRs, docs).
    A plugin can be **Mature** and still ship no license file. A plugin can be **Stable**
    with a permissive license but thin docs. Do not read one column as implying the other.

> **Heads up:** the package repo name, the pip name, and the **entry-point name you put in config** are not always the same. Configure plugins by their *entry-point name* (for example `ovos-translate-plugin-server`, not the repo `ovos-translate-server-plugin`). The names in the table above are entry-point names.

### Configuring `ovos-translate-plugin-server`

If you don't set anything, the client shuffles through its built-in public-server list. It fails over to the next server whenever one errors or times out. To point it at your own [ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server) instance(s), set `host`. Use a single URL, or a list of URLs for failover:

```json
{
  "language": {
    "translation_module": "ovos-translate-plugin-server",
    "detection_module": "ovos-lang-detector-plugin-server",
    "ovos-translate-plugin-server": {
        "host": ["https://my-nllb.example", "https://backup-nllb.example"],
        "timeout": 5,
        "skip_detection": false
    }
  }
}
```

- **`host`**: a URL string or a list of URLs. When a list, the client tries each in order on failure. Omit it to use the built-in public servers (tried in random order to spread load).

- **`timeout`**: per-request timeout in seconds (default `5`).

- **`skip_detection`** (translator only): when `true`, the plugin skips the pre-translate `/detect/{text}` round-trip. The server then infers the source language directly from the `/translate/{target}/{text}` endpoint. This halves the request count when the server can self-detect. Defaults to `false`.

---

## Technical Explanation

OVOS provides two base classes for language processing, both in `ovos_plugin_manager.templates.language`: `LanguageDetector` and `LanguageTranslator`. Each is constructed with a `config` dict (the plugin's section from `mycroft.conf`), exposed as `self.config`.

### Language Detector Interface

```python
from ovos_plugin_manager.templates.language import LanguageDetector

class LanguageDetector:
    def detect(self, text: str) -> str:
        """Return the single best language code (e.g. 'en')."""

    def detect_probs(self, text: str) -> Dict[str, float]:
        """Return a {language_code: probability} dict."""
```

### Language Translator Interface

```python
from ovos_plugin_manager.templates.language import LanguageTranslator

class LanguageTranslator:
    def translate(self, text: str, target: Optional[str] = None,
                  source: Optional[str] = None) -> str:
        """Abstract. Every backend implements this. Translate `text` to
        `target`; if `source` is None the plugin detects it."""

    @classproperty
    def available_languages(cls) -> Set[str]:
        """Languages this backend supports (may be empty if unknown/dynamic)."""
```

> **Gotcha (advanced):** `available_languages` is a `classproperty`. Several real plugins return an empty set when the backend's language list is dynamic or unknown (for example `ovos-translate-plugin-server` and `ovos-google-translate-plugin`). Don't assume it is populated.

## Creating Your Own Plugin

### 1. Implementation Template (Translator)

```python
from ovos_plugin_manager.templates.language import LanguageTranslator

class MyTranslator(LanguageTranslator):
    def translate(self, text, target=None, source=None):
        target = target or self.config.get("lang")
        # Implement your translation logic here
        return self.api.translate(text, target, source)

    @property
    def available_languages(self):
        return {"en", "es", "fr", "de"}
```

### 2. Registration

Register your plugin in `pyproject.toml` under the correct entry-point groups. Translators use `opm.lang.translate`. Detectors use `opm.lang.detect`:

```toml
[project.entry-points."opm.lang.translate"]
my-translator = "my_package.module:MyTranslator"

[project.entry-points."opm.lang.detect"]
my-detector = "my_package.module:MyDetector"
```

> The legacy Neon groups `neon.plugin.lang.translate` / `neon.plugin.lang.detect` are still honoured as aliases by `ovos-plugin-manager` (this is why a plugin like `ovos-lang-detector-fasttext-plugin` keeps working), but new plugins **should** register under the `opm.lang.*` groups.

## Standalone Usage

```python
from ovos_plugin_manager.language import find_tx_plugins, find_lang_detect_plugins

# Translation
tx_plugins = find_tx_plugins()
translator = tx_plugins["ovos-google-translate-plugin"]()
print(translator.translate("Hello", target="es"))

# Detection
detect_plugins = find_lang_detect_plugins()
detector = detect_plugins["ovos-lang-detector-fasttext-plugin"]()
print(detector.detect("Hola, como estas?"))
```
