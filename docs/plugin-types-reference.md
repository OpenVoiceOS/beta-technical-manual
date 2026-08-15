# Plugin Types Reference

!!! abstract "In a nutshell"
    This page is the exhaustive lookup table of every plugin type the
    [OVOS Plugin Manager](plugin-manager.md) (OPM) knows how to discover: its entry
    point group, its template base class, and (for deprecated types) what to use
    instead. Use it to find the exact entry point group and base class for the kind
    of plugin you're writing. For how discovery and loading actually work, and for a
    walkthrough of writing a plugin, see [Plugin Manager](plugin-manager.md).

---

## Plugin Types

All plugin types are defined in the `PluginTypes` enum (`ovos_plugin_manager.utils`).
The entry point group is the canonical identifier used in `setup.py` / `pyproject.toml`.

### Core Voice Pipeline Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| [STT](stt-plugins.md) ([Speech-to-Text](stt-plugins.md)) | `opm.stt` | `ovos_plugin_manager.templates.stt.STT` |
| [TTS](tts-plugins.md) ([Text-to-Speech](tts-plugins.md)) | `opm.tts` | `ovos_plugin_manager.templates.tts.TTS` |
| [Wake word](wake-word-plugins.md) | `opm.wake_word` | `ovos_plugin_manager.templates.hotwords.HotWordEngine` |
| Wake-word Verifier | `opm.wake_word.verifier` | `HotWordVerifier` |
| [VAD](vad-plugins.md) ([Voice Activity Detection](vad-plugins.md)) | `opm.VAD` | `VADEngine` |
| Microphone | `opm.microphone` | `Microphone` |
| G2P (Grapheme-to-Phoneme) | `opm.g2p` | `Grapheme2PhonemePlugin` |
| Audio→IPA | `opm.audio2ipa` | `Audio2IPA` |
| Voice Clone | `opm.vc` | `VoiceClonePlugin` |

### System & Hardware Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| [PHAL](phal.md) (user) | `opm.phal` | `PHALPlugin` |
| PHAL (admin/root) | `opm.phal.admin` | `AdminPlugin` |
| GUI | `opm.gui` | `GUIExtension` |

!!! warning "Upcoming, unreleased"
    A dedicated GUI-adapter plugin type (entry point `opm.gui_adapter`, base class
    `AbstractGUIPlugin`) is in development. Tracked in
    [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377).
    Until it lands, the current GUI plugin type is `opm.gui` (`GUIExtension`).

!!! note "How many can run at once?"
    The core voice-pipeline plugin types (`opm.stt`, `opm.tts`, `opm.wake_word`, `opm.VAD`,
    `opm.microphone`) are **singleton per service**: their factory (`OVOSSTTFactory`,
    `OVOSTTSFactory`, etc.) reads a single `module` config key and instantiates exactly one
    active engine. This is unlike the six transformer chains below, which are explicitly
    multi-instance and run all configured plugins of a type in priority order.

    Discovery is also name-keyed: if two installed packages register the same entry-point
    name under the same group, OPM keys them by that name, so one silently shadows the other
    with no error. Avoid duplicate plugin names across packages.

    For the singleton core types this collision happens *before* the factory ever runs: the
    factory (`OVOSSTTFactory.create()`, `OVOSTTSFactory.create()`, etc.) just asks
    `find_*_plugins()` for whichever class is registered under the configured `module` name
    and instantiates it. If two packages registered that same entry-point name, discovery has
    already picked one of them silently at import time. The factory has no way to detect or
    warn about the collision, it only ever sees the single class discovery handed it.

### Transformer Plugins

These six types are the six ordered chains of [OVOS-TRANSFORM-1](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md). Each one is injected at a fixed point in the utterance lifecycle (audio → utterance → metadata → intent → dialog → tts) and runs in **ascending** priority order.

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Audio Transformer | `opm.transformer.audio` | `AudioTransformer` |
| Dialog Transformer | `opm.transformer.dialog` | `DialogTransformer` |
| TTS Transformer | `opm.transformer.tts` | `TTSTransformer` |
| [Utterance](life-of-an-utterance.md) Transformer | `opm.transformer.text` | `UtteranceTransformer` |
| Metadata Transformer | `opm.transformer.metadata` | `MetadataTransformer` |
| Intent Transformer | `opm.transformer.intent` | `IntentTransformer` |

#### Canonical chain runners: `ovos_plugin_manager.transformer_services`

Loading, ordering, and chaining transformer plugins used to be reimplemented separately by
each consumer. `ovos_plugin_manager.transformer_services` is now the single shared
implementation: `ovos-core`, `ovos-audio`, `ovos-dinkum-listener`, HiveMind, and the OVOS
TTS/STT servers all build their transformer chains from this module instead of maintaining
their own copies. It exposes one runner class per transformer type:

| Class | Transformer type |
|---|---|
| `UtteranceTransformersService` | `opm.transformer.text` |
| `MetadataTransformersService` | `opm.transformer.metadata` |
| `IntentTransformersService` | `opm.transformer.intent` |
| `DialogTransformersService` | `opm.transformer.dialog` |
| `TTSTransformersService` | `opm.transformer.tts` |
| `AudioTransformersService` | `opm.transformer.audio` |

