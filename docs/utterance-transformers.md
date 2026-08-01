# Utterance Transformers

!!! abstract "In a nutshell"
    An "utterance" is simply the text of what you said, once the assistant has transcribed your speech into words. These plugins get to fix and tidy that text *before* the assistant tries to understand it — for example correcting misheard words, smoothing out the phrasing, or handling more than one language — so it matches your request more reliably. See [Transformer Plugins](transformer-plugins.md) and the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    Utterance transformers are the **`utterance` chain** of **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §3.2** (a formal [architecture spec](architecture-specs.md)). The spec's post-STT, pre-intent injection point receives the **non-empty list of candidate transcriptions** (`utterances[0]` is the primary candidate, later indices are n-best alternatives), an optional `lang`, and the full `Message.context`; it returns a possibly rewritten list plus mutated `lang`/context. Returning an empty list signals "no plausible transcription"; returning empty **with** `canceled: true` + `cancel_reason` invokes utterance cancellation (§3.2, §8). **Ordering:** the chain runs by **ascending** `priority` (lowest first), matching the spec.

**Utterance Transformers** in OpenVoiceOS (OVOS) are plugins that process and modify user utterances immediately after speech-to-text ([STT](stt-plugins.md)) conversion but before intent recognition. They serve to enhance the accuracy and flexibility of the assistant by correcting errors, normalizing input, and handling multilingual scenarios.

---

## How They Work

1. **Speech Recognition**: The user's spoken input is transcribed into text by the STT engine.


2. **Transformation Phase**: The transcribed text passes through any active utterance transformers.


3. **Intent Recognition**: The transformed text is then processed by the intent recognition system to determine the appropriate response.

This sequence ensures that any necessary preprocessing is applied to the user's input, improving the reliability of intent matching.

Utterance transformers register under the `opm.transformer.text` entry-point group and subclass `UtteranceTransformer` from `ovos_plugin_manager.templates.transformers`. They are loaded and chained by `UtteranceTransformersService` in `ovos-core`.

---

## Configuration

A transformer is only loaded if its plugin name appears under the `utterance_transformers` section of your `mycroft.conf`; an empty `{}` is enough to enable it. Set `"active": false` to load-skip it. When several are active they run sorted by `priority` (lowest first), each operating on the output of the previous.

```jsonc
"utterance_transformers": {
  "plugin_name": {
    // plugin-specific configuration
  }
}

```

Replace `"plugin_name"` with the identifier of the desired plugin and provide any necessary configuration parameters.

---

## Available Utterance [Transformer](transformer-plugins.md) Plugins

### **OVOS Utterance Normalizer Plugin**

* **Purpose**: Standardizes user input by expanding contractions, converting numbers to words, and removing unnecessary punctuation.


* **Example**:


    * Input: `"I'm 5 years old."`


    * Output: `"I am five years old"`


* **Installation**:

```bash
pip install ovos-utterance-normalizer

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-utterance-normalizer": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-normalizer)

---

### **OVOS Utterance Corrections Plugin**

* **Purpose**: Applies predefined corrections to common misrecognitions or user-defined replacements to improve intent matching.


* **Features**:


    * Full utterance replacements via `corrections.json`


    * Word-level replacements via `word_corrections.json`


    * Regex-based pattern replacements via `regex_corrections.json`


* **Example**:


    * Input: `"shalter is a switch"`


    * Output: `"schalter is a switch"`


* **Installation**:

```bash
pip install ovos-utterance-corrections-plugin

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-utterance-corrections-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-corrections-plugin)

---

### **OVOS Utterance Cancel Plugin**

* **Purpose**: Detects phrases indicating the user wishes to cancel or ignore the current command and prevents further processing.


* **Example**:


    * Input: `"Hey Mycroft, can you tell me the... umm... oh, nevermind that"`


    * Output: *Utterance is discarded; no action taken*


* **Installation**:

```bash
pip install ovos-utterance-plugin-cancel

```

* **Configuration** (the installed package is `ovos-utterance-plugin-cancel`, but its registered plugin name is `ovos-utterance-cancel-plugin`):

```jsonc
"utterance_transformers": {
  "ovos-utterance-cancel-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel)

---

### **OVOS Bidirectional Translation Plugin**

* **Purpose**: Detects the language of the user's input and translates it to the assistant's primary language if necessary, enabling multilingual interactions.


* **Features**:


    * Language detection and translation to primary language


    * Optional translation of responses back to the user's language


* **Example**:


    * Input: `"¿Cuál es el clima hoy?"` (Spanish)


    * Output: `"What is the weather today?"` (translated to English for processing)


* **Installation**:

```bash
pip install ovos-bidirectional-translation-plugin

```

* **Configuration** (the utterance half registers under the entry-point name `ovos-utterance-translation-plugin`):

```jsonc
"utterance_transformers": {
    "ovos-utterance-translation-plugin": {
      "verify_lang": true,
      "ignore_invalid_langs": true
    }
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)

