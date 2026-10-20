# Let an AI Agent Speak: Text to Speech (TTS) over MCP and UTCP

Connect an AI agent to the OVOS text-to-speech (TTS) server, so the agent can turn text into a WAV file. Use the TTS server when Claude Code, Claude Desktop, opencode, Mistral Vibe, or your own MCP or UTCP agent must make speech with a TTS voice that runs on your own computer.

## What you get

- An MCP tool `synthesize` at `http://localhost:9666/mcp`. It returns the WAV audio as base64.
- A UTCP manual at `http://localhost:9666/utcp`.

## Start the server

!!! warning "Alpha channel only"
    The `mcp` extra needs the prerelease channel:

    ```bash
    pip install --pre "ovos-tts-server[mcp]" ovos-tts-plugin-espeakng
    ```

1. Start the server with the `--mcp` flag:

    ```bash
    ovos-tts-server --engine ovos-tts-plugin-espeakng --mcp
    ```

## Speak from Claude Code

1. Add the server to Claude Code:

    ```bash
    claude mcp add --transport http ovos-tts http://localhost:9666/mcp
    ```

2. Make sure that Claude Code can connect:

    ```bash
    claude mcp list
    ```

    ```text
    ovos-tts: http://localhost:9666/mcp (HTTP) - ✔ Connected
    ```

## Speak from Claude Desktop

Add the `mcp-remote` bridge to `claude_desktop_config.json`, then restart Claude Desktop. The bridge needs Node.js.

```json
{
  "mcpServers": {
    "ovos-tts": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:9666/mcp"]
    }
  }
}
```

## Speak from opencode

1. Add the server to `opencode.json` in your project folder:

    ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "mcp": {
        "ovos-tts": {
          "type": "remote",
          "url": "http://localhost:9666/mcp",
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
    ●  ✓ ovos-tts connected
    │      http://localhost:9666/mcp
    ```

## Speak from Mistral Vibe

1. Add the server to `~/.vibe/config.toml`:

    ```toml
    [[mcp_servers]]
    name = "ovos-tts"
    transport = "streamable-http"
    url = "http://localhost:9666/mcp"
    ```

    Write the entry in the file. Do not use `vibe mcp add` for this server: that command sets OAuth login for an HTTP server, and the OVOS server does not use OAuth.

2. Start `vibe`. Vibe loads the tools of the server when it starts. It gives each tool the server name as a prefix and changes each hyphen to `_`, for example `ovos_tts_synthesize`.

## Speak from your own MCP client

This script calls `synthesize` and writes the audio to `speech.wav`. It uses the `mcp` SDK (`pip install "mcp>=2.3.0"`) in any environment. The client does not need the environment of the server.

```python
import asyncio, base64, json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://localhost:9666/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "synthesize", {"text": "turn on the kitchen light", "lang": "en-us"})
            reply = json.loads(result.content[0].text)
            open("speech.wav", "wb").write(base64.b64decode(reply["data"]))
            print(reply["mime_type"], len(reply["data"]), "base64 characters")

asyncio.run(main())
```

```text
audio/wav 88896 base64 characters
```

`file speech.wav` reports `RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 22050 Hz`. To transcribe this file, see [Transcribe audio from an AI agent](ai-agent-transcribe.md).

## Speak from a UTCP agent {#read-the-server-status-over-utcp}

The UTCP manual lists `tts_status` and `tts_synthesize_v2`. `tts_status` returns the plugin and its languages. `tts_synthesize_v2` returns the same JSON object as the MCP tool `synthesize`:

```python
import asyncio, base64
from utcp.utcp_client import UtcpClient

async def main():
    client = await UtcpClient.create(config={"manual_call_templates": [{
        "name": "ovos_tts", "call_template_type": "http",
        "url": "http://localhost:9666/utcp", "http_method": "GET"}]})
    print(await client.call_tool("ovos_tts.tts_status", {}))
    reply = await client.call_tool("ovos_tts.tts_synthesize_v2",
                                   {"utterance": "turn on the kitchen light", "lang": "en-us"})
    open("speech.wav", "wb").write(base64.b64decode(reply["data"]))
    print(reply["mime_type"])

asyncio.run(main())
```

```text
{'status': 'ok', 'plugin': 'ovos-tts-plugin-espeakng', 'langs': ['fr-ch', 'th', 'uz', 'en-us', ...], 'default_lang': 'en-us', 'default_model': None, 'default_voice': 'm1'}
audio/wav
```

## Tool reference

| Tool | Protocol | Arguments | Result |
|---|---|---|---|
| `synthesize` | MCP | `text`, `voice` (optional), `lang` (optional) | `{"mime_type": "audio/wav", "data": <base64 WAV>, "path": <file on the server>, "phonemes"}` |
| `tts_status` | UTCP | none | `{"status", "plugin", "langs", ...}` |
| `tts_synthesize_v2` | UTCP | `utterance`, `voice` (optional), `lang` (optional) | `{"mime_type", "data", "phonemes"}` |

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `/mcp` returns `404` | The server started without `--mcp`, or the `mcp` extra is not installed | Install the `mcp` extra. Start the server with `--mcp`. The server log shows a warning when the extra is missing. |
| A client behind a TLS reverse proxy refuses a redirect | The server answers `POST /mcp` with `307` and the location `/mcp/` | Use `http://<host>:9666/mcp/`, with the slash at the end. |

## More information

- [Agent integration](https://github.com/OpenVoiceOS/ovos-tts-server#agent-integration) in the `ovos-tts-server` README.
- [TTS Server](tts-server.md) and [TTS Server Deployment](tts-server-deployment.md).

---
**Read next:** [Translate text from an AI agent](ai-agent-translate.md)
**Related:** [AI Agents](ai-agents.md) · [Transcribe audio from an AI agent](ai-agent-transcribe.md) · [TTS Server](tts-server.md)
