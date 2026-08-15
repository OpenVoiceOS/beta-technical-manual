# Updating Plugins From Older OVOS

## In a nutshell

This page is for maintainers of [STT](stt-plugins.md), [TTS](tts-plugins.md), [wake word](wake-word-plugins.md), audio-backend, [media](media-plugins.md),
[GUI-adapter](gui-adapters.md), [PHAL](phal.md), and solver/engine plugins moving forward from an older
OVOS install. Entries are in date order: start at the version you are
currently running and read forward to your target version. For the
Big-ticket migrations (the changes with the widest blast radius, including
the wake-word signature split), see
[Updating from Older OVOS](updating-from-older-ovos.md#big-ticket-migrations).

## If you maintain plugins

### TTS plugin queue tuple shape (ovos-audio)

Direct mutation of `TTS.queue` used a 6-tuple
`(_, data, visemes, ident, listen, tts_id)`. It now expects a 5-tuple
`(data, visemes, listen, tts_id, message)`.

- Migration: push `(data, visemes, listen, tts_id, message)` tuples onto
  `PlaybackThread`'s queue.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `931784a` | |
| Deprecated but functional | from `931784a` (2023-10-25) | logs via `log_deprecation(..., "0.1.0")` |
| Dropped | target was `0.1.0`, exact drop commit unverified | (ovos-audio `931784a`, #37) |

### Audio-backend template methods became abstract

`AudioBackend`/`RemoteAudioBackend` templates in [`ovos-plugin-manager`](plugin-manager.md)
turned previously-optional methods into `@abstractmethod`, and dropped the
dependency on the old `common_play` base class ([OCP](ocp-pipeline.md)'s predecessor).

- Migration: implement every required method on your `AudioBackend`
  subclass or instantiation raises `TypeError: Can't instantiate abstract
  class`.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `77c66a3` | |
| Deprecated but functional | unverified | |
| Dropped | `77c66a3` (2024-05-11) | (ovos-plugin-manager `77c66a3`, #226) |

### STT legacy helper classes deprecated

`StreamingSTT`, `StreamThread`, and related classic-mycroft-derived helper
classes in `ovos_plugin_manager/templates/stt.py` were deprecation-warned,
first via logging (`ff342fe`, #233, 2024-06-03) and later as a real Python
`DeprecationWarning` (`dfbac90`, #291, 2025-01-04): CI suites running
`-W error::DeprecationWarning` will fail the build on continued use.

- Migration: move off `StreamingSTT`/`StreamThread` to the current STT
  template contract.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `ff342fe` | |
| Deprecated but functional | from `ff342fe` (2024-06-03) | warning strength increased in `dfbac90` (2025-01-04) |
| Dropped | drop date unverified | (ovos-plugin-manager `ff342fe`, #233) |

### Dialect matching switched to `tag_distance`

Ad-hoc exact-prefix dialect matching (`en` matches `en-us` via
`.startswith`) was replaced with `langcodes.tag_distance` (threshold
`< 10`) across [STT](stt-plugins.md), [TTS](tts-plugins.md), [wake word](wake-word-plugins.md), and tokenization plugin
[config](config-reference.md) resolution.

- Migration: no code change needed for callers of the public
  `get_plugin_config` family. Re-verify locale resolution after upgrading
  if you pinned plugin configs to exact locale strings, since dialect
  fallback selection can differ.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | behavior-only change, no removal | |
| Deprecated but functional | n/a | |
| Dropped | landed `08ad348` (2024-10-12) | (ovos-plugin-manager `08ad348`, #267) |

Later replaced again by `ovos_spec_tools.lang_distance` in `35919b7`
(#391, 2026-05-22), same `< 10` threshold preserved. Requires the
`ovos-spec-tools[langcodes]` extra or region codes silently strip
(`en-US` → `en`).

### G2P deprecated, moved toward ovos-audio

`opm.g2p` (Grapheme2Phoneme, used only for MK1 mouth animation) is marked
deprecated in `ovos-plugin-manager`. The companion work moves it toward
`ovos-audio`.

- Migration: no functional removal yet in `ovos-plugin-manager`. Expect
  deprecation warnings on every access.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `c102889` | |
| Deprecated but functional | from `c102889` (2024-10-23) | |
| Dropped | drop version unverified | (ovos-plugin-manager `c102889`, #277) |

### `EmbeddingsDB` gains required collection methods

`create_collection`, `get_collection`, `delete_collection`,
`list_collections` became required `@abstractmethod`s on `EmbeddingsDB`.

- Migration: implement all four on your `EmbeddingsDB` subclass.
  single-collection plugins can wrap a fixed default collection name.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `15beb84` | |
| Deprecated but functional | none | added directly as abstract |
| Dropped | landed `15beb84` (2025-07-22) | (ovos-plugin-manager `15beb84`, #333) |

### `opm.*` canonical entry-point rename

Every `PluginTypes`/`PluginConfigTypes` entry-point group string that had
carried a `# TODO rename` comment was flipped to the canonical `opm.*`
form. Old groups keep working through a `DEPRECATED_ENTRYPOINTS` alias
table (with a warning), but comparing `PluginTypes.STT.value` against the
old literal string breaks.

| Old group | New canonical group |
|---|---|
| `mycroft.plugin.stt` | `opm.stt` |
| `mycroft.plugin.tts` | `opm.tts` |
| `mycroft.plugin.wake_word` | `opm.wake_word` |
| `ovos.plugin.gui` | `opm.gui` |
| `ovos.plugin.phal` | `opm.phal` |
| `ovos.plugin.skill` | `opm.skill` |
| `ovos.plugin.microphone` | `opm.microphone` |
| `ovos.plugin.VAD` | `opm.VAD` |
| `ovos.plugin.g2p` | `opm.g2p` |
| `neon.plugin.solver` | `opm.solver.question` |
| `neon.plugin.text` / `.metadata` / `.audio` | `opm.transformer.text` / `.metadata` / `.audio` |
| `neon.plugin.lang.translate` / `.detect` | `opm.lang.translate` / `.detect` |
| `intentbox.coreference` / `.keywords` / `.segmentation` / `.tokenization` / `.postag` | `opm.coreference` / `opm.keywords` / `opm.segmentation` / `opm.tokenization` / `opm.postag` |
| `ovos.ocp.extractor` | `opm.ocp.extractor` |

- Migration: update `entry_points` in your plugin's `setup.py`/
  `pyproject.toml` to the new group at your convenience. Old groups still
  work via the alias table. Code comparing enum values as raw strings
  should compare against `PluginTypes.STT` (the enum member), not the
  literal old string.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `15beb84` | |
| Deprecated but functional | from `15beb84` (2025-07-22) | aliased, with a warning |
| Dropped | no stated removal version as of the sweep | treat as indefinitely deprecated (ovos-plugin-manager `15beb84`, #333) |

A case-sensitivity bug in the alias table (`ovos.plugin.VAD` mapped to
lowercase `opm.vad` instead of `opm.VAD`) silently broke discovery of
un-migrated VAD plugins for about eleven months, fixed in `3a7a330`
(#401, 2026-06-16).

### Solver plugin family deprecated in favor of agent engines

The entire `templates/solvers.py` family (`QuestionSolver`, `CorpusSolver`,
`TldrSolver`, `EvidenceSolver`, `MultipleChoiceSolver`, `EntailmentSolver`)
is deprecated with a stated removal target of the next major version.

| Deprecated | Replacement |
|---|---|
| `QuestionSolver` | `ChatEngine` / `RetrievalEngine` |
| `CorpusSolver` | `DocumentIndexerEngine` / `QAIndexerEngine` |
| `TldrSolver` | `SummarizerEngine` |
| `EvidenceSolver` | `ExtractiveQAEngine` |
| `MultipleChoiceSolver` | `ReRankerEngine` |
| `EntailmentSolver` | `NaturalLanguageInferenceEngine` |

- Migration: move to the matching `templates/agents.py` [agent engine](agent-plugins.md) class
  before the removal version ships.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `53564ce` | |
| Deprecated but functional | from `53564ce` (2026-01-29) | `opm.solver.*` entry points still discoverable |
| Dropped | removal target is the current major version plus one, not yet shipped as of `53564ce` | (ovos-plugin-manager, #365) |

`ovos-bus-client`'s parallel `opm.py` (`neon.plugin.solver`-based chat
class) was already removed outright in `d526e99` (#207, 2026-05-18,
`2.0.0`): migrate to `ovos-messagebus-chat-plugin`.

### Pending plugin-surface changes

Three further breaking changes to plugin templates (GUI adapters gaining
`session_id`, the PHAL enclosure-abstraction drop, and the `MediaProvider`
surface) exist only as open pull requests. Nothing shipped implements them.
See [Upcoming Changes](upcoming-changes.md) for the PR-by-PR status.

---

**Read next:** [Version-Compatible Skills & Plugins](version-compat-guide.md) · [Upcoming Changes](upcoming-changes.md)
**Related:** [Updating from Older OVOS](updating-from-older-ovos.md) · [Media Service (ovos-media)](ovos-media.md)
