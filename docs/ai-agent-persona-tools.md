# Use Persona Tools from an AI Agent (MCP and UTCP)

This page serves every installed OVOS tool plugin to AI agents, through the MCP and UTCP endpoints of the persona server.

## Who this is for

You have OVOS tool plugins, your own or the ones that OVOS ships. You want Claude Code, Claude Desktop, opencode, Mistral Vibe, or another agent to call them.

## What you get

- An MCP endpoint at `http://localhost:8337/mcp`, with one MCP tool for each tool of each installed toolbox.
- A UTCP manual at `http://localhost:8337/utcp` (also at `/tools/manual`), and one HTTP endpoint for each tool at `POST /tools/<name>`.
- A stdio MCP server, `ovos-persona-tools-mcp`, for MCP clients that start a local command.

## Start the server

!!! warning "Alpha channel only"
    The `mcp` extra is only in the prerelease channel. Install the server
    from that channel:

    ```bash
    pip install --pre "ovos-persona-server[mcp]" ovos-solver-rivescript-plugin
    ```

1. Install the tool plugins in the same environment. This page uses `my-math-tools` from [Write a tool plugin](ai-agent-tool-plugin.md):

    ```bash
    pip install -e ./my-math-tools
    ```

2. Start the server with the `--mcp` flag. Use the `helper.json` persona from [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md):

    ```bash
    ovos-persona-server --persona helper.json --mcp
    ```

## Call the tools from Claude Code

1. Add the server to Claude Code:

    ```bash
    claude mcp add --transport http ovos-persona http://localhost:8337/mcp
    ```

2. Make sure that Claude Code can connect:

    ```bash
    claude mcp list
    ```

    ```text
    ovos-persona: http://localhost:8337/mcp (HTTP) - ✔ Connected
    ```

## Call the tools from Claude Desktop

Claude Desktop can start the stdio server directly. `PERSONA_PATH` names the persona file that holds the toolbox settings. Use absolute paths:

```json
{
  "mcpServers": {
    "ovos-persona": {
      "command": "/home/me/venvs/ovos/bin/ovos-persona-tools-mcp",
      "env": {"PERSONA_PATH": "/home/me/helper.json"}
    }
  }
}
```

An MCP client that started this command found one tool, `add`. The call `add(a=2, b=3)` returned:

```json
{"sum": 5.0}
```

## Call the tools from opencode

1. Add the server to `opencode.json` in your project folder:

    ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "mcp": {
        "ovos-persona": {
          "type": "remote",
          "url": "http://localhost:8337/mcp",
          "enabled": true
        }
      }
    }
    ```

2. Make sure that opencode can connect:

    ```bash
    opencode mcp list
    ```

    ```text
    ●  ✓ ovos-persona connected
    │      http://localhost:8337/mcp
    ```

opencode can also start the stdio server directly, with no running persona server. Use a `local` entry with absolute paths:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "ovos-persona": {
      "type": "local",
      "command": ["/home/me/venvs/ovos/bin/ovos-persona-tools-mcp"],
      "environment": {"PERSONA_PATH": "/home/me/helper.json"},
      "enabled": true
    }
  }
}
```

## Call the tools from Mistral Vibe

1. Add the server to `~/.vibe/config.toml`:

    ```toml
    [[mcp_servers]]
    name = "ovos-persona"
    transport = "streamable-http"
    url = "http://localhost:8337/mcp"
    ```

    Write the entry in the file. Do not use `vibe mcp add` for this server: that command sets OAuth login for an HTTP server, and the OVOS server does not use OAuth.

2. Start `vibe`. Vibe loads the tools of the server when it starts. It gives each tool the server name as a prefix and changes each hyphen to `_`, for example `ovos_persona_add`.

Vibe can also start the stdio server directly, with no running persona server. Use a `stdio` entry with absolute paths:

```toml
[[mcp_servers]]
name = "ovos-persona"
transport = "stdio"
command = "/home/me/venvs/ovos/bin/ovos-persona-tools-mcp"
env = { PERSONA_PATH = "/home/me/helper.json" }
```

## Call the tools from your own MCP client

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://localhost:8337/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print([t.name for t in (await session.list_tools()).tools])
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print(result.content[0].text)

asyncio.run(main())
```

```text
['search_wikipedia', 'get_current_datetime', 'read_file', 'write_file', 'list_directory', 'search_in_files', 'find_files', 'evaluate_expression', 'unit_convert', 'statistics_summary', 'solve_equation', 'run_command', 'fastapi', 'web_search', 'add']
{"sum": 5.0}
```

The list holds the tools of every toolbox in the environment. In this run, `ovos-agentic-loop` and `ovos-wikipedia-plugin` were installed beside `my-math-tools`.

## Call the tools from a UTCP agent

Each tool takes its arguments as one JSON object in `body`:

```python
import asyncio
from utcp.utcp_client import UtcpClient

async def main():
    client = await UtcpClient.create(config={"manual_call_templates": [{
        "name": "ovos_persona", "call_template_type": "http",
        "url": "http://localhost:8337/utcp", "http_method": "GET"}]})
    print(await client.call_tool("ovos_persona.add", {"body": {"a": 2, "b": 3}}))

asyncio.run(main())
```

```text
{'sum': 5.0}
```

With plain HTTP, send the same object:

```bash
curl -s -X POST http://localhost:8337/tools/add -H 'Content-Type: application/json' -d '{"a": 2, "b": 3}'
```

## Configure a toolbox

The server gives each toolbox the section with its name from the default persona file. For example, this persona gives `ovos-mcp-toolbox` its settings:

```json
{
  "name": "helper",
  "handlers": ["ovos-solver-rivescript-plugin"],
  "ovos-mcp-toolbox": {"transport": "http", "url": "http://localhost:9686/mcp"}
}
```

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `/mcp` returns `404` | The server started without `--mcp`, or the `mcp` extra is not installed | Install the `mcp` extra. Start the server with `--mcp`. |
| A tool that you installed is not in the list | The package is in a different environment | Install the package in the environment of the server. Restart the server. |
| The log shows `MCPToolBox: failed to connect to MCP server: 'command'` | `ovos-mcp-toolbox` is installed but has no settings | Add an `ovos-mcp-toolbox` section to the persona, or ignore the warning. |

!!! danger "The server publishes every installed toolbox"
    The server serves the tools of every toolbox in its environment, with no authentication. `ovos-agentic-loop` adds file and shell tools. In a default install, `run_command` answers `Shell execution is disabled (allow_shell=False)`, and `read_file` refuses paths outside its sandbox root. Install only the toolboxes that you want to publish, and bind the server to a trusted network.

## More information

- [API surfaces](https://github.com/OpenVoiceOS/ovos-persona-server#api-surfaces) in the `ovos-persona-server` README.
- [Persona Server](persona-server.md) and [Agent Tool Plugins](tool-plugins.md).

---
**Read next:** [Share tools on the messagebus](ai-agent-bus-tools.md)
**Related:** [AI Agents](ai-agents.md) · [Write a tool plugin](ai-agent-tool-plugin.md) · [Give a persona MCP and UTCP tools](ai-agent-persona-uses-tools.md)
