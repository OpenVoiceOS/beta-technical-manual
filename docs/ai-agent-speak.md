# Let an AI Agent Speak: Text to Speech (TTS) over MCP and UTCP

This page connects an AI agent to the OVOS text-to-speech (TTS) server, so the agent can turn text into a WAV file.

## Who this is for

You use Claude Code, Claude Desktop, or your own MCP agent. You want the agent to make speech with a TTS voice that runs on your own computer.

## What you get

- An MCP tool `synthesize` at `http://localhost:9666/mcp`. It returns the WAV audio as base64.
- A UTCP manual at `http://localhost:9666/utcp`.

## Start the server

The `mcp` extra of `ovos-tts-server` 1.15.3a1 needs `fastmcp` 3. The `mcp` extras of `ovos-stt-http-server` 0.28.0a1, `ovos-translate-server` 0.11.3a3 and `ovos-persona-server` 0.18.6a1 need `fastmcp` 4.1.1 or later. Install the TTS server in its own virtual environment.

1. Make a virtual environment for the TTS server:

    ```bash
    python3 -m venv ~/venvs/ovos-tts
    ```

2. Install the server and a voice:

    ```bash
    ~/venvs/ovos-tts/bin/pip install --pre "ovos-tts-server[mcp]>=1.15.3a1" ovos-tts-plugin-espeakng
    ```

3. Start the server with the `--mcp` flag:

    ```bash
    ~/venvs/ovos-tts/bin/ovos-tts-server --engine ovos-tts-plugin-espeakng --mcp
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

`file speech.wav` reports `RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 22050 Hz`. The [STT story](ai-agent-transcribe.md) transcribes this file.

## Read the server status over UTCP

The UTCP manual lists `tts_status`, `tts_synthesize_v2` and `tts_synthesize_legacy`. `tts_status` returns the plugin and its languages:

```text
{'status': 'ok', 'plugin': 'ovos-tts-plugin-espeakng', 'langs': ['eo', 'id', 'en-gb', ...]}
```

In `ovos-tts-server` 1.15.3a1, the two synthesis tools return raw WAV bytes. The UTCP client reads every answer that is not JSON as text, so it stops with `UnicodeDecodeError`. Use the MCP tool `synthesize` to make speech.

## Tool reference

| Tool | Protocol | Arguments | Result |
|---|---|---|---|
| `synthesize` | MCP | `text`, `voice` (optional), `lang` (optional) | `{"mime_type": "audio/wav", "data": <base64 WAV>, "path": <file on the server>, "phonemes"}` |
| `tts_status` | UTCP | none | `{"status", "plugin", "langs", ...}` |

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| The install stops with `requirements are unsatisfiable` | The TTS server and another OVOS server are in the same environment | Install the TTS server in its own virtual environment. |
| `/mcp` returns `404` | The server started without `--mcp`, or the `mcp` extra is not installed | Install the `mcp` extra. Start the server with `--mcp`. The server log shows a warning when the extra is missing. |
| A client behind a TLS reverse proxy refuses a redirect | `ovos-tts-server` 1.15.3a1 answers `POST /mcp` with `307` and the location `/mcp/` | Use `http://<host>:9666/mcp/`, with the slash at the end. |
| `UnicodeDecodeError` from the UTCP client | The UTCP synthesis tools of `ovos-tts-server` 1.15.3a1 return raw WAV | Use the MCP tool `synthesize`. |

## More information

- [Agent integration](https://github.com/OpenVoiceOS/ovos-tts-server#agent-integration) in the `ovos-tts-server` README.
- [TTS Server](tts-server.md) and [TTS Server Deployment](tts-server-deployment.md).

---
**Read next:** [Translate text from an AI agent](ai-agent-translate.md)
**Related:** [AI Agents](ai-agents.md) · [Transcribe audio from an AI agent](ai-agent-transcribe.md) · [TTS Server](tts-server.md)
