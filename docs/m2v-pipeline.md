# Model2Vec Intent Pipeline

!!! note "Maturity — Beta ⬤⬤⬤◯◯"
    In real use but still settling — watch releases for the occasional breaking change. Rated by [repository health](maturity.md), not version.

!!! abstract "In a nutshell"
    This is another tool that figures out which skill should handle what you said. Instead of matching exact keywords or memorized examples, it compares the *meaning* of your words to the commands it knows. This means it can still understand you when you phrase things differently than expected. Think of it as recognizing that "turn the music down" and "lower the volume" are asking for the same thing. It is meant to work alongside the keyword-based [Adapt](adapt-pipeline.md) and example-based [Padatious](padatious-pipeline.md) tools, not replace them. See the [Glossary](glossary.md) for unfamiliar terms.

Shipped in the default pipeline.

The rest of this page is for people deploying or customizing OVOS. If you only wanted to know what this stage does, you are done.

??? info "📐 Formal specification"
    Model2Vec is a **pipeline plugin** under **[OVOS-PIPELINE-1 — Utterance Lifecycle & Pipeline](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)**. It serves the same **template-intent** role as Padatious in **[OVOS-INTENT-3 — Intent Definition §5](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-3.md)**: a classifier paired with a slot extractor (INTENT-3 §6.2). Only the matching strategy (static embeddings) differs, and INTENT-3 §8 leaves that strategy unconstrained. Skill resources are written in the **[OVOS-INTENT-1 grammar](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md)**. See the [spec index](architecture-specs.md).

