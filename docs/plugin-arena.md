# Plugin Arena

!!! abstract "In a nutshell"
    OVOS lets you swap in different plugins for jobs like understanding speech or recognizing commands. Which one is best? The Plugin Arena answers that by comparing them two ways: objective scores measured against test data, and a "which sounds better?" vote where people blindly pick between two plugins' results, scored a bit like chess rankings. It is purely a scoreboard for comparing plugins. It never installs or runs them itself. See the [Glossary](glossary.md) for unfamiliar terms.

The arena runs live at [openvoiceos.github.io/ovos-plugin-arena](https://openvoiceos.github.io/ovos-plugin-arena), with source and battle definitions at [OpenVoiceOS/ovos-plugin-arena](https://github.com/OpenVoiceOS/ovos-plugin-arena). Each league has automated A/B battles and ELO standings, seeded from benchmarks. Human votes refine the ratings.

**What this is:** a way to answer *"which OVOS plugin should I use?"* It compares plugins on two signals:

1. **Benchmarks**: accuracy/F1 for intent, WER for STT, detection metrics and false wake-ups per hour for wake word. These are
   computed offline against labeled datasets and published openly as HuggingFace datasets.
2. **Human preference**: chess-style ELO ratings from blind A/B "battles" where people pick the
   better of two plugin outputs. The initial ELO is seeded from the benchmarks. Human votes refine
   it.

The arena is the *rating and voting* venue, **not** an execution venue. It never installs, isolates, or runs plugins.

---

## GitHub-Native, Zero Servers

The arena is a **repository**, not a service. There is no backend, no database, and no account system:

- **Data artifacts** are JSON files committed by scheduled GitHub Actions (`assemble.yml` daily, `tally.yml` hourly).
- **The UI** is a static Astro site published to **GitHub Pages**.
- **Votes** are **GitHub issues**.
- **Plugin predictions** are produced *outside* the arena as offline batch jobs and published as HuggingFace datasets.

Forking the repo and editing JSON yields a working arena. A local FastAPI shim may exist as a development tool only; it is not a deployment target.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **GitHub-native** | Artifacts are committed JSON, the UI is GitHub Pages, votes are GitHub issues. No backend, no database. |
| **Decentralized predictions** | Plugins run outside the arena as offline jobs anywhere. The arena never installs or executes plugins in CI. |
| **HuggingFace as artifact layer** | Every prediction run is published as a queryable HF dataset, independent of the arena. |
| **Everything declarative** | Every competitor and dataset is a JSON file under `registry/`. Editing JSON is enough to extend the arena. |
| **Replayable ratings** | Battle ids are content hashes. The ELO seed is a deterministic function of the published predictions. Human votes replay in **issue-number order**. Standings are reproducible from public data alone. |
| **All predictions kept** | Bad predictions are kept, not deleted. Failure cases guide plugin improvements. |

---

## Leagues (Modalities)

Each league has its own datasets, benchmark boards and ELO standings. The leagues are `stt`, `tts`, `vad`, `wake_word`, `ww_stream` and four intent leagues. The [leagues page](https://github.com/OpenVoiceOS/ovos-plugin-arena/blob/dev/docs/leagues.md) lists each league with its task and primary metric.

- The four intent leagues (`intent_zero_shot`, `intent_online`, `intent_offline`, `intent_keyword`) share one `intent` battle pool, because a blind vote cannot see how each engine was prepared. `intent` and `intent_template` are dataset namespaces, not leagues: no competitor is filed under them.
- `ww_stream` is the false wake-up league. Its fighters are the `wake_word` fighters that can stream. They listen to hours of audio with no wake word, and the board ranks them on `fa_per_hour`, lower is better.
- The site lists a wake word board only when it compares trained models: the test set must hold enough positive clips, and at least two trained models must rank on it. The [false wake-up page](https://github.com/OpenVoiceOS/ovos-plugin-arena/blob/dev/docs/leagues/ww_stream.md) gives the rule.

A "competitor" is a **shippable config**, not only a plugin. A single-stage pipeline benchmarks one engine. A multi-stage pipeline is an ensemble fighter in its own right. The same plugin under a different config is a *different competitor*. `competitor_id` is the stable key for predictions, battles, ELO and leaderboards.

---

## Declarative Registry

- **Competitors**: `registry/competitors/<modality>/<id>.json`. For intent, `config` is a valid `mycroft.conf` fragment (an `intents` section with an ordered `pipeline` of `<plugin>-<tier>` stages).
- **Datasets**: `registry/datasets/<modality>/<id>.json`. One corpus per entry: HF source id + revision, `reference_fields` (the datashape contract), license, `lang` (or `lang: multi` + `langs`), and a `role` (`train`/`eval`). Keyword and template training corpora are distinct datasets with distinct datashapes.

## Getting Your Plugin Ranked

You do not run any benchmarks yourself. A competitor is *a configuration you could ship*. The
same plugin under a different config counts as a different fighter. Once its registry entry
is merged, the arena's sweep runs it against the pinned datasets and it appears on the boards.

The plugin must be published to PyPI first. The arena itself never installs plugins (see
[GitHub-Native, Zero Servers](#github-native-zero-servers) above). Whoever runs the offline
prediction job that produces the competitor's HuggingFace dataset needs to `pip install` the
plugin by name, which only works once it is on PyPI. See [TTS Plugins: Package and
publish](tts-plugin-development.md#package-and-publish) or [Writing a Transformer Plugin: Package and
publish](transformer-plugin-development.md#package-and-publish) for the steps to get there.

1. Add a JSON file at `registry/competitors/<modality>/<competitor-id>.json`, where `<modality>`
   is a league that has a competitor directory (`ww_stream` has none: it reuses `wake_word`
   fighters). See the [leagues page](https://github.com/OpenVoiceOS/ovos-plugin-arena/blob/dev/docs/leagues.md). Required fields are `competitor_id`, `modality`
   and `config` (a valid `mycroft.conf` fragment). Non-intent fighters also need `plugin`, the OPM
   entry-point name. Intent fighters describe an ordered `config.intents.pipeline` of
   `<plugin>-<tier>` stages. A single stage benchmarks one engine, several stages make an
   ensemble, and `plugin` is derived automatically for the single-stage case.
2. Validate locally with `uv run pytest tests/test_registry.py`, which checks every competitor
   file against the schema. CI runs the same test under the reusable `build_tests` job (`test_path: tests/`).
3. Open a pull request. The sweep and the boards do the rest. The fighter then gets an embeddable
   rank badge for its README.

Optional metadata — `display_name`, `species`, `types`, `size`, `description`, `model`, `links` —
populates the fighter's card in the browser. The full field reference, including the `size`
footprint classes, lives in
[add-a-fighter](https://github.com/OpenVoiceOS/ovos-plugin-arena/blob/dev/docs/add-a-fighter.md).

---

## Prediction Contract (HuggingFace)

Predictions live in HF dataset repos — one per benchmark modality, named `ovos-<modality>-bench-<dataset_id>` (league underscores dashed). Intent predictions use one repo per paradigm, `ovos-intent-<paradigm>-bench-<dataset_id>`. Rows are stored as per-competitor JSON lines at `predictions/<competitor_id>.jsonl`, one row per sample (language is a field on each row, not a path segment).

Core `PredictionRow` fields (`arena/models.py`):

| Field | Notes |
|--------|-------|
| `competitor_id` | Stable competitor key |
| `sample_id` | Stable ID within the source dataset |
| `dataset_id` | Source corpus identifier |
| `lang` | BCP-47 |
| `modality` | League (inferred from fields when absent) |
| `plugin_id`, `plugin_version` | Plugin name + exact installed version |
| `prediction` | Modality-specific payload |
| `runner_version` | Reproducibility anchor |
| `created_at` | Timestamp |

Modality-specific fields (kept inline or in `extras`):

- **Intent**: `utterance`, `reference_intent`, `exact_match`, `confidence`, `bucket`, `reference_slots`, `predicted_slots`.
- **STT**: `reference_text`, `wer`.
- **Shared diagnostics**: `latency_ms`.

---

## ELO Ratings

- Standard ELO formula (`arena/elo.py`): `K_FACTOR = 32` for new competitors (`< 30` battles), `K_FACTOR_VETERAN = 16` once past the `VETERAN_THRESHOLD = 30` battles.
- The ELO seed is derived deterministically from the published benchmark predictions. Human votes (GitHub issues) replay in issue-number order on top of it.
- Automatic benchmark-seeded votes are down-weighted relative to human votes: `AUTO_K_DIVISOR = 4.0`, so auto votes carry a quarter of the K-weight of a human vote. `k_factor(battles, auto=True)` divides K by 4. The Bradley-Terry path uses the matching `BT_AUTO_WEIGHT = 1/4`.
- Standings are fully recomputable from public data alone. The leaderboard JSON committed by `tally.yml` is a cache, not the source of truth.

---

## Benchmarks

The [benchmarks page](https://github.com/OpenVoiceOS/ovos-plugin-arena/blob/dev/docs/benchmarks.md) lists the benchmark notebooks and scripts for each league, and tells how to run them.

---

## Registry Validation, Scoring, and Provenance

- **Registry validation**: `tests/test_registry.py` validates every competitor/dataset JSON file under `registry/` against the schema. This catches a malformed registry entry in CI (under the reusable `build_tests` job) before it can silently break assembly. Run it locally with `uv run pytest tests/test_registry.py`.
- **WER normalization**: STT scoring normalizes both sides through `normalize_transcript` (`arena/metrics.py`) before tokenizing: NFKC normalization, casefolding, digit-by-digit numeral spelling, punctuation stripping, and whitespace collapsing — so scores ignore raw punctuation/casing/numeral-formatting differences. Both `row_wer` and `row_wer_components` (the latter used for WER bootstrap CIs) are **recompute-first**: they prefer recomputing from raw `reference_text`/`prediction` so scores stay comparable across runners that may have normalized differently before persisting, and fall back to the stored `wer` only when the raw text is unavailable.
- **Version-blend guard**: if a competitor's rows span more than one `plugin_version`, the board build logs a warning rather than silently averaging scores across versions.
- **Reproducible predictions provenance**: `assemble` pins every HuggingFace predictions source to an immutable commit SHA (the dataset registry entry's `predictions_revision` when set, else `--revision`). It records the resolved mapping on each benchmark board (`predictions_revisions`) and in the top-level index. This lets a third party re-fetch the exact predictions that produced any published score.

---
**Read next:** [Choosing Plugins](choosing-plugins.md) · [Microphone Plugins](mic-plugins.md)
**Related:** [Maturity Scale](maturity.md) · [STT Plugins](stt-plugins.md) · [TTS Plugins](tts-plugins.md) · [Wake-word Verifier](ww-verifier.md)
