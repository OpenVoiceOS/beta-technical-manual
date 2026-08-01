# Intent Transformers

!!! abstract "In a nutshell"
    Once the assistant has figured out *what you want* (your "intent," for example, "set a timer"), these plugins can add extra detail or tidy up that request before the matching feature actually runs. It gives you a chance to fill in or pull out the specifics, like spotting names, places, or numbers in what you said, in one shared place instead of repeating that work everywhere. See [Transformer Plugins](transformer-plugins.md) and the [Glossary](glossary.md) for unfamiliar terms.

??? info "📐 Formal specification"
    Intent transformers are the **`intent` chain** of **[OVOS-TRANSFORM-1: Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §3.4** (a formal [architecture spec](architecture-specs.md)). The spec's post-match, pre-dispatch injection point receives the `Match` a pipeline plugin produced ([OVOS-PIPELINE-1 §4.1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md): `skill_id`, `intent_name`, `slots`; the `slots` map's shape is in turn defined by [OVOS-INTENT-3](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)). It may **enrich `Match.slots`**. This is the canonical home for slot and entity injection. It **MUST NOT** change `Match.skill_id` or `Match.intent_name`, since that would re-route the handler. An orchestrator treats such a change as a shape violation and discards it. **Ordering:** the chain runs by **ascending** `priority`. `priority` 1 runs **first**, matching the spec. A chain authored for the opposite, descending, convention is the exact inverse of a conformant one. It must be renumbered, or it runs backwards.

**Intent Transformers** are a pluggable mechanism in OVOS that allow you to enrich or transform intent data **after** an intent is matched by an engine ([Padatious](padatious-pipeline.md), [Adapt](adapt-pipeline.md), etc.), but **before** it is passed to the skill handler.

This is useful for:

* Named Entity Recognition (NER)


* Keyword extraction


* Slot filling


* Contextual enrichment

Each transformer subclasses `IntentTransformer` (`ovos_plugin_manager.templates.transformers`), registers under the `opm.transformer.intent` entry-point group, and operates on the `IntentHandlerMatch` object returned by the matching pipeline. They are loaded and chained by `IntentTransformersService` in `ovos-core` (`ovos_core/transformers.py`).

Transformers run sorted by `priority`, **lowest first**. A transformer with `priority` 1 runs *first*, and later transformers see and may build on its output, per OVOS-TRANSFORM-1 §4. This lets you implement entity logic once instead of in every skill.

---

## Default Transformers

`ovos-core` declares these two plugins as dependencies, so a standard install ships with them present. Each one only *runs* when its plugin name is listed under `intent_transformers` in your config:

| Plugin name (config key)        | PyPI package                | Description                                                                                         | Priority |
|---------------------------------|-----------------------------| -------------------------------------------------------------------------------------------------- | -------- |
| `ovos-keyword-template-matcher` | `keyword-template-matcher`  | Extracts values from `{placeholder}`-style intent templates                                        | 1        |
| `ovos-ahocorasick-ner-plugin`   | `ahocorasick-ner`           | Performs NER using Aho-Corasick keyword matching based on registered entities from skill templates | 5        |

A transformer is loaded only if its plugin name appears under `intent_transformers`. Set `"active": false` to skip it. (Note: `keyword-template-matcher` runs before `ahocorasick-ner`, since 1 < 5.)

---

## Configuration

To enable or disable specific transformers, modify your `mycroft.conf`:

```jsonc
"intent_transformers": {
  "keyword-templates": {
    "active": true
  },
  "ovos-ahocorasick-ner-plugin": {
    "active": false
  }
}

```

Note: `ovos-keyword-template-matcher` is the plugin's entry-point name, used for
installation and discovery. `keyword-templates` is the config key the plugin
registers itself under (`super().__init__("keyword-templates", 1, config)`), and
is the key `intent_transformers` must use.


---

## How It Works

### Example Workflow

