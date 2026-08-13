# Writing a Pipeline Plugin

!!! abstract "In a nutshell"
    A pipeline plugin is a checkpoint you write yourself: a small class with one job, deciding whether it understands an utterance and, if so, handing back a match. This page walks through building one, from the base classes to packaging and testing it without a running OVOS instance. For the built-in stages and how to order them, see [Pipelines Overview](pipelines-overview.md).

A pipeline plugin implements one `match(utterances, lang, message)` call. (The shipped base classes pass the full utterance `Message` as the third argument; the [PIPELINE-1 spec](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md) prescribes the extracted `session` carrier there instead — a known divergence, so read the session from `message.context["session"]` for now.) Pick your base class by shape:

*   **`PipelinePlugin`**: a single-tier plugin. It exposes one bare pipeline ID and implements `match()` directly. Use this for stages like converse or stop-exact.
*   **`ConfidenceMatcherPipeline`**: a `PipelinePlugin` subclass for plugins with high/medium/low tiers, like Adapt and Padatious. OVOS derives the `-high`/`-medium`/`-low` pipeline IDs from your single registered plugin at runtime. See [Pipeline IDs vs. plugins](pipelines-overview.md#pipeline-ids-vs-plugins) on the overview page.

Both classes come from `ovos_plugin_manager.templates.pipeline`. Register your plugin under the `opm.pipeline` entry-point group. Add an optional matching `opm.pipeline.config` group for config metadata. This is the same pattern used by [transformer and agent plugins](building-agent-plugins.md).

---

## The `ConfidenceMatcherPipeline` contract

Don't override `match()` on `ConfidenceMatcherPipeline`. The base class already implements it: it tries `match_high`, then `match_medium`, then `match_low`, and returns the first non-`None` result. You implement the three tier methods instead. All three, and `match()` on a plain `PipelinePlugin`, share one signature:

```python
def match_high(self, utterances: List[str], lang: str, message: Message) -> Optional[IntentHandlerMatch]:
    ...
```

Return `None` when your plugin does not want to claim the utterance. Return an `IntentHandlerMatch` when it does.

`IntentHandlerMatch` fields:

*   `match_type`: name of the matching service.
*   `match_data`: extra data for the intent handler.
*   `skill_id` and `utterance`: route the dispatch to the right skill.
*   `updated_session`: lets a plugin mutate session state as part of matching.
*   `suppress_activation`: set this for a termination or continuation of an already-active skill, such as stop. It tells the orchestrator to dispatch without sending a fresh `{skill_id}.activate`.

The constructor is `__init__(self, bus=None, config=None)`. This differs from the transformer templates: there is no `name` or `priority` argument. `self.bus` defaults to a `FakeBus()` when you pass none. A `FakeBus` needs no running message bus, so you can unit test a plugin standalone.

Pipeline plugins have no numeric priority field. Their order comes entirely from the deployer's `intents.pipeline` config list. See [Pipeline Structure](pipelines-overview.md#pipeline-structure) on the overview page. First match wins.

---

## Minimal example

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

---

## Packaging

```toml
[project]
name = "ovos-demo-pipeline-plugin"
version = "0.0.1"
dependencies = ["ovos-plugin-manager"]  # match your installed ovos-plugin-manager version

[project.entry-points."opm.pipeline"]
ovos-demo-pipeline-plugin = "ovos_demo_pipeline_plugin:DemoPipeline"
```

---

## Test it without OVOS

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

---

## Verify discovery

`ovos_plugin_manager.pipeline.find_pipeline_plugins()` wraps the general `find_plugins(PluginTypes.PIPELINE)` helper. Confirm your entry point resolves after installing your package:

```python
from ovos_plugin_manager.pipeline import find_pipeline_plugins

assert "ovos-demo-pipeline-plugin" in find_pipeline_plugins()
```

---

## Related pages

Worked examples already in this manual:

*   Tiered `ConfidenceMatcherPipeline` plugins: [Adapt Pipeline](adapt-pipeline.md), [Padatious Pipeline](padatious-pipeline.md)
*   Single-tier `PipelinePlugin` plugins: [Converse Pipeline](converse-pipeline.md), [Stop Pipeline](stop-pipeline.md)

---
**Read next:** [Building Your Pipeline](building-your-pipeline.md)
**Related:** [Pipelines Overview](pipelines-overview.md) · [Adapt Pipeline](adapt-pipeline.md) · [Padatious Pipeline](padatious-pipeline.md) · [Building Agent Plugins](building-agent-plugins.md)
