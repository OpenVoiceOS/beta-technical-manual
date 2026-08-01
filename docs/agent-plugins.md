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
`ovos_plugin_manager.templates.solvers`) are deprecated. See [Specialized Agent Engine
Types](advanced-solvers.md) for the migration map. For per-engine method contracts and config
examples, see [Agents & Personas](personas.md) and [Advanced Solvers](advanced-solvers.md).

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
