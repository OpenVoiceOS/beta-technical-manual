# Building Your Pipeline

!!! abstract "In a nutshell"
    The `intents.pipeline` list in `mycroft.conf` is the whole arbitration model for intent
    matching. OVOS tries each stage in the order you list, and the first one that claims the
    utterance wins. This page shows three fully worked pipeline configs, built only from stages
    documented elsewhere in this manual, so you can see how the ordering rules play out in
    practice. See the [Intent Pipeline Overview](pipelines-overview.md) for the full stage
    reference.

---

## How the pipeline list works

Every entry in `intents.pipeline` is a **pipeline ID** for a plugin already installed and
initialized. OVOS walks the list in order and hands the utterance to each stage until one
returns a match. There is no cross-plugin score comparison. Each plugin's own `conf_high` /
`conf_med` / `conf_low` thresholds are its private accept gate, not a rank the orchestrator
compares between plugins.

Reordering the list changes which stage gets first refusal on an utterance. Removing an ID
from the list stops that stage from being *tried*, but the plugin is still loaded at startup
unless you uninstall its package. See [Pipelines Overview](pipelines-overview.md) for the full
list of available stage IDs and their confidence tiers.

The three configs below are complete and directly runnable. Nothing is left as "add remaining
stages as needed."

---

## Example A: the stock voice-assistant default

