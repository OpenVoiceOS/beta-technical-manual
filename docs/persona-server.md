# OVOS Persona Server

!!! abstract "In a nutshell"
    A "persona" is an OVOS chat character, a configured AI personality that answers questions. This server puts a persona online and makes it *look and behave like* the well-known AI chat services (such as OpenAI, Ollama, or Anthropic Claude). The practical upshot: any app or tool that already knows how to talk to one of those services can be pointed at your persona instead, with no changes. This is handy for plugging an OVOS persona into other software (like Home Assistant). Note it has no built-in password protection, so keep it on a trusted network. See [OVOS Personas](personas.md) and the [Glossary](glossary.md).

The OVOS Persona Server exposes any OVOS [persona](personas.md) over HTTP using the APIs of
major LLM vendors, so an OVOS persona becomes a drop-in replacement for an LLM backend in
third-party tools. The running server mounts **OpenAI-** and **Ollama-compatible** chat
endpoints, a UTCP tool surface, and vendor-compatible routers for **Anthropic**, **Gemini**,
**Cohere**, **AWS Bedrock**, and **HuggingFace TGI** (plus MCP, if installed).

It is a FastAPI app served by `uvicorn`. The server loads a persona from a JSON file at startup. The persona's `handlers` do the actual work (anything from a local rule-based bot to a remote LLM).

---

## Install

```bash
pip install ovos-persona-server
```

Install the agent-engine plugin(s) your persona references, e.g.:

```bash
pip install ovos-openai-plugin
```

Optional extras: `rag` (file/vector-store endpoints), `mcp` (pulls in `fastmcp>=3,<4` to
serve the `/mcp` endpoint below), and `a2a` (Agent-to-Agent endpoint), e.g.
`pip install 'ovos-persona-server[a2a]'`.

!!! note "The `mcp` extra installs `fastmcp`, not the `mcp` SDK"
    The extra is still called `mcp`, so `pip install 'ovos-persona-server[mcp]'` is unchanged,
    but it resolves the third-party `fastmcp` package (`fastmcp>=3,<4`), not the official `mcp`
    SDK. The split is deliberate: this server *serves* MCP with `fastmcp`, while a client
    consuming another MCP server (like [`ovos-mcp-toolbox`](tool-plugins.md)) uses the official
    `mcp` SDK instead. The two packages diverged because MCP SDK 2.0 removed
    `mcp.server.fastmcp.FastMCP`, so a server still importing that symbol fails to start on the
    2.x SDK; `fastmcp` is the maintained standalone project that symbol used to alias.

---

## Run