Loading is config-gated and opt-in. A plugin only runs if its name appears in the relevant
config section and its entry does not set `"active": false`. Ordering follows
[OVOS-TRANSFORM-1](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md) §4:
plugins run in ascending `priority` order by default, but an explicit `"order"` list of
plugin names in the config section overrides priority-based ordering. Loaded plugins absent
from that list are not run. A plugin can cancel the rest of the chain by returning both
`"canceled": true` and a `"cancel_reason"` in its context (§8.1).

### Language Processing Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Language Translator | `opm.lang.translate` | `LanguageTranslator` |
| Language Detector | `opm.lang.detect` | `LanguageDetector` |
| Keyword Extraction | `opm.keywords` | `KeywordExtractor` |
| Utterance Segmentation | `opm.segmentation` | `Segmenter` |
| Tokenization | `opm.tokenization` | `Tokenizer` |
| POS Tagger | `opm.postag` | `PosTagger` |

### Intent Pipeline Plugins

A pipeline plugin is a matcher exposing `match(utterances, lang, session) → Match | None`. The orchestrator runs the configured set in order, **first-match-wins**, with no cross-plugin scoring ([OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)).

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Pipeline | `opm.pipeline` | `PipelinePlugin` |

!!! note "Minimum OPM version"
    The transformer (`opm.transformer.*`) and solver (`opm.solver.*`) groups require
    `ovos-plugin-manager>=2.1.0`. The agent groups (`opm.agents.*`) require
    `ovos-plugin-manager>=2.4.0a1` (the option-matcher group arrived last). Pin
    accordingly in your plugin's dependencies (cap below `<3.0.0`).

### Media Plugins

| Plugin type | Entry point group |
|---|---|
| [OCP](ocp-pipeline.md) Stream Extractor | `opm.ocp.extractor` |
| Audio Player | `opm.media.audio` |
| Video Player | `opm.media.video` |
| Web Player | `opm.media.web` |
| Media Provider | `opm.media.provider` |
| Legacy audio backend | `mycroft.plugin.audioservice` — deprecated but still discovered at runtime; it has no `opm.*` rename (`opm.media.audio` is a distinct newer type, not its replacement). Used by the classic [audio backends](ocp-audio-plugin.md) |

### Agent Plugins

Every base class below is in `ovos_plugin_manager.templates.agents`, except `ToolBox`, which
the table marks.

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Chat | `opm.agents.chat` | `ChatEngine` |
| Chat (multimodal) | `opm.agents.chat.multimodal` | `MultimodalChatEngine` |
| Multimodal adapter | `opm.agents.multimodal_adapter` | `MultimodalAdapter` |
| Retrieval | `opm.agents.retrieval` | `RetrievalEngine` |
| Document retrieval | `opm.agents.retrieval.documents` | `DocumentIndexerEngine` |
| Q/A retrieval | `opm.agents.retrieval.qa` | `QAIndexerEngine` |
| Summarizer | `opm.agents.summarizer` | `SummarizerEngine` |
| Chat summarizer | `opm.agents.summarizer.chat` | `ChatSummarizerEngine` |
| Extractive QA | `opm.agents.extractive_qa` | `ExtractiveQAEngine` |
| NLI | `opm.agents.nli` | `NaturalLanguageInferenceEngine` |
| Reranker | `opm.agents.reranker` | `ReRankerEngine` |
| Coreference | `opm.agents.coref` | `CoreferenceEngine` |
| Yes/No | `opm.agents.yesno` | `YesNoEngine` |
| Toolbox | `opm.agents.toolbox` | `ToolBox` (in `ovos_plugin_manager.templates.agent_tools`) |
| Memory | `opm.agents.memory` | `AgentContextManager` |
| Option Matcher | `opm.agents.option_matcher` | `OptionMatcherEngine` |

### Embeddings & Knowledge Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| Embeddings (generic) | `opm.embeddings` | `EmbeddingsDB` |
| Text embeddings | `opm.embeddings.text` | `TextEmbedder` |
| Voice embeddings | `opm.embeddings.voice` | `VoiceEmbedder` |
| Image embeddings | `opm.embeddings.image` | `ImageEmbedder` |
| Face embeddings | `opm.embeddings.face` | `FaceEmbedder` |
| Knowledge triples | `opm.triples` | `TriplesExtractor` |

### Skill & Persona Plugins

| Plugin type | Entry point group | Template base class |
|---|---|---|
| [Skill](skill-design-guidelines.md) | `opm.skill` | None |
| [Persona](personas.md) | `opm.plugin.persona` | None |

### Deprecated Types

These are still recognized (mapped to canonical names internally) but should not be used
in new plugins. This section covers **entry-point-level** deprecations, where an old entry
point group was renamed to a canonical one. For **repo-level** deprecations, where an entire
plugin/repository was retired in favor of a different package, see
[Deprecated & Archived Repositories](deprecated-repos.md).