This is the bundled default pipeline shipped in `mycroft.conf`, reproduced exactly as listed in
the [Pipelines Overview](pipelines-overview.md#available-pipeline-components):

```json
{
  "intents": {
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

Why each stage sits where it does:

- **`ovos-stop-pipeline-plugin-high`**: stop is a dedicated, always-on pipeline plugin, not a
  skill. It must sit first so an exact "stop" or "cancel" is intercepted before any other stage
  sees the bare word. See [Stop Pipeline](stop-pipeline.md).
- **`ovos-converse-pipeline-plugin`**: converse depends on session state (which skills are
  active, who is awaiting a reply), so it must run before the general matchers so a skill mid
  conversation can claim "yes", "the kitchen", or "stop" before a generic parser would. See
  [Converse Pipeline](converse-pipeline.md).
- **`ovos-ocp-pipeline-plugin-high`**: OCP's high tier claims explicit media intents and, while
  it holds paused media for the session, bare control words like "resume" or "next". It needs
  to run early for the same session-aware reason as converse. See [OCP Pipeline](ocp-pipeline.md).
- **`ovos-padatious-pipeline-plugin-high`**: Padatious's high tier runs before Adapt's, so a
  strong example-sentence match wins over a keyword rule. See
  [Padatious Pipeline](padatious-pipeline.md).
- **`ovos-adapt-pipeline-plugin-high`**: Adapt's high tier runs right after Padatious's, so a
  strong keyword match still beats most fallbacks even when no example sentence matched. See
  [Adapt Pipeline](adapt-pipeline.md).
- **`ovos-m2v-pipeline-high`**: placed after the high tiers of Padatious and Adapt, so exact and
  keyword matches win first and Model2Vec only catches the paraphrases the deterministic engines
  miss. See [Model2Vec Pipeline](m2v-pipeline.md).
- **`ovos-ocp-pipeline-plugin-medium`**: catches utterances classified as media queries by
  keyword rather than an explicit intent, once the higher-confidence stages have passed. See
  [OCP Pipeline](ocp-pipeline.md).
- **`ovos-fallback-pipeline-plugin-high`**: the fallback plugin's high-priority range
  (`0 < p ≤ 5`) is reserved for critical fallback handlers, tried before medium-confidence
  matchers get another pass. See [Fallback Pipeline](fallback-pipeline.md).
- **`ovos-stop-pipeline-plugin-medium`**: a fuzzy (non-exact) stop match, for stop phrases that
  are not a literal "stop" or "cancel". See [Stop Pipeline](stop-pipeline.md).
- **`ovos-adapt-pipeline-plugin-medium`**: Adapt's medium tier, a second, looser pass over
  keyword rules.
- **`ovos-fallback-pipeline-plugin-medium`** and **`ovos-fallback-pipeline-plugin-low`**: general
  and catch-all fallback skills, tried last, in ascending priority order, only once every regular
  matcher has passed.

Note what is deliberately absent: Padatious/Adapt's low tier, Model2Vec's medium/low tiers,
OCP's low tier, Common Query, Persona, and stop/padatious's low tiers are not in the default
list. You add them yourself if you want them.

---

## Example B: a media-focused device

A device used mainly for music or podcasts can afford to promote OCP further and add its low
tier, which the [OCP Pipeline](ocp-pipeline.md) page warns should only run "on devices used
mainly for media playback" because it can fire on any phrase containing a known artist or show
name.

```json
{
  "intents": {
    "ovos-ocp-pipeline-plugin": {
      "min_score": 50
    },
    "pipeline": [
      "ovos-stop-pipeline-plugin-high",
      "ovos-converse-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-high",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-ocp-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-medium",
      "ovos-ocp-pipeline-plugin-low"
    ]
  }
}
```

Why each stage sits where it does:

- **`ovos-stop-pipeline-plugin-high`** and **`ovos-converse-pipeline-plugin`**: stop and
  converse stay first for the same session-state reasons as Example A. A media device still
  needs "stop" and an in-progress conversation to win before playback control does.
- **`ovos-ocp-pipeline-plugin-high`**: promoted right after converse, ahead of Padatious/Adapt,
  because on this device explicit playback commands and stateful "resume"/"next" control words
  are the primary use case.
- **`ovos-padatious-pipeline-plugin-high`** and **`ovos-adapt-pipeline-plugin-high`**: regular
  skill intents (setting timers, asking the weather, and so on) still get their normal
  high-confidence pass.
- **`ovos-ocp-pipeline-plugin-medium`**: catches keyword-classified media queries that the
  explicit-intent high tier missed, per the [OCP Pipeline](ocp-pipeline.md) quick-start example.
- **`ovos-fallback-pipeline-plugin-medium`**: a general fallback pass before the most permissive
  OCP tier gets a turn, so a misheard non-media utterance is not swallowed by a loose media
  keyword hit.
- **`ovos-ocp-pipeline-plugin-low`**: last, and only justified on a media-focused device, exactly
  as the OCP page recommends. It keys off any skill-registered media keyword, so placing it last
  limits the damage from a false positive.

---

## Example C: a persona/chatbot-first assistant

This reproduces the **Hybrid Mode** configuration from the
[Persona Pipeline](persona-pipeline.md#2-hybrid-mode-skills-first) page: skills get first refusal,
and the persona (an LLM-backed conversational agent) fills in wherever they fall short, before
the catch-all fallback skills get a turn.

```json
{
  "intents": {
    "persona": {
      "handle_fallback": true,
      "default_persona": "Remote Llama"
    },
    "pipeline": [
      "ovos-stop-pipeline-plugin-high",
      "ovos-converse-pipeline-plugin",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-persona-pipeline-plugin-high",
      "ovos-padatious-pipeline-plugin-medium",
      "ovos-adapt-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-high",
      "ovos-fallback-pipeline-plugin-medium",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}
```

Why each stage sits where it does:

- **`ovos-stop-pipeline-plugin-high`** and **`ovos-converse-pipeline-plugin`**: unchanged from
  Examples A and B. Stop must always win over a chatty persona, and an in-progress skill
  conversation still gets priority.
- **`ovos-padatious-pipeline-plugin-high`** and **`ovos-adapt-pipeline-plugin-high`**: regular
  skills get first refusal, which is the point of Hybrid Mode: "preserves traditional voice
  assistant behavior" while the persona "fills in where skills fall short."
  See [Persona Pipeline](persona-pipeline.md).
- **`ovos-persona-pipeline-plugin-high`**: placed after the deterministic high tiers but before
  their medium tiers. An active or default persona (`handle_fallback: true`, `default_persona`)
  catches open-ended chat and unmatched questions before the pipeline relaxes to a looser
  keyword pass.
- **`ovos-padatious-pipeline-plugin-medium`** and **`ovos-adapt-pipeline-plugin-medium`**: a
  second, looser skill-matching pass in case the persona missed something a skill could still
  answer.
- **`ovos-fallback-pipeline-plugin-high`**, **`-medium`**, **`-low`**: the standard fallback
  ladder closes out the pipeline, in ascending priority order, in case neither skills nor the
  persona claimed the utterance.

For a persona-first deployment where the chatbot should override skills entirely, see
[Persona Pipeline: Full Control mode](persona-pipeline.md#1-full-control-persona-first) instead.

---

## Ordering rules of thumb

- **Stop goes first.** STOP-1 only works because a high-confidence stop stage placed first in
  the pipeline can intercept the bare word "stop" before any other plugin claims it. See
  [Stop Pipeline](stop-pipeline.md).
- **Converse goes early, before the general matchers.** It depends on session state (is a skill
  still active, is someone awaiting a reply), so it needs first refusal on utterances that
  continue an existing exchange. See [Converse Pipeline](converse-pipeline.md).
- **High tiers before medium tiers before low tiers.** A high-confidence match is tried before
  any medium-confidence stage, and a medium-confidence stage before any low-confidence one. This
  is the arbitration model itself, not an optional convention. See
  [Pipelines Overview](pipelines-overview.md).
- **Statistical/semantic stages (Model2Vec, Hierarchical KNN) go after the deterministic
  engines' high tiers.** They generalize well, which also means they can claim an utterance a
  more precise parser would have nailed if placed too early. See
  [Model2Vec Pipeline](m2v-pipeline.md) and [Hierarchical KNN Pipeline](knn-pipeline.md).
- **Fallback goes last.** By design it only runs "after all other matchers fail," and its own
  high/medium/low tiers further order fallback skills by priority range. See
  [Fallback Pipeline](fallback-pipeline.md).
- **A persona's placement encodes its strategy.** First and ahead of skills for a full-control
  chatbot, after the skills' high tiers for a hybrid assistant, or last (a `-low` stage) for a
  pure "default persona when nothing else matched" setup. See
  [Persona Pipeline](persona-pipeline.md).

---

## Related Pages

- [Intent Pipeline Overview](pipelines-overview.md): the full stage reference and the bundled
  default pipeline
- [Adapt Pipeline](adapt-pipeline.md), [Padatious Pipeline](padatious-pipeline.md),
  [Model2Vec Pipeline](m2v-pipeline.md), [Hierarchical KNN Pipeline](knn-pipeline.md): the
  deterministic and semantic matchers
- [Converse Pipeline](converse-pipeline.md), [Stop Pipeline](stop-pipeline.md): the
  session-aware interceptors
- [OCP Pipeline](ocp-pipeline.md), [Common Query Pipeline](cq-pipeline.md),
  [Persona Pipeline](persona-pipeline.md): the specialized matchers
- [Fallback Pipeline](fallback-pipeline.md): the catch-all stages tried last
- [Debugging Intent Matching](debugging-intent-matching.md): what to check when a pipeline you
  built does not behave as expected
