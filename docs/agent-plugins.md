# Agent Plugins

!!! abstract "In a nutshell"
    Agent plugins are the swappable "brains" your assistant can use to do thinking work: holding a conversation, answering a factual question, summarizing a document, picking the best of several answers, remembering what was said earlier, or figuring out who "she" refers to. You don't run them yourself. You list the ones you want in a [persona](personas.md), and OVOS loads them. Think of it like choosing which browser extensions to install, except each "extension" is a different reasoning skill. See [Agents & Personas](personas.md) or the [Glossary](glossary.md) for related terms.

**For beginners:** agent plugins are the installable building blocks that let a persona think,
answer, rank, summarize, remember, or resolve pronouns. You don't call them directly. You list
them in a [persona](personas.md) and the [PersonaService](personas.md#personaservice-pipeline-plugin)
loads them. Each plugin advertises itself to OVOS through an OPM entry-point group.

!!! note "Version requirement"
    The agent plugin system (`opm.agents.*` entry-point groups) requires
    **`ovos-plugin-manager >= 2.3.0a1`** (cap below `<3.0.0`). Older OPM releases don't
    know these groups.

**For advanced users:** every agent engine subclasses an abstract base in
`ovos_plugin_manager.templates.agents` and registers under one `opm.agents.*` group (each with a
parallel `*.config` group for config metadata). The discovery helpers live in
`ovos_plugin_manager.agents`. The authoritative group/base-class mapping:

| Entry-point group | Base class | Purpose |
|---|---|---|
| `opm.agents.chat` | `ChatEngine` | Multi-turn conversational LLM |
| `opm.agents.chat.multimodal` | `MultimodalChatEngine` | Chat with image/audio/file input |
| `opm.agents.multimodal_adapter` | `MultimodalAdapter` | Render non-text content as text |
| `opm.agents.summarizer` | `SummarizerEngine` | Condense a document |
| `opm.agents.summarizer.chat` | `ChatSummarizerEngine` | Compress a chat history |
| `opm.agents.reranker` | `ReRankerEngine` | Score/rank candidate answers |
| `opm.agents.option_matcher` | `OptionMatcherEngine` | Match an utterance to a fixed option set |
| `opm.agents.extractive_qa` | `ExtractiveQAEngine` | Extract the answering passage from evidence |
| `opm.agents.nli` | `NaturalLanguageInferenceEngine` | Premise → hypothesis entailment |
| `opm.agents.yesno` | `YesNoEngine` | Classify a response as yes / no / unknown |
| `opm.agents.coref` | `CoreferenceEngine` | Pronoun / coreference resolution |
| `opm.agents.memory` | `AgentContextManager` | Per-session conversation history |
| `opm.agents.retrieval` | `RetrievalEngine` | Retrieval-augmented generation |
| `opm.agents.retrieval.documents` | `DocumentIndexerEngine` | Index + retrieve over a document corpus |
| `opm.agents.retrieval.qa` | `QAIndexerEngine` | Index + retrieve over a Q/A corpus |
| `opm.agents.toolbox` | none | Tool / function-calling registry |

To write your own engine, see [Building Agent Plugins](building-agent-plugins.md) for
the base-class decision guide, method contracts, packaging walkthroughs, and the solver
migration path.

The legacy `opm.solver.*` groups (and the `QuestionSolver` family in
`ovos_plugin_manager.templates.solvers`) are deprecated. See [Deprecated Solver
Types](#deprecated-solver-types) below for the migration map. For per-engine method contracts and
config examples, see [Agent Engine Types](#agent-engine-types) below and [Agents &
Personas](personas.md).

---

## Agent Engine Types

OVOS provides a full suite of specialized agent engine types beyond simple chat. Each type solves
a specific NLP sub-problem and registers under its own OPM entry point group. This makes it
discoverable, configurable, and usable together with other engine types on its own.

All base classes live in `ovos_plugin_manager.templates.agents`. The deprecated solver API
(`opm.solver.*`) is covered in [Deprecated Solver Types](#deprecated-solver-types) below. Migrate
to `opm.agents.*` for all new plugins.

### ReRanker: `opm.agents.reranker`

**Base class:** `ReRankerEngine`

Scores a list of candidate answers by relevance to a query and returns them ranked highest-first.
Used internally by the [Common Query pipeline](cq-pipeline.md) and
[OCP](ocp-pipeline.md) media search.

```python
from ovos_plugin_manager.templates.agents import ReRankerEngine

# Returns: List[Tuple[float, str]] sorted descending
ranked = engine.rerank("play bohemian rhapsody", ["Bohemian Rhapsody by Queen", "Bohemian Groove Mix"])
best = engine.select_answer("play bohemian rhapsody", candidates)

```

!!! note "Score semantics"
    `ReRankerEngine.rerank()` returns `(score, option)` pairs, but the base class does
    **not** fix the score's scale. It is whatever the underlying model produces. There
    is no `ReRankerEngine` implementation shipped by an OpenVoiceOS-org repository yet.
    A community reranker plugin such as `ovos-flashrank-reranker-plugin` applies a
    sigmoid (binary cross-encoder) or softmax (multi-class) normalization internally,
    so its scores land in **`[0, 1]`** and read as a relevance/similarity value, with
    `min_reranker_score` tunable as a plain probability-like threshold against it. A
    different reranker plugin backed by a raw-logit model would need its own
    calibration. Check that plugin's docs before reusing the same threshold.

#### Common Query pipeline config

```json
{
  "intents": {
    "ovos-common-query-pipeline-plugin": {
      "min_self_confidence": 0.5,
      "min_reranker_score": 0.5,
      "reranker": "<your-reranker-plugin>",
      "<your-reranker-plugin>": {}
    }
  }
}

```

The `reranker` key names any installed `opm.agents.reranker` plugin.

---

### Extractive QA: `opm.agents.extractive_qa`

**Base class:** `ExtractiveQAEngine`

Given a paragraph of evidence text and a question, returns the exact sentence(s) that answer
the question. Used by knowledge-retrieval skills (Wikipedia, news reader) to avoid speaking
entire documents.

```python
evidence = (
    "The Eiffel Tower stands 330 metres tall. "
    "It was constructed from 1887 to 1889 as the centrepiece of the 1889 World's Fair."
)
answer = engine.get_best_passage(evidence, "How tall is the Eiffel Tower?")

# "The Eiffel Tower stands 330 metres tall."

```

Available implementations: `GGUFExtractiveQAEngine` ([GGUF plugin](gguf-plugin.md)).

---

### Summarizer: `opm.agents.summarizer`

**Base class:** `SummarizerEngine`

Condenses a plain-text document into one to three sentences. Used by solvers and skills before passing
text to [TTS](tts-plugins.md) to avoid overwhelming the user with long responses.

```python
summary = engine.summarize(long_article_text)

```

Implementations: `OpenAISummarizer`, `GGUFSummarizerEngine`.

---

### Chat Summarizer: `opm.agents.summarizer.chat`

Converts a structured `List[AgentMessage]` chat history into a concise narrative summary. Used
internally by memory plugins (`GGUFContextManager`) to compress history
when it exceeds `max_history` turns, keeping the context window manageable.

```python
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole

messages = [
    AgentMessage(MessageRole.USER, "What's the weather?"),
    AgentMessage(MessageRole.ASSISTANT, "It's sunny and 22°C."),
]
summary_text = engine.summarize(messages)

```

Implementations: `GGUFChatSummarizerEngine`.

---

### NLI: `opm.agents.nli`

**Base class:** `NaturalLanguageInferenceEngine`

Predicts whether a *premise* logically entails a *hypothesis*. Used for reasoning chains, intent
conflict detection, and condition evaluation in skills.

```python
print(engine.predict_entailment("It is raining heavily.", "The weather is wet."))  # True
print(engine.predict_entailment("It is sunny.", "You need an umbrella."))           # False

```

Implementations: `GGUFNLIEngine`.

---

### Yes/No Classifier: `opm.agents.yesno`

Classifies a user's ambiguous confirmation as `True` (yes), `False` (no), or `None` (unclear).
Returns `None` on API error.

```python
print(engine.yes_or_no("Do you want me to set a timer?", "sure, go ahead"))  # True
print(engine.yes_or_no("Shall I call John?", "no, not now"))                  # False
print(engine.yes_or_no("Ready?", "what do you mean?"))                        # None

```

Use this in skills when `ask_yesno()` receives uncertain phrasing like "I guess" or "maybe".

Implementations: `GGUFYesNoEngine`.

---

### Option Matcher: `opm.agents.option_matcher`

**Base class:** `OptionMatcherEngine`

Resolves a free-form user reply to one entry in a fixed list of options. This is the engine behind a
skill's `ask_selection()`.

The reference implementation,
[`ovos-option-matcher-fuzzy-plugin`](https://github.com/OpenVoiceOS/ovos-option-matcher-fuzzy-plugin)
(`FuzzyOptionMatcherPlugin`), resolves in this order: fuzzy match via ovos-utils `match_one` (difflib `SequenceMatcher` ratio) when the score
reaches `min_conf` (config key, default `0.65`), then locale-aware "last option" vocab, then
ordinal/cardinal vocab (longest match wins), then a numeric fallback via `ovos-number-parser`.
It returns `None` if nothing matches.

`OVOSSkill.ask_selection()` loads the engine via `skills.ask_selection_plugin` (checked in the
skill's `settings.json` first, then `mycroft.conf`), defaulting to
`ovos-option-matcher-fuzzy-plugin` when neither is set.

---

### Coreference Resolution: `opm.agents.coref`

**Base class:** `CoreferenceEngine`

Resolves pronouns and ambiguous references in voice commands against recent conversation context.
The base class owns the *state* (a per-language context vault). The plugin subclass provides the
*intelligence* (the NLP that rewrites the text). `resolve()` first calls `contains_corefs()` to
skip expensive work when no pronouns are present.

```python

# Stateless one-shot resolution:
result = engine.resolve("Turn it off", lang="en")

# With memory: register context, then resolve future turns against it
engine.set_context("it", "Bohemian Rhapsody", lang="en")
result = engine.resolve("Turn it off", lang="en", use_memory=True)

# "Turn Bohemian Rhapsody off"

```

`use_memory` (default `False`) gates the learn/apply-context steps. Pass `use_memory=True` to
have `resolve()` apply previously registered context and learn new mappings from each turn.
`context_ttl` (config key, default `120` s) controls how long a tracked context entry remains
valid before it is pruned.

Implementations: `GGUFCoreferenceEngine`.

---

### Memory / Context Manager: `opm.agents.memory`

**Base class:** `AgentContextManager`

Manages per-session conversation history. The default implementation (`BasicShortTermMemory`
from `ovos-persona`) stores history in RAM with `max_history` truncation. LLM-powered
implementations (`GGUFContextManager`) also compress old history into a SYSTEM summary message
when the history exceeds a configurable threshold.

```python
from ovos_plugin_manager.templates.agents import AgentContextManager, AgentMessage

# Abstract interface
ctx = manager.build_conversation_context(utterance, session_id)  # List[AgentMessage]
manager.update_history([user_msg, assistant_msg], session_id)

```

Compression config (`GGUFContextManager`):

```json
{
  "<your-memory-plugin>": {
    "system_prompt": "You are a helpful assistant.",
    "max_history": 20,
    "compress": true
  }
}

```

The default no-LLM memory plugin `ovos-agents-short-term-memory-plugin` (`BasicShortTermMemory`)
needs no API key and is always available when `ovos-persona` is installed.

---

### Multimodal Chat: `opm.agents.chat.multimodal`

Extends `ChatEngine` with image input. Images are passed as base64-encoded strings in
`MultimodalAgentMessage.image_content`. Data-URI headers are stripped automatically.

```python
from ovos_plugin_manager.templates.agents import MultimodalAgentMessage, MessageRole

messages = [
    MultimodalAgentMessage(
        role=MessageRole.USER,
        content="What is in this image?",
        image_content=[b64_string],
    )
]
reply = engine.continue_chat(messages)

```

Provided by any installed `opm.agents.chat.multimodal` plugin.

---

## Deprecated Solver Types

The legacy `opm.solver.*` entry points are deprecated and will be removed in the next major
release. Migrate existing plugins to the corresponding `opm.agents.*` types.

| Deprecated entry point | Replacement | Why |
|---|---|---|
| `opm.solver.question` (`QuestionSolver`) | `opm.agents.chat` (`ChatEngine`) | Single-turn Q&A folds into the general chat contract. No separate type is needed. |
| `opm.solver.chat` (`ChatMessageSolver`) | `opm.agents.chat` (`ChatEngine`) | Same engine type as above. The two deprecated solvers converge on one replacement. |
| `opm.solver.summarization` (`TldrSolver`) | `opm.agents.summarizer` (`SummarizerEngine`) | Renamed for clarity. Behavior is otherwise equivalent. |
| `opm.solver.reading_comprehension` (`EvidenceSolver`) | `opm.agents.extractive_qa` (`ExtractiveQAEngine`) | Renamed to match the standard NLP task name (extractive QA over evidence). |
| `opm.solver.multiple_choice` (`MultipleChoiceSolver`) | `opm.agents.reranker` (`ReRankerEngine`) | Choosing among options is really scoring and ranking candidates, so it moved under the reranker contract. |
| `opm.solver.entailment` (`EntailmentSolver`) | `opm.agents.nli` (`NaturalLanguageInferenceEngine`) | Renamed to the standard NLI task name. Entailment is one of NLI's three labels. |
| `opm.coreference` | `opm.agents.coref` | Moved under the unified `opm.agents.*` namespace alongside the other engine types. |

The deprecated classes remain in `ovos_plugin_manager.templates.solvers` and are still loaded
by `PersonaService` and `QuestionSolversService` for backwards compatibility. But no new
plugins should use them.

---

## Plugin catalog

| Plugin | Description |
|--------|-------------|
| [ovos-qdrant-embeddings-plugin](#ovos-qdrant-embeddings-plugin) | The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://qdrant.tech/) database to store, retrieve, and query embeddings. This plugin extends the abstract `EmbeddingsDB` class, using qdrant's capabilities. |
| [ovos-solver-plugin-aiml](#ovos-solver-plugin-aiml) | A rule-based chatbot answer engine for OVOS, using AIML pattern matching. |
| [ovos-persona](#ovos-persona) | The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. With personas, you can customize how queries are handled by assigning specific solvers to each persona. |
| [ovos-openai-plugin](#ovos-openai-plugin) | Uses the [OpenAI Completions API](https://platform.openai.com/docs/api-reference/completions/create) to provide a chat engine, a dialog-rewriting transformer, and a summarizer, all pointed at any OpenAI-compatible endpoint. |
| [ovos-messagebus-chat-plugin](#ovos-messagebus-chat-plugin) | `OVOSMessagebusChatAgent`: a `ChatEngine` (`opm.agents.chat`, entry point `ovos-messagebus`) that proxies each turn through a connected OVOS messagebus pipeline. |
| [ovos-wikipedia-plugin](#ovos-wikipedia-plugin) | Answers factual questions by querying Wikipedia. |
| [ovos-chromadb-embeddings-plugin](#ovos-chromadb-embeddings-plugin) | The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to store, retrieve, and query embeddings. This plugin extends the abstract `EmbeddingsDB` class, using ChromaDB's capabilities. |
| [ovos-wolfram-alpha-plugin](#ovos-wolfram-alpha-plugin) | Answers computational and factual questions via the Wolfram Alpha API. |
| [ovos-ddg-plugin](#ovos-ddg-plugin) | Answers questions using DuckDuckGo instant-answer results. |
| [ovos-solver-YesNo-plugin](#ovos-solver-yesno-plugin) | A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt. |
| [ovos-solver-failure-plugin](#ovos-solver-failure-plugin) | Extreme fallback, just complains it does not have a brain |
| [ovos-gguf-plugin](#ovos-gguf-plugin) | Unified GGUF wrapper for chat, summarization, dialog rewriting, translation, language detection, and text embeddings, all backed by quantized GGUF models via `llama-cpp-python`. |
| [ovos-persona-server](#ovos-persona-server) | Standalone server that exposes an OVOS persona over an HTTP API. |
| [ovos-solver-plugin-rivescript](#ovos-solver-plugin-rivescript) | A rule-based chatbot answer engine for OVOS, using RiveScript pattern matching. |

See [Available ToolBoxes](#available-toolboxes) and [Available Chat Engines](#available-chat-engines)
below for the standalone `opm.agents.toolbox` and `opm.agents.chat` plugin registries.

## ovos-qdrant-embeddings-plugin

- **GitHub**: [OpenVoiceOS/ovos-qdrant-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-qdrant-embeddings-plugin)


- **Description**: The `QdrantEmbeddingsDB` plugin integrates with the [qdrant](https://qdrant.tech/) database to store, retrieve, and query embeddings. This plugin extends the abstract `EmbeddingsDB` class, using qdrant's capabilities.

- **Entry point group**: `opm.embeddings` (the `EmbeddingsDB` backends register here, not under `opm.agents.*`).

- **Config keys**:

| Key | Default | Notes |
|---|---|---|
| `vector_size` | none | **Required.** Dimension of the stored embedding vectors. |
| `distance_metric` | `cosine` | One of `cosine`, `euclidean`, `dot`. |
| `host` | none | When set, connects to a remote Qdrant server (otherwise a persistent local client is used). |
| `port` | `6333` | HTTP port for the remote client. |
| `grpc_port` | `6334` | gRPC port for the remote client. |

---

## ovos-solver-plugin-aiml

- **GitHub**: [OpenVoiceOS/ovos-solver-plugin-aiml](https://github.com/OpenVoiceOS/ovos-solver-plugin-aiml)


- **Description**: A rule-based chatbot answer engine for OVOS, using AIML pattern matching.

- **Config**: `"enable_tx"` (bool, default `false`): auto-translate the utterance to English before matching AIML patterns.

---

## ovos-persona

- **GitHub**: [OpenVoiceOS/ovos-persona](https://github.com/OpenVoiceOS/ovos-persona)


- **Description**: The **`PersonaPipeline`** brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. With personas, you can customize how queries are handled by assigning specific solvers to each persona.

---

## ovos-openai-plugin

- **GitHub**: [OpenVoiceOS/ovos-openai-plugin](https://github.com/OpenVoiceOS/ovos-openai-plugin)


- **Description**: An OpenAI-compatible engine family (chat, dialog-rewriting, and summarization) usable with any OpenAI-compatible endpoint. See [OpenAI Plugin](openai-plugin.md) for the full entry-point table, config keys, and examples.

---

## ovos-messagebus-chat-plugin

- **GitHub**: [OpenVoiceOS/ovos-messagebus-chat-plugin](https://github.com/OpenVoiceOS/ovos-messagebus-chat-plugin)

- **Entry point**: `ovos-messagebus` → `OVOSMessagebusChatAgent` (group `opm.agents.chat`).

- **Description**: A `ChatEngine` that proxies each turn through a connected OVOS messagebus pipeline, letting a persona answer via the full skills/intent stack rather than an LLM.

---

## ovos-wikipedia-plugin

- **GitHub**: [OpenVoiceOS/ovos-wikipedia-plugin](https://github.com/OpenVoiceOS/ovos-wikipedia-plugin)


- **Description**: Answers factual questions by querying Wikipedia.

- **Config**: `"extractive_qa"`: module name of the `ExtractiveQAEngine` plugin used to pull the exact answering passage out of a Wikipedia summary.

---

## ovos-chromadb-embeddings-plugin

- **GitHub**: [OpenVoiceOS/ovos-chromadb-embeddings-plugin](https://github.com/OpenVoiceOS/ovos-chromadb-embeddings-plugin)


- **Description**: The `ChromaEmbeddingsDB` plugin integrates with the [ChromaDB](https://www.trychroma.com/) database to store, retrieve, and query embeddings. This plugin extends the abstract `EmbeddingsDB` class, using ChromaDB's capabilities.

- **Entry point group**: `opm.embeddings` (the `EmbeddingsDB` backends register here, not under `opm.agents.*`).

- **Config keys**:

| Key | Default | Notes |
|---|---|---|
| `path` | `./chromadb_storage` | Storage path for the persistent local client. |
| `host` | none | When set, connects to a remote ChromaDB HTTP server instead of the local persistent client. |
| `port` | `8000` | Port for the remote HTTP client. |

Per-collection metadata defaults `hnsw:space` to `cosine` when not specified.

---

## ovos-wolfram-alpha-plugin

- **GitHub**: [OpenVoiceOS/ovos-wolfram-alpha-plugin](https://github.com/OpenVoiceOS/ovos-wolfram-alpha-plugin)


- **Description**: Answers computational and factual questions via the Wolfram Alpha API.

- **Config**: `"appid"`: your own Wolfram Alpha AppID. Without one, queries go to Wolfram's
  servers on a shared demo key. Either way this solver is a call to a third-party cloud
  service. It has no offline mode.

---

## ovos-ddg-plugin

- **GitHub**: [OpenVoiceOS/ovos-ddg-plugin](https://github.com/OpenVoiceOS/ovos-ddg-plugin)


- **Description**: Answers questions using DuckDuckGo instant-answer results.

- **Config**: `"keyword_extractor"`: module name of the keyword-extraction plugin used to pull search terms out of the question (defaults to `ovos-rake-keyword-extractor`).

---

## ovos-solver-YesNo-plugin

- **GitHub**: [OpenVoiceOS/ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin)


- **Description**: A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt.

- **Config**: no config keys. It works out of the box with no settings to tune.

---

## ovos-solver-failure-plugin

- **GitHub**: [OpenVoiceOS/ovos-solver-failure-plugin](https://github.com/OpenVoiceOS/ovos-solver-failure-plugin)


- **Description**: Extreme fallback, just complains it does not have a brain

- **Config**: no config keys. It works out of the box with no settings to tune.

---

## ovos-gguf-plugin

- **GitHub**: [OpenVoiceOS/ovos-gguf-plugin](https://github.com/OpenVoiceOS/ovos-gguf-plugin)


- **Description**: A unified GGUF wrapper providing chat, summarization, dialog rewriting, translation, language detection, and text-embedding engines, all backed by quantized GGUF models loaded through `llama-cpp-python`. See [GGUF Plugin](gguf-plugin.md) for the full entry-point table.

---

## ovos-persona-server

- **GitHub**: [OpenVoiceOS/ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)


- **Description**: Standalone server that exposes an OVOS persona over an HTTP API (e.g. `ovos-persona-server --persona rivescript_bot.json`).

---

## ovos-solver-plugin-rivescript

- **GitHub**: [OpenVoiceOS/ovos-solver-plugin-rivescript](https://github.com/OpenVoiceOS/ovos-solver-plugin-rivescript)


- **Description**: A rule-based chatbot answer engine for OVOS, using RiveScript pattern matching.

- **Config**: `"lang"`: language code used to pick the bundled RiveScript brain (defaults to `en-us`).

---

## Available ToolBoxes

These `opm.agents.toolbox` plugins each wrap one external service as a set of callable
`AgentTool` functions. Call them directly with `ToolBox.call_tool(name, kwargs)`, or over the
bus via `ovos.persona.tools.{toolbox_id}.call`. See [Tool Plugins](tool-plugins.md) for the
`ToolBox` API itself.

| Plugin ID | Tools | Package | API key |
|---|---|---|---|
| `ovos-wikipedia-tools` | `search_wikipedia`, `get_wikipedia_sections`, `get_wikipedia_page` | `ovos-wikipedia-plugin` | None, public Wikipedia REST API |
| `ovos-ddg-tools` | `search_duckduckgo`, `get_duckduckgo_infobox` | `ovos-ddg-plugin` | None, DuckDuckGo Instant Answer API |
| `ovos-wolfram-alpha-tools` | `compute`, `compute_full` | `ovos-wolfram-alpha-plugin` | Optional, free key at developer.wolframalpha.com; a demo key ships in the plugin |
| `ovos-weather-tools` | `get_current_weather`, `get_daily_forecast`, `get_hourly_forecast` | `ovos-skill-weather` | None, Open-Meteo public API |
| `ovos-datetime-tools` | `get_current_datetime`, `convert_timezone`, `get_timezone_for_location` | `ovos-skill-date-time` | None, stdlib + pytz |
| `ovos-ip-tools` | `get_local_ip_addresses`, `get_public_ip` | `ovos-skill-ip` | None |
| `ovos-iss-tools` | `get_iss_position`, `get_iss_crew` | `ovos-skill-iss-location` | Optional, geonames.org user for reverse geocoding |
| `ovos-speedtest-tools` | `run_speedtest` | `ovos-skill-speedtest` | None, Speedtest.net |
| `ovos-wallpapers-tools` | `search_wallpapers` | `ovos-skill-wallpapers` | None, wallhaven.cc public API |
| `ovos-wikihow-tools` | `search_wikihow`, `get_wikihow_steps` | `ovos-skill-wikihow` | None, pywikihow scraper |
| `ovos-wordnet-tools` | `lookup_word`, `define_word` | `ovos-skill-wordnet` | None, local NLTK corpus |

The [agentic loop](agentic-loop.md) bundles its own toolboxes (`ovos-filesystem-tools`,
`ovos-shell-tools`, `ovos-web-search-tools`, `ovos-clock-tools`, `ovos-skill-md-toolbox`) —
see that page for those.

## Available Chat Engines

`opm.agents.chat` plugins beyond the ones documented above as their own catalog entries
(`ovos-openai-plugin`, `ovos-gguf-plugin`) are not currently shipped by an OpenVoiceOS-org
repository. This manual only documents plugins backed by an OpenVoiceOS-org repo.

---
