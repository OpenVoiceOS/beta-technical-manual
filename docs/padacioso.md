# Padacioso

!!! abstract "In a nutshell"
    Padacioso is a simple tool that figures out what a user *meant*. It matches what they said against a list of example phrases you write by hand, like a phrasebook. Unlike its smarter sibling Padatious, it does no machine learning and needs no training. It checks the words literally, with some flexibility for optional words and fill-in-the-blank slots. It also pulls out useful pieces, called an "entity" (for example, the city name in "weather in Lisbon"). See the [Glossary](glossary.md) for terms like *intent* and *entity*.

Not in the default pipeline. Add its stage IDs to `intents.pipeline` explicitly to use it.

*A lightweight, dead-simple intent parser*

Built on top of [simplematch](https://github.com/tfeldmann/simplematch), inspired by [Padaos](https://github.com/MycroftAI/padaos).

Padacioso matches an utterance against example sentences using plain string templates. It needs no training and no model files. It is the pure-Python sibling of Padatious. Padatious learns from examples, but Padacioso matches them literally, with a few placeholder syntaxes. Each call to `calc_intent` returns the best match as `{"name", "entities", "conf"}`, or `name: None` when nothing matches.

## Example

```python
from padacioso import IntentContainer

container = IntentContainer()

# plain samples
container.add_intent('hello', ['hello', 'hi', 'how are you', "what's up"])

# "optionally" syntax — [word] is optional
container.add_intent('hello world', ["hello [world]"])

# "one_of" syntax — any of the alternatives
container.add_intent('greeting', ["(hi|hey|hello)"])

# entity extraction with {placeholders}
container.add_intent('search', [
    'search for {query} on {engine}', 'using {engine} (search|look) for {query}',
    'find {query} (with|using) {engine}'
])
container.add_entity('engine', ['abc', 'xyz'])
container.calc_intent('find cats using xyz')
# {'name': 'search', 'entities': {'query': 'cats', 'engine': 'xyz'}, 'conf': 0.96}
# wildcards — * matches anything; the name is the registered intent name
container.add_intent('say', ["say *"])
container.calc_intent('say something, whatever')
# {'name': 'say', 'entities': {}, 'conf': 0.85}
```

Both `padacioso.IntentContainer.add_intent()`, called directly as above, and the OVOS
pipeline's `.intent`-file path share the same `ovos-spec-tools` slot-name validator, which
enforces the OVOS grammar (`{lowercase_with_underscores}`) — `simplematch`'s colon-typed
slot syntax (`{number:int}`) is **not** supported by either path, and fails with
`MalformedTemplate`.

The two paths differ only in how they handle that failure. Calling `add_intent()` directly
propagates the exception — it crashes. The pipeline plugin catches it per sample instead:
the malformed line is skipped with a `LOG.warning`, and registration only fails outright if
every sample in the file was malformed.

A wildcard (`*`) carries a confidence penalty proportional to how much of the template it
covers: `0.05 + 0.20 × (wildcard tokens / total tokens)`, so any wildcard costs between
`0.05` and `0.25`. For example, `"say *"` is one wildcard out of two tokens, dropping the
score from `1.0` to `0.85`. Entity placeholders like `{number}` are not wildcards and carry
no wildcard penalty. An entity whose name was never registered with `add_entity` still
matches, at a small `0.04` penalty (e.g. `0.96`). A registered entity whose parsed value is
not among the registered samples is penalized `0.1`.

!!! warning "Bracket/alternation expansion is capped per intent: keep high-cardinality lines narrow"
    Each `add_intent()` call bracket-expands every line (`(a|b|c)` alternation, `[optional]`
    words). All of an intent's lines share one fixed sample budget: 2000 total. A single line
    with a large alternation product, for example
    `(what is|what's) the (low|lowest|...) temp (mon|tue|...|sun) (morning|afternoon|...|night)`,
    can run into the hundreds of combinations and consume most or all of that budget alone.

    When a line's own expansion exceeds its even share of the budget, padacioso logs a
    warning and keeps a deterministic, uniformly-sampled subset of that line's combinations.
    It does not just keep the first N. Even so, a subset is still a subset, so specific
    phrasings can come back unmatched. Split an overflowing line into several narrower lines
    instead of relying on the sampler to cover it.

## Context and keyword gating

Intents can be gated at runtime by session context or suppressed by keyword:

- `set_context(intent_name, context_name, context_val=None)` / `require_context(intent_name, context_name)`: only consider the intent when the given context is active. `unset_context` / `unrequire_context` reverse them.
- `exclude_context(intent_name, context_name)`: suppress the intent while a context is active (`unexclude_context` reverses it).
- `exclude_keywords(intent_name, samples)`: drop the intent from matching when the query contains any of the given keywords.

These let a container activate or hide intents based on conversational state without rebuilding it.

!!! tip "When to choose Padacioso"
    Use it when you want Padatious-style example-based matching with entity extraction, but
    without a training step or model files. It suits tests, tiny scripts, or resource-constrained
    devices. Padacioso also has an optional built-in fuzzy mode. `IntentContainer(fuzz=True)`
    enables rapidfuzz-based typo-tolerant matching against template variants, scored with a
    confidence penalty. For a dedicated fuzzy parser, use [Nebulento](nebulento.md). For keyword-only
    matching, use [Palavreado](palavreado.md). For the full neural version, use
    [Padatious](padatious-pipeline.md).

## Pipeline config

Beyond the standalone library, the same package ships an intent-pipeline plugin:

| Entry point (`opm.pipeline`) | Class |
|---|---|
| `ovos-padacioso-pipeline-plugin` | `padacioso.opm:PadaciosoPipeline` |

Configure it under `intents.ovos-padacioso-pipeline-plugin`:

```json
{"intents": {"ovos-padacioso-pipeline-plugin": {"conf_high": 0.95}}}
```

| Key | Default | Description |
|-----|---------|-------------|
| `conf_high` | `0.95` | Threshold for the high-confidence stage. |
| `conf_med` | `0.8` | Threshold for the medium-confidence stage. |
| `conf_low` | `0.5` | Threshold for the low-confidence stage. |
| `workers` | `4` | Worker processes for parallel intent matching. |
| `fuzz` | unset | Fuzzy-matching setting passed through to `IntentContainer`. |

---

*Source code: [OpenVoiceOS/padacioso](https://github.com/OpenVoiceOS/padacioso).*

---
**Read next:** [Nebulento](nebulento.md)
**Related:** [Adapt Pipeline](adapt-pipeline.md) · [Padatious Pipeline](padatious-pipeline.md) · [Palavreado](palavreado.md)
