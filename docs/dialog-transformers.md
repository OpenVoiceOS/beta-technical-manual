# Dialog Transformers

!!! abstract "In a nutshell"
    These plugins give the assistant's written reply one last edit just before it's read aloud. Like a proofreader catching the text on its way out, they can adjust the tone, simplify the wording, or translate it. Because this happens in one shared place, it applies to every feature at once without changing any of them. See [Transformer Plugins](transformer-plugins.md) and the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    Dialog transformers are the **`dialog` chain** of **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §3.5** (a formal [architecture spec](architecture-specs.md)). The spec's post-skill, pre-TTS injection point receives the rendered dialog **string**, an optional `lang`, and the full `Message.context`. It may rewrite the string entirely (translate, persona, simplify, length-cap) and mutate `lang`/context. The spec names setting a `voice_id` context hint (for a downstream TTS transformer to act on) as a common case. Rewriting and translation belong here (against the text), not in the `tts` chain (against the audio). **Ordering:** the chain runs by **ascending** `priority` (lowest first), matching the spec.

**Dialog Transformers** in OpenVoiceOS (OVOS) are plugins that modify or enhance text responses just before they are sent to the [Text-to-Speech](tts-plugins.md) ([TTS](tts-plugins.md)) engine. This lets the assistant's speech adjust dynamically, such as altering tone, simplifying language, or translating content, without requiring changes to individual skills.

---

## How They Work

1. **Intent Handling**: After a user's utterance is processed and an intent is matched, the corresponding skill generates a textual response.


2. **Transformation Phase**: Before this response is vocalized, it passes through any active dialog transformers.


3. **TTS Output**: The transformed text is then sent to the TTS engine for audio synthesis.

This pipeline ensures that all spoken responses can be uniformly modified according to the desired transformations.

Dialog transformers run inside the **ovos-audio** service, in the `speak` handling path, just before text is handed to the TTS engine. Every loaded transformer's `transform(dialog, context)` is called in turn, each receiving the previous one's output. Transformers run in **ascending priority** order: a plugin with a lower `priority` value runs first. Responses from blacklisted skills can be skipped via the service `blacklisted_skills` config.

---

## Configuration

To enable dialog transformers, add them to your `mycroft.conf` file under the `dialog_transformers` section. An optional `"order"` list of plugin names in the same section overrides priority ordering entirely: plugins listed there run in that exact order (and are enabled even without their own config entry), while any loaded plugin absent from the list is not run.

```jsonc
"dialog_transformers": {
  "plugin_name": {
    // plugin-specific configuration
  }
}

```

Replace `"plugin_name"` with the identifier of the desired plugin and provide any necessary configuration parameters.

---

## Available Dialog [Transformer](transformer-plugins.md) Plugins

### **OVOS Dialog Normalizer Plugin**

* **Purpose**: Prepares text for TTS by expanding contractions, expanding title abbreviations (`Dr.`→`Doctor`, `Mr.`→`Mister`, `Prof.`→`Professor`), normalizing currency (`€`→`euros`), and converting digits to spoken words, ensuring clearer pronunciation.


* **Multilingual coverage**: Contractions are English-only, while title abbreviations are defined per language (en/ca/es/pt/gl/fr/it/nl/de). Numbers are pronounced via `ovos-number-parser`, falling back to `unicode-rbnf` for languages it doesn't yet cover. A few language-specific rules exist too (for example, `ºC`→`graos centígrados` for Galician).


* **Example**:


    * Input: `"I'm 5 years old."`


    * Output: `"I am five years old."`


* **Installation**:

```bash
pip install ovos-dialog-normalizer-plugin

```

* **Configuration**:

```jsonc
"dialog_transformers": {
  "ovos-dialog-normalizer-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-dialog-normalizer-plugin)

---

### **OVOS OpenAI Dialog Transformer Plugin**

* **Purpose**: Uses OpenAI's API to rewrite responses based on a specified persona or tone.


* **Example**:


    * Rewrite Prompt: `"Explain like I'm five"`


    * Input: `"Quantum mechanics is a branch of physics that describes the behavior of particles at the smallest scales."`


    * Output: `"Quantum mechanics helps us understand really tiny things."`


* **Installation**:

```bash
pip install ovos-openai-plugin