1. An utterance matches an intent via Padatious, Adapt, or another engine, producing an `IntentHandlerMatch`.


2. The `IntentService` passes that match to `IntentTransformersService.transform(match)`.


3. Each registered transformer plugin runs its `transform()` method in priority order (lowest first), each receiving the match returned by the previous one.


4. Extracted entities are injected into the intent's `match_data`.


5. The updated `match_data` is passed to the skill via the `Message` object.

### Skill Access

Entities extracted by transformers are made available to your skill in the `message.data` dictionary:

```python
location = message.data.get("location")
person = message.data.get("person")

```

---

## Default Plugins

### `ovos-ahocorasick-ner-plugin`

This plugin builds a per-skill Aho-Corasick automaton using keywords explicitly provided by the developer via registered entities.

> ❗ It will **only match keywords that the skill developer has accounted for**

It does **not** use external data or extract entities generically.

---

### `ovos-keyword-template-matcher`

This plugin parses registered intent templates like:

```text
what's the weather in {location}

```

It uses the template structure to extract `{location}` directly from the utterance.

If the user says "what's the weather in Tokyo", the plugin will populate:

```python
match_data = {
  "location": "Tokyo"
}

```

---

## Writing Your Own Intent [Transformer](transformer-plugins.md)

Subclass `IntentTransformer` and implement `transform()` (the base declares it abstract). The method receives and must return an `IntentHandlerMatch`. Mutate its `match_data` in place and return it. Register under the `opm.transformer.intent` entry-point group.

```python
from ovos_plugin_manager.templates.transformers import IntentTransformer
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch

class MyCustomTransformer(IntentTransformer):
    def __init__(self, config=None):
        super().__init__("my-transformer", priority=10, config=config)

    def transform(self, intent: IntentHandlerMatch) -> IntentHandlerMatch:
        # enrich the matched intent, e.g. inject extracted entities
        intent.match_data["my_entity"] = "value"
        return intent

```

A lower `priority` runs earlier in the chain; the default is 50. Pick a priority that
puts your transformer before or after the entity extractors you depend on or feed
(`ovos-keyword-template-matcher` runs at 1, `ovos-ahocorasick-ner-plugin` at 5).

A full `pyproject.toml` for a standalone plugin package:

```toml
[project]
name = "ovos-intent-transformer-mycustom"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.transformer.intent"]
my-transformer = "my_module:MyCustomTransformer"
```

An `opm.transformer.intent.config` group is also available, for a dict of config
metadata an installer or GUI can read. It is optional; add it once the plugin has
settings worth advertising.

Like other transformer types, intent transformers get the messagebus attached (`bind(bus)`) when loaded, so `self.bus` is available inside `transform()`.

### Test it without OVOS

`IntentTransformer` subclasses are plain classes, so a unit test needs no bus and no
`Configuration`:

```python
from my_module import MyCustomTransformer
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch

transformer = MyCustomTransformer()
match = IntentHandlerMatch(match_type="my_skill:intent", match_data={},
                           skill_id="my_skill", utterance="hello")
result = transformer.transform(match)
assert result.match_data["my_entity"] == "value"
```

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.intent_transformers import find_intent_transformer_plugins

print(find_intent_transformer_plugins())
# {'my-transformer': <class 'my_module.MyCustomTransformer'>}
```

### Checklist before you publish

1. `transform()` accepts and returns an `IntentHandlerMatch`, without changing
   `skill_id` or `intent_name`.
2. `__init__` hardcodes the plugin `name` and forwards it, plus `priority` and
   `config`, to `super().__init__()`.
3. The entry-point group in `pyproject.toml` is `opm.transformer.intent`.
4. A unit test calls `transform()` directly, with no OVOS services running.
5. `find_intent_transformer_plugins()` discovers the installed plugin under the
   expected name.

---

*Source code: [OpenVoiceOS/ovos-core](https://github.com/OpenVoiceOS/ovos-core).*