---

### **OVOS Transcription Validator Plugin**

* **Purpose**: Uses an OpenAI-compatible LLM to judge whether an STT transcription is a
  plausible utterance at all, filtering out garbled or nonsensical speech-to-text output
  before it reaches intent matching.

!!! note
    This plugin makes a network call per utterance (to the configured LLM endpoint), so
    it trades latency for robustness against noisy STT.

* **Installation**:

```bash
pip install ovos-transcription-validator-plugin

```

* **Configuration**:

```jsonc
"utterance_transformers": {
  "ovos-transcription-validator-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-transcription-validator-plugin)

---

## Writing your own Utterance Transformer

Subclass `UtteranceTransformer` (`ovos_plugin_manager.templates.transformers`) and
override its `transform(utterances, context=None) -> Tuple[List[str], dict]` method.
Register the class under the `opm.transformer.text` entry-point group.

**Create a Python Class**:

```python
from typing import List, Tuple, Optional, Dict, Any
from ovos_plugin_manager.templates.transformers import UtteranceTransformer

class MyCustomTransformer(UtteranceTransformer):
    def __init__(self, name: str = "my-custom-transformer", priority: int = 50,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, priority, config)

    def transform(self, utterances: List[str],
                  context: dict = None) -> Tuple[List[str], dict]:
        # utterances is a list of strings; return (utterances, extra_context)
        context = context or {}
        modified_utterances = [u.lower() for u in utterances]
        return modified_utterances, context

```

The base `UtteranceTransformer.__init__(self, name, priority=50, config=None)` requires `name`,
and the loader only ever calls a transformer plugin as `plug(config=plugin_config)`. So a plugin
must override `__init__` to supply its own `name`, as shown above, and must pass `name`,
`priority`, and `config` through to `super().__init__()` so the base class still sees them.

The second return value is *additional* context that gets merged into the message context, not a
replacement for it.

### Config-driven priority

The loader passes only the plugin's config block into `__init__`, not a separate `priority`
argument. To let a deployment override priority from `mycroft.conf` instead of the hard-coded
default, read it back out of `self.config` after calling `super().__init__()`:

```python
class MyCustomTransformer(UtteranceTransformer):
    def __init__(self, name: str = "my-custom-transformer", priority: int = 50,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, priority, config)
        self.priority = self.config.get("priority", self.priority)
```

```jsonc
"utterance_transformers": {
  "my-custom-transformer": {"priority": 10}
}
```

Without that explicit `self.config.get("priority", ...)` line, a `"priority"` key in
`mycroft.conf` is inert — the loader does not read it back into `self.priority` on its own.
The default `priority` is 50; a lower number runs earlier in the chain.

!!! note "Where `lang` fits"
    The spec box above describes the transform as receiving `utterances`, `lang`, and
    `Message.context`; in the installed `UtteranceTransformer.transform()` signature
    `lang` isn't a separate parameter — it travels inside the `context` dict (e.g.
    `context.get("lang")`), matching the class actually shipped in
    `ovos_plugin_manager.templates.transformers`.

**Register as a Plugin**. A full `pyproject.toml` for a standalone plugin package:

```toml
[project]
name = "ovos-utterance-transformer-mycustom"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.transformer.text"]
my-custom-transformer = "my_module:MyCustomTransformer"
```

An `opm.transformer.text.config` group is also available, for a dict of config
metadata an installer or GUI can read. It is optional; add it once the plugin has
settings worth advertising.

**Install and Configure**:
After installation, add your transformer to the `mycroft.conf`:

```jsonc
"utterance_transformers": {
 "my-custom-transformer": {}
}

```

### Test it without OVOS

`UtteranceTransformer` subclasses are plain classes, so a unit test needs no bus and
no `Configuration`:

```python
from my_module import MyCustomTransformer

transformer = MyCustomTransformer()
utterances, context = transformer.transform(["Hello World"])
assert utterances == ["hello world"]
```

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.text_transformers import find_utterance_transformer_plugins

print(find_utterance_transformer_plugins())
# {'my-custom-transformer': <class 'my_module.MyCustomTransformer'>}
```

### Checklist before you publish

1. `transform()` accepts `utterances: List[str]` and returns `(utterances, context)`.
2. `__init__` hardcodes the plugin `name` and forwards `name`, `priority`, `config` to
   `super().__init__()`.
3. The entry-point group in `pyproject.toml` is `opm.transformer.text`.
4. A unit test calls `transform()` directly, with no OVOS services running.
5. `find_utterance_transformer_plugins()` discovers the installed plugin under the
   expected name.

---
**Read next:** [Intent Transformers](intent-transformers.md)
**Related:** [Transformers Overview](transformer-plugins.md) · [Language Selection](lang-selection.md) · [Bidirectional Translation](bidirectional-translation.md)
