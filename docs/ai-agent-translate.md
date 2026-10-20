# Translate Text From an AI Agent (MCP and UTCP)

This page connects an AI agent to the OVOS translate server, so the agent can translate text and detect its language.

## Who this is for

You use Claude Code, Claude Desktop, or your own MCP or UTCP agent. You want translation that goes through a translation plugin that you choose.

## What you get

- The MCP tools `translate` and `detect_language` at `http://localhost:9686/mcp`.
- A UTCP manual at `http://localhost:9686/utcp` with five tools: `translate`, `translate_with_source`, `detect_language`, `classify_language` and `supported_languages`.

## Start the server

!!! warning "Alpha channel only"
    The `mcp` extra has a prerelease floor, so the server installs from the
    prerelease channel:

    ```bash
    pip install --pre "ovos-translate-server[mcp]>=0.11.3a3" ovos-google-translate-plugin
    ```

1. Start the server with a translation plugin, a language detection plugin and the `--mcp` flag:

    ```bash
    ovos-translate-server --tx-engine ovos-google-translate-plugin --detect-engine ovos-google-lang-detector-plugin --mcp
    ```

The `ovos-google-translate-plugin` package also installs the `ovos-google-lang-detector-plugin` detector. Both send the text to Google.

## Translate from Claude Code

1. Add the server to Claude Code:

    ```bash
    claude mcp add --transport http ovos-translate http://localhost:9686/mcp
    ```

2. Make sure that Claude Code can connect:

    ```bash
    claude mcp list
    ```

    ```text
    ovos-translate: http://localhost:9686/mcp (HTTP) - ✔ Connected
    ```

## Translate from Claude Desktop

Add the `mcp-remote` bridge to `claude_desktop_config.json`, then restart Claude Desktop. The bridge needs Node.js.

```json
{
  "mcpServers": {
    "ovos-translate": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:9686/mcp"]
    }
  }
}
```

## Translate from your own MCP client

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://localhost:9686/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print([t.name for t in (await session.list_tools()).tools])
            result = await session.call_tool("translate", {"text": "good morning", "target_lang": "pt"})
            print(result.content[0].text)
            result = await session.call_tool("detect_language", {"text": "bonjour tout le monde"})
            print(result.content[0].text)

asyncio.run(main())
```

```text
['translate', 'detect_language']
bom dia
fr
```

Without `source_lang`, the server detects the source language before it translates.

## Translate from a UTCP agent

```bash
pip install "utcp>=1.2.0" "utcp-http>=1.1.14"
```

```python
import asyncio
from utcp.utcp_client import UtcpClient

async def main():
    client = await UtcpClient.create(config={"manual_call_templates": [{
        "name": "ovos_translate", "call_template_type": "http",
        "url": "http://localhost:9686/utcp", "http_method": "GET"}]})
    print(await client.call_tool("ovos_translate.translate_with_source",
                                 {"src_lang": "en", "tgt_lang": "de", "utterance": "is 1/2 the answer?"}))
    print(await client.call_tool("ovos_translate.classify_language",
                                 {"utterance": "bonjour tout le monde"}))

asyncio.run(main())
```

```text
ist 1/2 die Antwort?
{'fr': 1.0}
```

The translate server names its UTCP tools `ovos_translate.<tool>`. When the manual has another name in the client config, the client puts that name in front, for example `tx.ovos_translate.translate`. MCP tool names have no prefix (`translate`).

## Tool reference

| Tool | Protocol | Arguments | Result |
|---|---|---|---|
| `translate` | MCP | `text`, `target_lang`, `source_lang` (optional) | Translated text |
| `detect_language` | MCP | `text` | A language tag, for example `fr` |
| `ovos_translate.translate` | UTCP | `tgt_lang`, `utterance` | Translated text |
| `ovos_translate.translate_with_source` | UTCP | `src_lang`, `tgt_lang`, `utterance` | Translated text |
| `ovos_translate.detect_language` | UTCP | `utterance` | A language tag |
| `ovos_translate.classify_language` | UTCP | `utterance` | A map of language tag to score |
| `ovos_translate.supported_languages` | UTCP | none | `{"plugin", "langs"}` |

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `detect_language` fails with `has no attribute 'detect'` | The server started without `--detect-engine`, and the translation plugin cannot detect languages | Start the server with a detection plugin, for example `--detect-engine ovos-google-lang-detector-plugin`. |
| `/mcp` returns `404` | The server started without `--mcp`, or the `mcp` extra is not installed | Install the `mcp` extra. Start the server with `--mcp`. The server log shows a warning when the extra is missing. |
| The UTCP client registers no tools for `http` | `utcp-http` is not installed | Install `utcp-http`. |

## More information

- [AI agent integration](https://github.com/OpenVoiceOS/ovos-translate-server#ai-agent-integration) in the `ovos-translate-server` README.
- [Translate Server](translate-server.md) for all endpoints and plugins.

---
**Read next:** [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md)
**Related:** [AI Agents](ai-agents.md) · [Give a persona MCP and UTCP tools](ai-agent-persona-uses-tools.md) · [Translate Server](translate-server.md)