The **Model2Vec Intent Pipeline** matches utterances to skill intents using
[Model2Vec](https://github.com/MinishLab/model2vec) static embeddings instead of
deterministic parsers. Where Adapt looks for keywords and Padatious learns from
example sentences, this pipeline embeds the utterance as a vector and picks the
closest known intent. That makes it more forgiving of paraphrases and word order,
and it works across languages when a multilingual model is used.

It is meant to **augment** Adapt and Padatious, not replace them. Put a Model2Vec
matcher in your pipeline alongside the others and let confidence ordering decide.

---

## Quick start

Install the plugin:

```bash
pip install ovos-m2v-pipeline
```

Add a matcher to your pipeline in `mycroft.conf`:

```json
{
  "intents": {
    "ovos-m2v-pipeline": {
      "model": "OpenVoiceOS/ovos-m2v-intents-multilingual"
    },
    "pipeline": [
      "ovos-converse-pipeline-plugin",
      "ovos-padatious-pipeline-plugin-high",
      "ovos-adapt-pipeline-plugin-high",
      "ovos-m2v-pipeline-high",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}
```

That is enough to get going. The model is downloaded from Hugging Face on first
run. The sections below cover how matching works and how to tune it.

---

## How it works

The plugin (`Model2VecIntentPipeline`) is a `ConfidenceMatcherPipeline`, so it
exposes three confidence tiers, `match_high`, `match_medium`, and `match_low`, that
become the pipeline matcher IDs `ovos-m2v-pipeline-high` / `-medium` / `-low`.

For an utterance it:

1. Embeds the text with the configured Model2Vec model.
2. Scores every label the model knows about.
3. Keeps only labels that belong to **currently registered** Adapt/Padatious
   intents (the pipeline tracks them over the bus via
   `intent.service.adapt.manifest` / `intent.service.padatious.manifest` and the
   `register_intent` / `padatious:register_intent` / `detach_intent` /
   `detach_skill` events). Three special labels, `ocp:play`,
   `common_query:common_query`, and `stop:stop`, are also allowed, but only when the
   corresponding downstream pipeline (`ovos-ocp-pipeline-plugin`,
   `ovos-common-query-pipeline-plugin`, `ovos-stop-pipeline-plugin`) is present in
   the session's pipeline list.
4. Returns the highest-scoring label as an `IntentHandlerMatch` if its score
   clears the tier threshold (`conf_high` / `conf_medium` / `conf_low`).

Because matching is restricted to intents that are actually loaded, the model can
ship knowledge of many skills without firing for skills you do not have installed.

A label registered with `requires_context` or `excludes_context` is gated the same way
whether it came from a padatious registration or an INTENT-4 template: the pipeline checks
the declared context before accepting the label as a match, not just the confidence score.

!!! note "Model2Vec classifies; it does not extract `{slot}` values from the utterance"
    A `.intent` sample can declare `{slot}` placeholders, but Model2Vec never parses them out
    of the spoken utterance the way Padatious and Padacioso do. It only fills a label's
    declared `{slot}` placeholders from `session.intent_context` (OVOS-CONTEXT-1 §7). A skill
    whose `.intent` files rely on `{slot}` extraction from the utterance itself still needs
    Padatious or Padacioso in the pipeline ahead of Model2Vec to populate those values.
    Model2Vec alone matches the intent but leaves any unfilled placeholder as a literal
    `{slot}` string.

```mermaid
flowchart TD
    U[Utterance] --> E[Embed with Model2Vec model]
    R[Registered Adapt/Padatious\nintent labels] --> F
    E --> SC[Score every known label]
    SC --> F{Filter to\nregistered labels}
    F --> B[Keep best-scoring label]
    B --> C{Score clears\nstage threshold?}
    C -->|yes| I[Intent + confidence]
    C -->|no| N[No match, try next stage]
```

*Diagram: the utterance is embedded, scored against every label the model knows, filtered down to labels that are actually registered by loaded skills, and the best surviving label is accepted only if it clears the current stage's threshold.*

---

## Two operating modes

The pipeline has a `mode` config key:

* **`classifier`** (default): loads a `StaticModelPipeline` (embedding model plus
  a trained linear classifier head). Scores are softmax probabilities. This is the
  mode used by the published `OpenVoiceOS/ovos-m2v-intents-*` models.
* **`prototype`**: loads a bare `StaticModel` (embeddings only, no trained head)
  and builds a prototype store from the example utterances skills provide when
  they register Padatious intents. Scores are cosine similarities. Adapt intents
  (which have no example sentences) are tracked by name but not matched in this
  mode. An unchanged registration is loaded from an on-disk cache instead of
  re-encoded on every boot; the cache clears itself when a skill or intent
  detaches (see `prototype_cache` below).

In classifier mode, the `-low` stage (`ovos-m2v-pipeline-low`) does not use the
trained head by default. It matches against the skills' own example utterances in
prototype mode, with the same model (`low_tier: "prototype"`). Set
`low_tier: "classifier"` to score the `-low` stage with the trained head at
`conf_low` instead.

A second entry point, `ovos-m2v-prototype-pipeline`
(`Model2VecPrototypePipeline`), is the prototype mode exposed as a standalone
plugin so it can run alongside the classifier one. It reads its config from
`intents.ovos-m2v-prototype-pipeline`.

---

## Configuration

```json
{
  "intents": {
    "ovos-m2v-pipeline": {
      "model": "OpenVoiceOS/ovos-m2v-intents-multilingual",
      "mode": "classifier",
      "conf_high": 0.7,
      "conf_medium": 0.5,
      "conf_low": 0.15,
      "ignore_intents": []
    }
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `model` | `OpenVoiceOS/ovos-m2v-intents-multilingual` (`DEFAULT_MULTILINGUAL`, used when no `models` entry matches the language) | Local path or Hugging Face repo of the Model2Vec model; an explicit value always wins over any per-language default. See `models` below for a per-language override map. |
| `models` | *(unset)* | `{locale_or_lang: repo_id}` map, matched first against the full locale (`"pt-BR"`), then against the primary subtag (`"pt"`); case-insensitive. Falls back to a built-in per-language default table, then to `model`/`DEFAULT_MULTILINGUAL` if no entry matches. |
| `mode` | `classifier` | `classifier` (trained head, softmax) or `prototype` (runtime prototypes, cosine). |
| `subfolder` | `int8` for the two `OpenVoiceOS/ovos-m2v-intents-*` repos when no `revision` is set | Folder of the model repo to load, such as `int8`, `fp16` or a per-language folder. `""` loads the repo root. |
| `revision` | *(unset)* | Git revision of the model repo to pin. |
| `conf_high` | `0.7` classifier, `0.85` prototype | Threshold for `match_high`. |
| `conf_medium` | `0.5` classifier, `0.7` prototype | Threshold for `match_medium`. |
| `conf_low` | `0.15` classifier, `0.65` prototype | Threshold for `match_low`. |
| `ignore_intents` | `[]` | Intent labels to never match. |
| `renormalize` | `false` | Classifier mode: renormalize probabilities over the surviving (registered) labels. |
| `low_tier` | `prototype` | Classifier mode: the engine behind the `-low` stage, `prototype` (skill examples) or `classifier` (trained head at `conf_low`). |
| `low_prototype` | `{}` | Classifier mode: prototype-mode keys for the `-low` stage, such as `conf_low` or `prototype_k`. |
| `timeout` | `1` | Seconds to wait for the Adapt/Padatious manifest sync at startup. |

Prototype mode adds seven more keys controlling how prototype embeddings are
selected per label, cached on disk and loaded prebuilt:

| Key | Default | Description |
|-----|---------|-------------|
| `prototype_k` | unlimited | Cap on stored prototype embeddings per label (subsample/cluster via `prototype_strategy`). |
| `prototype_strategy` | `max_over_all` | How utterance embeddings are reduced to per-label prototypes. |
| `prototype_top_k` | `3` | Number of best prototype matches aggregated per label. |
| `prototype_tau` | `0.1` | Softmax temperature for prototype score aggregation. |
| `prototype_cache` | `true` | Cache encoded prototypes on disk per skill, keyed on the registration's example utterances, instead of re-encoding on every boot. |
| `prototype_cache_dir` | `{XDG_DATA_HOME}/mycroft/m2v_prototypes/` | Where the per-skill cache files live. |
| `prebuilt_prototypes` | *(unset)* | Local directory or Hugging Face repo id of a prebuilt prototype artifact, made with `ovos-m2v-prototypes export`. A matching artifact skips the encoding step at boot, which shortens start-up on a Raspberry Pi. An artifact built for another model or `model2vec` version is ignored. |

> The model is **pretrained**. It does not learn new skills at runtime. The
> registered-intent filter just decides which of the model's known labels are
> eligible. In prototype mode the store is rebuilt at runtime, but only from the
> example utterances Padatious skills provide.

---

## Models

`OpenVoiceOS/ovos-m2v-intents-multilingual` is the default for every language with
no `models` entry. It is an embedding model plus a trained classifier head, fit on
the OVOS skill intent corpus. The plugin loads its `int8` folder by default.

`OpenVoiceOS/ovos-m2v-intents-en` is an English-only alternative with smaller
folders down to about 8 MB. It is not the default for any language. Select it with
`models["en"]`.

For devices with little memory, such as a Raspberry Pi, the multilingual repository
also holds one folder per language (`pt`, `es`, `ca`, `da`, `de`, `nl`, `sv`, `gl`,
`eu`). Each folder is an int8 copy with its vocabulary cut to that language. Select
one with a `models` entry:

```json
{
  "intents": {
    "ovos-m2v-pipeline": {
      "models": {
        "pt": {"model": "OpenVoiceOS/ovos-m2v-intents-multilingual", "subfolder": "pt"}
      }
    }
  }
}
```

A cut folder can misread words of another language, for example an English request
on a Portuguese install.

!!! warning "Alpha channel only"
    The `OpenVoiceOS/ovos-m2v-intents-*` defaults, the `-low` prototype stage,
    `subfolder` and `prebuilt_prototypes` are in the prerelease channel only. The stable
    `ovos-m2v-pipeline` 0.0.9 loads
    `Jarbas/ovos-model2vec-intents-distiluse-base-multilingual-cased-v2` by default.

---

## Training your own model

The published `OpenVoiceOS/ovos-m2v-intents-*` models are built from a
`train/` toolchain shipped inside the `ovos-m2v-pipeline` source repository
(it is not part of the installed pip package). The dataset builder reads every
skill at its `dev` branch head when a build starts and records each resolved
commit in `manifest.json`. A classifier's label head is frozen at fit time, so a
skill that renames or merges an intent needs a refit before its labels are
correct again.

```
train/
├── sources.yaml        # every source: a repository and its branch
├── build_dataset.py    # resolve, normalise, dedup, split, write the manifest
├── train.py            # fit a classifier on the built corpus
├── distill.py          # distill a Sentence Transformer into a Model2Vec base
└── predict.py           # inference smoke test
```

1. **Build the dataset**: `python train/build_dataset.py --workspace <repos> --out train/dataset`
   fetches every source in `sources.yaml` at its branch head, deduplicates rows, and
   writes `train.parquet`/`test.parquet` (plus JSONL twins), `labels.json`,
   and `manifest.json`. Labels are `<skill_id>:<intent_name>`, exactly as the
   pipeline registers them at runtime. A branch that does not exist stops the
   build. `train/build_from_skills.py --from-manifest <manifest.json>` rebuilds a
   corpus at exactly the commits a manifest records.
2. **Train**: `python train/train.py --dataset train/dataset --base-model <model>`
   fits a classifier on the built corpus.
3. **Optional distillation**: `distill.py` turns a Sentence Transformer that
   has no Model2Vec distillate yet into a usable base model.
4. **Smoke-test**: `predict.py` runs inference against a saved model before
   publishing it.

Point the plugin's `model` config key at your own Hugging Face repo or a local
path to the saved pipeline directory once you are happy with it. See the
`ovos-m2v-pipeline` repository's own `docs/training.md` and `docs/labels.md`
for the full dataset schema, label scheme, and script options.

A separate, exploratory notebook trio covers the same ground interactively —
benchmarking, monolingual, and multilingual classifier training — in
[`m2v/`](https://github.com/TigreGotico/ml-notebooks) under `TigreGotico/ml-notebooks`.
It is not the canonical `train/` toolchain above; use it for experimentation, not
for producing the published `OpenVoiceOS/ovos-m2v-intents-*` models.

---

## Gotcha: ordering against the deterministic engines

Model2Vec generalizes well. This also means it can claim an utterance a more
precise parser would have nailed. The usual setup is to place
`ovos-m2v-pipeline-high` after the high tiers of Padatious/Adapt (or interleaved by
confidence) so exact matches win first and Model2Vec catches the paraphrases the
others miss. Tune `conf_high`/`conf_medium`/`conf_low` to control how aggressive it
is.

Do not copy Padatious's confidence thresholds over verbatim. The two engines score
completely differently, and the two Model2Vec modes also score differently from each
other. `classifier` mode's scores are softmax probabilities out of a trained head.
`prototype` mode's scores are raw cosine similarities against stored example embeddings.
Retune `conf_high`, `conf_medium`, and `conf_low` for whichever mode you run.

---
**Read next:** [Padacioso](padacioso.md)
**Related:** [Padatious Pipeline](padatious-pipeline.md) · [Adapt Pipeline](adapt-pipeline.md) · [Transformers Overview](transformer-plugins.md)