```bash
ovos-persona-server --persona my_persona.json --host 0.0.0.0 --port 8337
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--persona` | `None` | Path to a single persona `.json` file to load |
| `--personas-dir` | `None` | Directory whose `*.json` files are all loaded as personas, one process serving all of them |
| `--default-persona` | `None` | Name of the persona that answers requests which do not select one; only meaningful with `--personas-dir` |
| `--host` | `0.0.0.0` | Host to bind |
| `--port` | `8337` | TCP port |
| `--a2a-base-url` | `None` | Mounts an [A2A](https://a2aproject.github.io/A2A/)-compatible endpoint at `/a2a`, using this URL as the public base URL in the Agent Card (e.g. `http://myhost:8337/a2a`). Requires the `a2a` extra (`pip install 'ovos-persona-server[a2a]'`) |

The console script is `ovos-persona-server` (module `ovos_persona_server.__main__:main`).

### Serving multiple personas from one process

```bash
ovos-persona-server --personas-dir /etc/ovos/personas --default-persona assistant --host 0.0.0.0 --port 8337
```

Every `*.json` file in the directory loads as its own persona, keyed by its `name`. A client
selects which one to talk to with the `model` field; a request that omits it falls back to
`--default-persona` (or the first persona loaded, if that flag is unset). Serving more than one
persona is what makes `model` authoritative: a name that matches none of them is rejected with a
404, not silently redirected. Both `/v1/models` (OpenAI-compatible) and `/api/tags`
(Ollama-compatible) enumerate the loaded personas, so a client can discover the available names
before picking one.

The directory must yield at least one persona: startup fails fast with a `ValueError` rather
than serving nothing — `--personas-dir is not a directory` when the path is missing, `no *.json
persona files found` when it exists but is empty. Worth knowing before mounting a
not-yet-populated volume into a container.

---

## The Persona File

A persona is a JSON object whose `handlers` list names the plugins that answer queries. Per-plugin config is keyed by the plugin name. Example pointing at an OpenAI-compatible LLM:

```json
{
  "name": "kb-assistant",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "https://llama.smartgic.io/v1",
    "model": "llama3.1:8b",
    "key": "sk-xxx"
  }
}
```

Solvers are tried in order. The first that returns an answer wins. Some solvers are **not** LLMs and keep no chat history. In that case only the last user message is processed.

---

## HTTP API Endpoints

| Endpoint | Method | Compatible with |
|----------|--------|-----------------|
| `/openai/v1/chat/completions` | POST | OpenAI chat (streaming + tool calls) |
| `/openai/v1/completions` | POST | OpenAI legacy completions |
| `/openai/v1/models` | GET | OpenAI model listing |
| `/openai/v1/embeddings` | POST | OpenAI embeddings |
| `/ollama/api/chat` | POST | Ollama chat |
| `/ollama/api/generate` | POST | Ollama generate |
| `/ollama/api/tags` | GET | Ollama model listing |
| `/ollama/api/show` | POST | Ollama model details |
| `/ollama/api/ps` | GET | Ollama running-model listing (stub) |
| `/ollama/api/pull`, `/ollama/api/push` | POST | Ollama pull/push (stubs; there is nothing to pull or push) |
| `/ollama/api/embed`, `/ollama/api/embeddings` | POST | Ollama embeddings |
| `/anthropic/v1/...` | POST/GET | Anthropic-compatible messages API |
| `/gemini/v1beta/models/...` | POST/GET | Gemini-compatible API |
| `/cohere/v1/...` | POST/GET | Cohere-compatible API |
| `/bedrock/model/...` | POST/GET | AWS Bedrock-compatible API |
| `/tgi/...` | POST/GET | HuggingFace TGI-compatible API |
| `/tools/manual` | GET | UTCP tool-discovery manual |
| `/tools/{name}` | POST | UTCP tool invocation |
| `/mcp` | * | MCP streamable-HTTP transport (mounted when the `mcp` extra is installed) |
| `/a2a` | * | A2A agent endpoint (mounted when `--a2a-base-url` is set and the `a2a` extra is installed) |
| `/openai/v1/files` | POST/GET/DELETE | OpenAI **Files** API (`{id}`, `{id}/content`) — mounted when the `rag` extra is installed |
| `/openai/v1/vector_stores` | POST/GET/DELETE | OpenAI **Vector Stores** API (`{id}`, `{id}/files`, `{id}/search`) — mounted when the `rag` extra is installed |

The legacy unprefixed paths `/v1/...` and `/api/...` (OpenAI and Ollama respectively) remain
mounted as deprecated aliases of `/openai/v1/...` and `/ollama/api/...`. Responses on these
legacy paths carry `Deprecation` and `Link` headers pointing at the canonical path.

There is no authentication. Put the server behind a reverse proxy if it is exposed.

Every vendor router accepts the usual auth header for that vendor, but silently ignores it: an invalid or missing key does not get rejected with a 401, it is simply not checked. Every router also accepts a `model` field in the request body but ignores its value: the loaded persona's own `name` is always the model identifier returned in the response, regardless of what the client asked for.

| Vendor | Auth header accepted (and ignored) | `model` field quirk | What to do |
|---|---|---|---|
| OpenAI, Ollama, Anthropic, Gemini, Cohere, HuggingFace TGI | `Authorization`, `x-api-key`, or `?key=` query param | Ignored; response always reports the persona's own `name` | Send any value, or omit it; it has no effect |
| AWS Bedrock | `Authorization`, `x-api-key`, or `?key=` query param | Ignored for identity; the `model_id` prefix (`anthropic.claude`, `meta.llama`, `amazon.titan`, `cohere.command`) also selects the request/response wire shape, so the endpoint speaks a different format depending on that string | Set `model_id` to match the wire format your client expects, even though the persona still answers |

### Memory, RAG & embeddings

By default the server is a **stateless passthrough**. The client owns conversation
state. Two modes are selected by the `CHAT_MEMORY` environment variable:

- `off` (default): *backend* mode, stateless. The client drives the Files /
  Vector-Stores endpoints itself. Use this for multi-user / drop-in-OpenAI
  deployments (a shared server memory would leak across users).
- `transparent`: single-user *hosted agent* mode. The server keys history by
  session (the OpenAI `user` field, else a default session) and folds the persona's
  `memory_module` into every turn.

The embeddings endpoints and vector-store search share one embeddings backend,
configured via environment variables:

| Env var | Default | Purpose |
|---|---|---|
| `TEXT_EMBEDDINGS_PLUGIN` | `ovos-gguf-embeddings-plugin` | Text-embeddings plugin |
| `EMBEDDINGS_DB_PLUGIN` | `ovos-chromadb-embeddings-plugin` | Vector store backend |
| `EMBEDDINGS_MODEL` / `EMBEDDINGS_URL` / `EMBEDDINGS_KEY` | unset | Model + remote embeddings endpoint/key |
| `FILE_STORAGE_PATH` | `~/.cache/ovos-persona-server/files` | Where uploaded files are stored |
| `FILE_STORAGE_STRATEGY` | `disk` | `disk`, `database`, or `both` |

| Endpoint | Vendor | Detection | If no handler supports it |
|---|---|---|---|
| `/openai/v1/embeddings` | OpenAI | Server scans the persona's loaded handlers for the first one that implements `get_embeddings()` | Returns `501` with `{"detail": "No embeddings solver configured for this persona."}` |
| `/ollama/api/embed`, `/ollama/api/embeddings` | Ollama | Same detection mechanism, shared with the other two endpoints | Same `501` response |
| `/cohere/v1/embed` | Cohere | Same detection mechanism, shared with the other two endpoints | Same `501` response |

---

## Streaming

Set `stream=true` (where the vendor API supports it) to get incremental output. Each router speaks the wire format its vendor expects:

| Vendor | Format |
|---|---|
| OpenAI | SSE, terminated by `data: [DONE]` |
| Ollama | newline-delimited JSON (NDJSON) |
| Anthropic | SSE with named events (`message_start`, `content_block_delta`, ...) |
| Gemini | SSE of full-response objects |
| Cohere | NDJSON with an `event_type` field per line |
| HuggingFace TGI | SSE token events |
| AWS Bedrock | SSE with `outputText` events |

Tool calling is only supported with `stream=false`, regardless of vendor.

---

## Function Calling: Who Executes What

A chat request can carry two independent kinds of tools, and they are executed by different
sides of the connection:

- **Client-side tools** arrive in the request's OpenAI-shaped `tools` field. The server never
  runs these: it relays the model's `tool_calls` back with `finish_reason: "tool_calls"`, and the
  caller is expected to execute the call itself and reply with a `role: "tool"` message on the
  next turn — the normal OpenAI function-calling contract.
- **Server-side tools** are the persona's own [`ToolBox` plugins](tool-plugins.md). The server
  executes these itself, in a bounded agentic loop: when the model calls one, the server runs it,
  appends the result as a `role: "tool"` message, and re-invokes the engine, up to
  `MAX_TOOL_ITERS` (5) rounds before it gives up and returns whatever the last response was.
  `tool_calls` for a server-side tool never reach the client — the client was never offered that
  tool, so it could not run it anyway.

Both kinds can appear in the same request; the server merges client-supplied specs with the
persona's own tool specs before offering them to the model.

!!! warning "A name collision is decided in the persona's favor"
    Nothing deduplicates the merged tool list by name. If a client sends a tool whose name
    matches one of the persona's `ToolBox` tools — a generic name like `search` is enough — the
    persona's tool wins: only one copy of that name is offered to the model, and a call to it
    always runs server-side, even though the client believes it owns that tool. The model never
    sees a duplicate name, but the client also never gets a `tool_calls` response it can act on
    for that name. Give tools specific names to avoid this.

---

## OpenAI-Compatible Example

Point the `openai` SDK at the `/openai/v1` path:

```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",                       # no key required for local use
    base_url="http://localhost:8337/openai/v1",
)

resp = client.chat.completions.create(
    model="",                                    # ignored; the persona decides
    messages=[{"role": "user", "content": "tell me a joke"}],
)
print(resp.choices[0].message.content)
```

!!! tip "Verify it worked"
    A working call prints a punchline-shaped string, e.g.:

    ```text
    Why don't scientists trust atoms? Because they make up everything!
    ```

    If instead you get a connection error, double-check the server is actually running on that
    host/port (`ovos-persona-server --persona ... --port 8337`) and that the URL includes the
    `/openai/v1` prefix. An empty or error-shaped `content` usually means the persona's `handlers`
    failed to answer. Check the server logs and the handler's own config (API key, model name).

---

## Ollama-Compatible Use

The Ollama surface (`/ollama/api/chat`, `/ollama/api/generate`, `/ollama/api/tags`) lets Ollama
clients treat the persona as a local model. For example, the
[Home Assistant Ollama integration](https://www.home-assistant.io/integrations/ollama/) can
connect directly and use the persona as its LLM backend. `/ollama/api/tags` reports the model
name(s) from the persona's solver config.

---

## Tips

- **Mind the prefix.** Clients must hit `/openai/v1` (OpenAI) or `/ollama/api` (Ollama), not the
  bare host root. Pointing a client at `http://localhost:8337` alone will 404. The legacy
  `/v1` and `/api` aliases still work but are deprecated. Tool calling is only supported with
  `stream=false`.

- Make sure your persona file's `handlers` and their config are complete. A missing plugin or model means the persona cannot answer.

- Capabilities (chat history, tool use, embeddings) depend entirely on the chosen solver plugins, so behavior varies by persona.

- For production, secure the endpoint (reverse proxy, rate limits). The server itself is unauthenticated.

!!! tip "Why remote MCP only became practical recently"
    The official `mcp` SDK's `FastMCP` (1.x) enforces DNS-rebinding protection by default: it
    only accepts a `Host` header of `127.0.0.1` or `localhost`, so a mounted MCP endpoint answers
    normally on the loopback address and **421 Misdirected Request** through any other domain
    name — no reverse-proxy configuration works around it, because the check runs before the
    proxy's headers are trusted. `fastmcp`, the package this server actually serves MCP with,
    does not impose that restriction, which is why proxying `/mcp` to a real hostname works here.

---

*Source code: [OpenVoiceOS/ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server).*

---
**Read next:** [Agent Engine Types](agent-plugins.md)
**Related:** [Personas & PersonaService](personas.md) · [Persona Memory](persona-memory.md) · [Remote Agents with HiveMind](hivemind-agents.md)