```

* **Configuration**:

```jsonc
"dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {
      "rewrite_prompt": "Explain like I'm five"
    }
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-openai-plugin)

---

### **OVOS Bidirectional Translation Plugin**

* **Purpose**: Translates responses to match the user's language, enabling multilingual interactions.


* **Features**:


    * Ships two cooperating plugins: an utterance transformer (`ovos-utterance-translation-plugin`, class `UtteranceTranslator`) that translates incoming user speech, and a dialog transformer (`ovos-dialog-translation-plugin`, class `DialogTranslator`) that translates the assistant's response back into the user's language.


    * Together they enable round-trip multilingual interactions.


* **Installation**:

```bash
pip install ovos-bidirectional-translation-plugin

```

* **Configuration** (the dialog half registers under the entry-point name `ovos-dialog-translation-plugin`):

```jsonc
"dialog_transformers": {
    "ovos-dialog-translation-plugin": {}
}

```

* **Source**: [GitHub Repository](https://github.com/OpenVoiceOS/ovos-bidirectional-translation-plugin)

---

## Writing your own Dialog Transformer

Subclass `DialogTransformer` (`ovos_plugin_manager.templates.transformers`) and
override its `transform(dialog, context=None) -> Tuple[str, dict]` method. Register
the class under the `opm.transformer.dialog` entry-point group.

**Create a Python Class**:

```python
from typing import Tuple
from ovos_plugin_manager.templates.transformers import DialogTransformer


class MyCustomTransformer(DialogTransformer):
    def __init__(self, name="my-custom-transformer", priority=10, config=None):
        super().__init__(name, priority, config)

    def transform(self, dialog: str, context: dict = None) -> Tuple[str, dict]:
        """
        Optionally transform passed dialog and/or return additional context
        :param dialog: str utterance to mutate before TTS
        :returns: tuple of (mutated dialog, context)
        """
        # Modify the dialog as needed
        modified_dialog = dialog.upper()
        return modified_dialog, context
```

The base `__init__` signature is `__init__(self, name, priority=50, config=None)`. When `config` is not passed, the base class auto-loads it from `mycroft.conf` under `dialog_transformers[name]`. A lower `priority` runs earlier in the chain; the
default is 50.

**Register as a Plugin**. A full `pyproject.toml` for a standalone plugin package:

```toml
[project]
name = "ovos-dialog-transformer-mycustom"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.transformer.dialog"]
"my-custom-transformer" = "my_module:MyCustomTransformer"
```

An `opm.transformer.dialog.config` group is also available, for a dict of config
metadata an installer or GUI can read. It is optional; add it once the plugin has
settings worth advertising.

**Install and Configure**:
After installation, add your transformer to the `mycroft.conf`:

```jsonc
"dialog_transformers": {
  "my-custom-transformer": {}
}

```

### Test it without OVOS

`DialogTransformer` subclasses are plain classes, so a unit test needs no bus. Pass an
explicit `config` though: when it is omitted, the base `__init__` reads the plugin's section
from the `Configuration()` singleton, which touches the on-disk config layers:

```python
from my_module import MyCustomTransformer

transformer = MyCustomTransformer(config={})
dialog, context = transformer.transform("hello world")
assert dialog == "HELLO WORLD"
```

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.dialog_transformers import find_dialog_transformer_plugins

print(find_dialog_transformer_plugins())
# {'my-custom-transformer': <class 'my_module.MyCustomTransformer'>}
```

### Checklist before you publish

1. `transform()` accepts a `dialog: str` and returns `(dialog, context)`.
2. `__init__` hardcodes the plugin `name` and forwards `name`, `priority`, `config`
   to `super().__init__()`.
3. The entry-point group in `pyproject.toml` is `opm.transformer.dialog`.
4. A unit test calls `transform()` directly, with no OVOS services running.
5. `find_dialog_transformer_plugins()` discovers the installed plugin under the
   expected name.

---
**Read next:** [Audio Transformers](audio-transformers.md)
**Related:** [Intent Transformers](intent-transformers.md) · [Dialog & Statements](statements.md) · [SSML](ssml.md)