| Old entry point group | Canonical |
|---|---|
| `mycroft.plugin.stt` | `opm.stt` |
| `mycroft.plugin.tts` | `opm.tts` |
| `mycroft.plugin.wake_word` | `opm.wake_word` |
| `ovos.plugin.phal` | `opm.phal` |
| `ovos.plugin.phal.admin` | `opm.phal.admin` |
| `ovos.plugin.VAD` | `opm.VAD` |
| `ovos.plugin.microphone` | `opm.microphone` |
| `ovos.plugin.skill` | `opm.skill` |
| `ovos.plugin.g2p` | `opm.g2p` |
| `ovos.plugin.audio2ipa` | `opm.audio2ipa` |
| `ovos.plugin.gui` | `opm.gui` |
| `ovos.ocp.extractor` | `opm.ocp.extractor` |
| `neon.plugin.lang.translate` | `opm.lang.translate` |
| `neon.plugin.lang.detect` | `opm.lang.detect` |
| `neon.plugin.text` | `opm.transformer.text` |
| `neon.plugin.metadata` | `opm.transformer.metadata` |
| `neon.plugin.audio` | `opm.transformer.audio` |
| `neon.plugin.solver` | `opm.solver.question` |
| `intentbox.coreference` | `opm.coreference` |
| `intentbox.keywords` | `opm.keywords` |
| `intentbox.segmentation` | `opm.segmentation` |
| `intentbox.tokenization` | `opm.tokenization` |
| `intentbox.postag` | `opm.postag` |

This table mirrors `ovos_plugin_manager.utils.DEPRECATED_ENTRYPOINTS`. This is the source of truth OPM
uses at runtime to silently rewrite a plugin's old entry-point group to its canonical one, so
plugins published under any of the names above still load correctly today.

The `opm.agents.*` types above supersede the legacy **solver** groups
(`opm.solver.question`, `opm.solver.chat`, `opm.solver.summarization`,
`opm.solver.entailment`, `opm.solver.multiple_choice`, `opm.solver.reading_comprehension`)
and `opm.coreference`. The next major release removes these legacy groups. That release is
the same `ovos-plugin-manager` major-version boundary as the `<3.0.0` cap noted above under
[Minimum OPM version](#plugin-types).

---

## Configuration Utilities

`ovos_plugin_manager.utils.config` provides helpers for resolving plugin configuration
from `mycroft.conf`.

### `get_plugin_config`

```python
def get_plugin_config(
    config: Optional[dict] = None,
    section: str = None,
    module: Optional[str] = None,
) -> dict

```

Resolve a merged configuration dict for a plugin. Precedence (highest to lowest):

1. Module-specific block: `config[section][module]`


2. Section-level defaults: `config[section]` (scalar keys only)


3. Top-level `lang`: `config['lang']`

```python
from ovos_plugin_manager.utils.config import get_plugin_config

cfg = get_plugin_config(section="stt", module="ovos-stt-plugin-whisper")

# {'module': 'ovos-stt-plugin-whisper', 'lang': 'en-US', ...}

```

### `load_plugin_configs`

```python
def load_plugin_configs(
    plug_name: str,
    plug_type: Optional[PluginConfigTypes] = None,
    normalize_language_keys: bool = False,
) -> Union[dict, list]

```

Load language/variant configuration for a single plugin by calling its `.config` entry point.
Returns `{lang: [list_of_config_dicts]}`.

### `load_configs_for_plugin_type`

```python
def load_configs_for_plugin_type(plug_type: PluginTypes) -> dict

```

Load configs for **all** installed plugins of the given type.
Returns `{plugin_name: {lang: [configs]}}`.

### `get_plugin_language_configs`

```python
def get_plugin_language_configs(
    plug_type: PluginTypes,
    lang: str,
    include_dialects: bool = False,
) -> dict

```

Return configs for all plugins of `plug_type` that support `lang`.
Returns `{plugin_name: [list_of_valid_config_dicts]}`.

When `include_dialects=True`, configs for closely related dialects (linguistic distance
under 10, via `ovos_spec_tools.lang_distance`) are also included. A dialect match has its
`priority` raised by 15 (`get_valid_plugin_configs` in `ovos_plugin_manager.utils.config`).
Since lower priority numbers are selected first, this makes dialect matches lower
precedence than an exact language/locale match.

### `get_plugin_supported_languages`

```python
def get_plugin_supported_languages(plug_type: PluginTypes) -> dict

```

Return `{lang: [plugin_name, ...]}` mapping language codes to all plugins supporting them.

### `sort_plugin_configs`

```python
def sort_plugin_configs(configs: dict) -> dict

```

Sort each plugin's config list by the `"priority"` key (lower = higher priority).
Invalid/empty config lists are removed.

---
**Read next:** [Plugin Manager](plugin-manager.md)
**Related:** [Choosing Plugins](choosing-plugins.md) · [Formal Specifications](architecture-specs.md) · [Transformers Overview](transformer-plugins.md)
