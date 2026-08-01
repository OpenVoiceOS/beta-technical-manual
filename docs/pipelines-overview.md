# OVOS Intent Pipeline

!!! abstract "In a nutshell"
    When you speak to your assistant, something has to figure out *what you actually want* and act on it. The intent pipeline is the part that does that: it passes your words through a series of checkpoints, each trying to understand the request, from confident exact matches down to best-guess fallbacks. The first checkpoint that recognizes your request handles it, much like a help desk that sends your question to the right department. See the [Glossary](glossary.md) and the [Fallback Pipeline](fallback-pipeline.md) for related terms.

??? info "📐 Formal specification"
    The utterance lifecycle and the pipeline-plugin contract are specified by **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. The intents these plugins consume are specified by **[OVOS-INTENT-3 — Intent Definition](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)** (keyword and template intents) over the **[OVOS-INTENT-1 — Sentence Template Grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)**. See the [spec index](architecture-specs.md) for the full set.

The OpenVoiceOS (OVOS) Intent Pipeline is a modular, extensible system that interprets user utterances and maps them to actions or responses. It orchestrates pipeline plugins and fallback mechanisms to produce accurate, contextually relevant responses. This layered, rule-based approach tries plain keyword and template matchers before any statistical or LLM-backed stage. This is a deliberate design choice. See the [blog post](https://blog.openvoiceos.org/posts/2025-11-25-gofai) for why classic Adapt/Padatious matching still earns the first checkpoints.

When the entry utterance carries no authoritative language tag, the orchestrator resolves the language **once**, from session evidence. It passes that same resolved tag into every plugin's `match` call for the utterance. A plugin may refine it locally but must not silently re-derive its own answer. Otherwise different stages could match the same utterance in different languages depending on ordering.

!!! note "Spec vocabulary in one paragraph"
    In OVOS-PIPELINE-1 terms, every stage on this page is a **pipeline plugin** identified by an opaque `pipeline_id`. Each one exposes exactly one operation to the **orchestrator**: `match(utterances, lang, message) → Match | None` (the third argument is the utterance `Message`. A plugin that needs the session reads it from `message.context["session"]`). The orchestrator iterates the plugins in the order given by `session.pipeline` and stops at the **first** one that returns a `Match`. **First match wins.** There is *no* cross-plugin confidence comparison. The per-stage `conf_high/medium/low` thresholds below are each plugin's *own* internal accept/reject gate, not a score the orchestrator ranks between plugins. On a match the orchestrator dispatches the handler on the topic `<skill_id>:<intent_name>` (PIPELINE-1 §7) and emits the handler-lifecycle trio. If no plugin claims, it emits `ovos.intent.unmatched`. Several stages here (converse, stop, common-query, fallback) are pipeline plugins that claim via **reserved `intent_name` values** (`converse`, `response`, `stop`, `common_query`, `fallback`) leased in PIPELINE-1 §7.3. Skills may not register those names.

---

## What is an Intent Pipeline?

An intent pipeline in OVOS is a sequence of processing stages that analyze user input to determine the user's intent. Each stage uses a different strategy, ranging from high-confidence pipeline plugins to fallback mechanisms.

This layered approach lets OVOS handle a wide range of user queries at varying levels of specificity and complexity.

---

## Pipeline Structure

When an utterance arrives, OVOS walks the pipeline in order and hands the utterance to each stage until one claims it. Stages are tried from most to least confident:

*   **High Confidence**: Primary pipeline plugins that provide precise matches.


*   **Medium Confidence**: Secondary parsers that handle less specific queries.


*   **Low Confidence**: [Fallback](fallback-pipeline.md) mechanisms for ambiguous or unrecognized inputs.

The first stage that matches wins, so order matters. A high-confidence Padatious match is tried before any medium-confidence stage. A medium-confidence stage is tried before any low-confidence stage. Each component is a plugin. You can enable, disable, or reorder it in your config.

!!! note "`intents.pipeline` orders matchers: it does not gate loading"
    The config list controls which loaded matchers are *tried* and in what order. Every
    installed pipeline plugin is still discovered and initialized at startup (some load
    models when they do); to keep a plugin from initializing at all, uninstall its package.

Ordering is **the arbitration model, not a missing feature** (PIPELINE-1 §6.2). An earlier plugin gets to answer before any later plugin is asked. This lets a stateful interceptor that depends on session state claim "yes" / "next" / "resume" / "stop" *before* a general pipeline plugin would match the bare words. Examples include converse with an open response window, an active persona, OCP holding paused media to *resume*, and stop. Such selective plugins are deliberately conservative. They claim only when both the utterance and the session warrant it, and return `None` otherwise, trusting their position rather than competing on a score. Heterogeneous engines share no common score space to rank across anyway.

**Pipeline IDs vs. plugins.** The IDs you list in your `pipeline` config (like `ovos-adapt-pipeline-plugin-high`) are not separate plugins. A confidence-aware plugin registers a single OPM entry point (e.g. `ovos-adapt-pipeline-plugin`), and OVOS derives the `-high`/`-medium`/`-low` matcher stages from it at runtime. Plugins that match at only one confidence level (such as `ovos-converse-pipeline-plugin` or `ovos-common-query-pipeline-plugin`) expose a single bare ID. The older short names (`adapt_high`, `common_qa`, …) are **deprecated aliases**. ovos-core still accepts them and rewrites them to the canonical plugin IDs via the `_PIPELINE_MIGRATION_MAP`. Existing configs keep working this way. The bundled default configuration and new configs alike should use the canonical names shown below.

---

## Available Pipeline Components

Below is a list of available pipeline components, grouped by confidence level. The **Pipeline ID** column shows the canonical name to put in your `pipeline` config. The **Legacy alias** column shows the older short name that some existing configs may still use. ovos-core rewrites it to the canonical ID at load time. New configs should use the canonical names.

!!! note "The bundled default pipeline"
    The default `pipeline` list shipped in `mycroft.conf` uses the canonical plugin IDs, in
    this order:

    --8<-- "snippets/default-pipeline.md"

    Note that Padatious/Adapt's low tier, Model2Vec's medium/low tiers, OCP's low tier,
    Common Query, Persona, and the `-low` tiers of stop/padatious are **not** in the default
    list; you add them yourself if you want them.

### High Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-high` | `stop_high` | Exact match for stop commands (replaces [skill-ovos-stop](https://github.com/OpenVoiceOS/skill-ovos-stop)) |
| `ovos-converse-pipeline-plugin` | `converse` | Continuous conversation interception for skills |
| `ovos-padatious-pipeline-plugin-high` | `padatious_high` | High-confidence matches using [Padatious](padatious-pipeline.md) |
| `ovos-adapt-pipeline-plugin-high` | `adapt_high` | High-confidence matches using [Adapt](adapt-pipeline.md) |
| `ovos-fallback-pipeline-plugin-high` | `fallback_high` | High-priority fallback skill matches |
| `ovos-ocp-pipeline-plugin-high` | `ocp_high` | High-confidence media-related queries |
| `ovos-persona-pipeline-plugin-high` | — | Active persona conversation (e.g., LLM integration) |
| `ovos-m2v-pipeline-high` | — | Multilingual intent classifier (only supports default skills) |

> **OCP vs. Common Query:** these are two unrelated pipeline plugins that both start with "Common."
> **OCP** (Common Play, the `ocp_*` stages above) matches media-*playback* requests like "play X."
> **Common Query** (the `common_qa` stage further below) sends a question to every skill that can
> answer it and picks the best response. Neither one calls into the other.

### Medium Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-medium` | `stop_medium` | Medium-confidence stop command matches |
| `ovos-padatious-pipeline-plugin-medium` | `padatious_medium` | Medium-confidence matches using Padatious |
| `ovos-adapt-pipeline-plugin-medium` | `adapt_medium` | Medium-confidence matches using Adapt |
| `ovos-ocp-pipeline-plugin-medium` | `ocp_medium` | Medium-confidence media-related queries |
| `ovos-fallback-pipeline-plugin-medium` | `fallback_medium` | Medium-priority fallback skill matches |
| `ovos-m2v-pipeline-medium` | — | Multilingual intent classifier (only supports default skills) |

### Low Confidence Components

| Pipeline ID | Legacy alias | Description |
|---|---|---|
| `ovos-stop-pipeline-plugin-low` | `stop_low` | Low-confidence stop command matches (disabled by default) |
| `ovos-padatious-pipeline-plugin-low` | `padatious_low` | Low-confidence matches using Padatious (disabled by default) |
| `ovos-adapt-pipeline-plugin-low` | `adapt_low` | Low-confidence matches using Adapt |
| `ovos-ocp-pipeline-plugin-low` | `ocp_low` | Low-confidence media-related queries |
| `ovos-fallback-pipeline-plugin-low` | `fallback_low` | Low-priority fallback skill matches |
| `ovos-common-query-pipeline-plugin` | `common_qa` | Sends utterance to common-query skills (best match among skills) |
| `ovos-persona-pipeline-plugin-low` | — | Persona catch-all fallback |
| `ovos-m2v-pipeline-low` | — | Multilingual intent classifier (only supports default skills) |

---

### Other available matchers (not enabled by default)

These are additional OVOS-org intent-matcher pipeline plugins you can install and add to the
pipeline. They expose the same high/medium/low confidence tiers as Adapt/Padatious:

| Plugin | Description |
|---|---|
| [Padacioso](padacioso.md) | Literal template matcher (simplematch), no training. A pure-Python sibling of [Padatious](padatious-pipeline.md). |
| [Nebulento](nebulento.md) | Fuzzy / typo-tolerant template matcher (rapidfuzz), no training step. Listens on the same `padatious:register_intent` bus events, plus a hierarchical variant. |
| [Palavreado](palavreado.md) | Dead-simple keyword matcher, an [Adapt](adapt-pipeline.md) drop-in that responds to the same `register_vocab`/`register_intent` events (zero-change skill swap). |
| [Hierarchical KNN](knn-pipeline.md) | Embedding-based two-stage k-NN matcher (Granite embeddings + FAISS), a heavier semantic alternative to [Model2Vec](m2v-pipeline.md) (~560 MB footprint, AVX2, 11 languages). |
| [`ovos-markov-pipeline-plugin`](https://github.com/OpenVoiceOS/ovos-markov-pipeline-plugin) | Markov-chain perplexity ensemble. Trains one word-level Markov chain per intent from example utterances and picks the intent whose model has the lowest perplexity for the utterance. Lightweight, GPU-free, and trains in milliseconds. A practical baseline for small skill sets. |
| [`ovos-hivemind-pipeline-plugin`](hivemind-agents.md#as-an-intent-pipeline-stage) | Delegates the utterance to a remote [HiveMind](hivemind-agents.md) agent, a catch-all "ask a smarter OVOS" stage. |

---

## Customizing the Pipeline

You can customize the intent pipeline through configuration files. You can enable or disable specific components, change their order, and set confidence thresholds.

```json
{
  "intents": {
    "ovos-adapt-pipeline-plugin": {
      "conf_high": 0.5,
      "conf_med": 0.3,
      "conf_low": 0.2
    },
    "persona": {
      "handle_fallback": true,
      "default_persona": "Remote Llama"
    },
    "pipeline": [
      "ovos-stop-pipeline-plugin-high",
      "ovos-converse-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-high",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-m2v-pipeline-high",
      "ovos-ocp-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-high",
      "ovos-stop-pipeline-plugin-medium",
      "ovos-adapt-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}
```

---

## Writing a Pipeline Plugin

A pipeline plugin implements one `match(utterances, lang, message)` call. Pick your base class by shape:

*   **`PipelinePlugin`** — a single-tier plugin. It exposes one bare pipeline ID and implements `match()` directly. Use this for stages like converse or stop-exact.
*   **`ConfidenceMatcherPipeline`** — a `PipelinePlugin` subclass for plugins with high/medium/low tiers, like Adapt and Padatious. OVOS derives the `-high`/`-medium`/`-low` pipeline IDs from your single registered plugin at runtime (see [Pipeline IDs vs. plugins](#pipeline-ids-vs-plugins) above).

Both classes come from `ovos_plugin_manager.templates.pipeline`. Register your plugin under the `opm.pipeline` entry-point group, with an optional matching `opm.pipeline.config` group for config metadata, the same pattern used by [transformer and agent plugins](building-agent-plugins.md).

### The `ConfidenceMatcherPipeline` contract

Don't override `match()` on `ConfidenceMatcherPipeline`. The base class already implements it: it tries `match_high`, then `match_medium`, then `match_low`, and returns the first non-`None` result. You implement the three tier methods instead. All three, and `match()` on a plain `PipelinePlugin`, share one signature:

```python
def match_high(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
    ...
```

Return `None` when your plugin does not want to claim the utterance. Return an `IntentHandlerMatch` when it does.

`IntentHandlerMatch` fields:

*   `match_type` — name of the matching service.
*   `match_data` — extra data for the intent handler.
*   `skill_id` and `utterance` — route the dispatch to the right skill.
*   `updated_session` — lets a plugin mutate session state as part of matching.
*   `suppress_activation` — set this for a termination or continuation of an already-active skill, such as stop. It tells the orchestrator to dispatch without sending a fresh `{skill_id}.activate`.

The constructor is `__init__(self, bus=None, config=None)`. This differs from the transformer templates: there is no `name` or `priority` argument. `self.bus` defaults to a `FakeBus()` when you pass none. A `FakeBus` needs no running message bus, so you can unit test a plugin standalone.

Pipeline plugins have no numeric priority field. Their order comes entirely from the deployer's `intents.pipeline` config list (see [Pipeline Structure](#pipeline-structure) above); first match wins.

### Minimal example

```python
from typing import List, Optional

from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.pipeline import ConfidenceMatcherPipeline, IntentHandlerMatch

# toy heuristic: exact phrase at high confidence, substring at medium, never at low
PHRASES = {"turn off the lights": "lights.skill"}
KEYWORDS = {"lights": "lights.skill"}


class DemoPipeline(ConfidenceMatcherPipeline):
    def match_high(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
        for utt in utterances:
            skill_id = PHRASES.get(utt.strip().lower())
            if skill_id:
                return IntentHandlerMatch(match_type="demo:exact", skill_id=skill_id, utterance=utt)
        return None

    def match_medium(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
        for utt in utterances:
            for keyword, skill_id in KEYWORDS.items():
                if keyword in utt.lower():
                    return IntentHandlerMatch(match_type="demo:keyword", skill_id=skill_id, utterance=utt)
        return None

    def match_low(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
        return None
```

A single-tier `PipelinePlugin` looks the same, minus the three tiers: you implement `match()` directly instead of `match_high`/`match_medium`/`match_low`.

### Packaging

```toml
[project]
name = "ovos-demo-pipeline-plugin"
version = "0.0.1"
dependencies = ["ovos-plugin-manager"]  # match your installed ovos-plugin-manager version

[project.entry-points."opm.pipeline"]
ovos-demo-pipeline-plugin = "ovos_demo_pipeline_plugin:DemoPipeline"
```

### Test it without OVOS

```python
from ovos_bus_client.message import Message

def test_demo_pipeline_matches_exact_phrase():
    plugin = DemoPipeline()  # no bus argument -> uses a default FakeBus()
    result = plugin.match_high(["turn off the lights"], "en-us", Message("recognizer_loop:utterance"))
    assert result is not None
    assert result.skill_id == "lights.skill"

def test_demo_pipeline_falls_through_to_medium():
    plugin = DemoPipeline()
    msg = Message("recognizer_loop:utterance")
    assert plugin.match_high(["check the lights"], "en-us", msg) is None
    result = plugin.match(["check the lights"], "en-us", msg)
    assert result is not None
    assert result.match_type == "demo:keyword"
```

No running OVOS instance, bus, or skill is needed for either test.

### Verify discovery

`ovos_plugin_manager.pipeline.find_pipeline_plugins()` wraps the general `find_plugins(PluginTypes.PIPELINE)` helper. Confirm your entry point resolves after installing your package:

```python
from ovos_plugin_manager.pipeline import find_pipeline_plugins

assert "ovos-demo-pipeline-plugin" in find_pipeline_plugins()
```

### Related pages

Worked examples already in this manual:

*   Tiered `ConfidenceMatcherPipeline` plugins: [Adapt Pipeline](adapt-pipeline.md), [Padatious Pipeline](padatious-pipeline.md)
*   Single-tier `PipelinePlugin` plugins: [Converse Pipeline](converse-pipeline.md), [Stop Pipeline](stop-pipeline.md)

---

## Pipeline Plugins Reference

Each pipeline plugin has its own manual page with full configuration details:

| Plugin | Description | Manual page |
|--------|-------------|-------------|
| `ovos-common-query-pipeline-plugin` | Answer questions by gathering answers from several skills | [Common Query](common-query.md) |
| `ovos-m2v-pipeline` | Intent matching powered by the Model2Vec model | [M2V Pipeline](m2v-pipeline.md) |
| `ovos-padatious-pipeline-plugin` | Neural network intent-matching pipeline plugin | [Padatious Pipeline](padatious-pipeline.md) |
| `ovos-adapt-pipeline-plugin` | Adapt Intent Parser | [Adapt Pipeline](adapt-pipeline.md) |
| `ovos-ocp-pipeline-plugin` | Specialized media handling | [OCP Pipeline](ocp-pipeline.md) |
