# Agent Plugins Reference

!!! abstract "In a nutshell"
    This page holds the full technical entry for each agent plugin in the catalog: repository
    link, description, entry-point group where it differs from the obvious one, and config keys.
    Start at [Agent Plugins](agent-plugins.md) to pick a plugin, come here for the exact settings.

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


- **Description**: The persona pipeline (the **`PersonaService`** class) brings multi-persona management to OpenVoiceOS (OVOS), enabling interactive conversations with virtual assistants. With personas, you can customize how queries are handled by assigning specific solvers to each persona.

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

## ovos-wordnet-plugin

- **GitHub**: [OpenVoiceOS/ovos-wordnet-plugin](https://github.com/OpenVoiceOS/ovos-wordnet-plugin)


- **Description**: Answers word-knowledge questions from the local WordNet corpus. Registers a `RetrievalEngine` (`opm.agents.retrieval`, entry point `ovos-wordnet-plugin`) that matches locale intent patterns such as "what are the antonyms of dog?" and falls back to multi-sense definition passages for bare word lookups, plus the `ovos-wordnet-tools` toolbox (`define_word`, `word_relations`) documented on [Tool Plugins](tool-plugins.md#available-toolboxes).

---

## ovos-solver-YesNo-plugin

- **GitHub**: [OpenVoiceOS/ovos-solver-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-solver-YesNo-plugin)


- **Description**: A simple tool to indicate whether a user answered "yes" or "no" to a yes/no prompt.

- **Config**: no config keys. It works out of the box with no settings to tune.

!!! note "Deprecated"
    Superseded by [ovos-YesNo-plugin](https://github.com/OpenVoiceOS/ovos-YesNo-plugin)
    (needs `ovos-plugin-manager>=2.4.0`). See [Deprecated Repos](deprecated-repos.md).

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

The standalone `opm.agents.toolbox` and `opm.agents.chat` plugin registries, including the
full list of available ToolBoxes and chat engines, are on
[Tool Plugins: Available ToolBoxes](tool-plugins.md#available-toolboxes) and
[Tool Plugins: Available Chat Engines](tool-plugins.md#available-chat-engines).

---
**Read next:** [Agent Plugins](agent-plugins.md)
**Related:** [Building Agent Plugins](building-agent-plugins.md) · [Personas & PersonaService](personas.md) · [Agent Tool Plugins](tool-plugins.md)
