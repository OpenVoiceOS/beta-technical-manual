# Give a Persona MCP and UTCP Tools (Agentic Loop and Tool Adapters)

This page gives an OVOS persona tools from an MCP server or a UTCP manual, so that its language model can call them while it answers.

## Who this is for

You build an OVOS persona with a language model. You want the persona to use tools that another server offers, such as the [translate server](ai-agent-translate.md) or any third-party MCP server.

## What you get

- `ovos-agentic-loop` runs the reasoning loop. Its `brain` is the language model, and its `toolboxes` are the tools.
- `ovos-tool-adapters` turns a server into a toolbox: `ovos-mcp-toolbox` for an MCP server, and `ovos-utcp-toolbox` for a UTCP manual.

## Before you start

You need:

- A language model with an OpenAI-compatible API that can call tools. A small local model is enough. For example, `llama-server -m Qwen3-0.6B-Q4_K_M.gguf --jinja --port 8081` from [llama.cpp](https://github.com/ggml-org/llama.cpp) serves one at `http://localhost:8081/v1`.
- A tool server. This page uses the translate server from [Translate text from an AI agent](ai-agent-translate.md), started with `--mcp` on port `9686`.

!!! warning "Alpha channel only"
    The loop and the adapters install from the prerelease channel:

    ```bash
    pip install --pre "ovos-persona-server>=0.18.6a1" "ovos-agentic-loop>=0.2.4a1" "ovos-tool-adapters[mcp,utcp]>=0.1.9a1" ovos-openai-plugin
    ```

## Use tools from an MCP server

1. Write the persona file `translator.json`. The settings of each toolbox go **inside** the section of the loop, beside `toolboxes`:

    ```json
    {
      "name": "translator",
      "description": "Answers with tools from the OVOS translate server",
      "handlers": ["ovos-native-toolcall-loop"],
      "ovos-native-toolcall-loop": {
        "brain": "ovos-chat-openai-plugin",
        "ovos-chat-openai-plugin": {
          "api_url": "http://localhost:8081/v1",
          "model": "qwen3-0.6b"
        },
        "toolboxes": ["ovos-mcp-toolbox"],
        "ovos-mcp-toolbox": {
          "transport": "http",
          "url": "http://localhost:9686/mcp",
          "timeout": 30
        }
      }
    }
    ```

2. Serve the persona:

    ```bash
    ovos-persona-server --persona translator.json
    ```

3. Ask a question through the OpenAI-compatible API of the persona server:

    ```bash
    curl -s http://localhost:8337/openai/v1/chat/completions -H 'Content-Type: application/json' \
      -d '{"model": "translator", "messages": [{"role": "user", "content": "Translate \"the kitchen light is on\" into German."}]}'
    ```

    The `content` of the answer:

    ```text
    The translated sentence in German is: **"Das Küchenlicht ist an"**.
    ```

    While the persona answered, the translate server logged the tool call:

    ```text
    "POST /mcp HTTP/1.1" 200 OK
    ```

## Use tools from a UTCP manual

Replace the toolbox in the loop section. `ovos-utcp-toolbox` lists each manual in `manual_call_templates`:

```json
{
  "name": "translator-utcp",
  "description": "Answers with tools from a UTCP manual",
  "handlers": ["ovos-native-toolcall-loop"],
  "ovos-native-toolcall-loop": {
    "brain": "ovos-chat-openai-plugin",
    "ovos-chat-openai-plugin": {
      "api_url": "http://localhost:8081/v1",
      "model": "qwen3-0.6b"
    },
    "toolboxes": ["ovos-utcp-toolbox"],
    "ovos-utcp-toolbox": {
      "utcp_config": {
        "manual_call_templates": [{
          "name": "ovos_translate",
          "call_template_type": "http",
          "url": "http://localhost:9686/utcp",
          "http_method": "GET"
        }]
      },
      "timeout": 30
    }
  }
}
```

The question "Translate "good night" into Portuguese." got this answer:

```text
The translated text in Portuguese is: "boa noite".
```

The translate server logged the call that the UTCP tool made:

```text
"GET /translate/auto/pt/good%20night HTTP/1.1" 200 OK
```

## Choose the transport of an MCP server

| Transport | Settings |
|---|---|
| Streamable HTTP | `"transport": "http", "url": "http://..."` |
| SSE | `"transport": "sse", "url": "http://..."` |
| A local command (stdio) | `"transport": "stdio", "command": "uvx", "args": ["mcp-server-fetch"]`, and an optional `"env": {...}` |

Each adapter also takes `timeout` (seconds for each call, default `30`) and `toolbox_id`. Give two adapters of the same type different `toolbox_id` values to use two servers.

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `MCPToolBox: failed to connect to MCP server: 'command'` in the log | The toolbox settings are at the top level of the persona, so the loop gives the adapter an empty config | Move the `ovos-mcp-toolbox` section into the section of the loop. |
| The answer comes but the tool server logs no call | The model answered from its own knowledge, or it cannot call tools | Use a model that supports tool calls. Start `llama-server` with `--jinja`. |
| A `tool_providers` config loads no tools | `tool_providers` is the key of UTCP before 1.0 | Use `manual_call_templates`. |
| The UTCP adapter registers no tools for `http` | `utcp-http` is not installed | Install `ovos-tool-adapters[utcp]`, which installs `utcp-http`. |

## More information

- [Toolboxes](https://github.com/OpenVoiceOS/ovos-agentic-loop/blob/dev/docs/toolboxes.md) in the `ovos-agentic-loop` docs.
- [MCP](https://github.com/OpenVoiceOS/ovos-tool-adapters/blob/dev/docs/mcp.md) and [UTCP](https://github.com/OpenVoiceOS/ovos-tool-adapters/blob/dev/docs/utcp.md) in the `ovos-tool-adapters` docs.
- [Agentic Loops](agentic-loop.md) for the reasoning loops.

---
**Read next:** [Answer through a remote A2A agent](ai-agent-a2a-solver.md)
**Related:** [AI Agents](ai-agents.md) · [Translate text from an AI agent](ai-agent-translate.md) · [Write a tool plugin](ai-agent-tool-plugin.md)
