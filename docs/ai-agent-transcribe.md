# Transcribe Audio From an AI Agent: Speech to Text (STT) over MCP and UTCP

Connect an AI agent to the OVOS speech-to-text (STT) server, so the agent can transcribe audio files. Use the STT server when Claude Code, Claude Desktop, opencode, Mistral Vibe, or your own MCP or UTCP agent must turn speech into text with an STT engine that runs on your own computer.

## What you get

- An MCP tool `transcribe` at `http://localhost:8080/mcp`.
- A UTCP manual at `http://localhost:8080/utcp` with the tools `stt`, `lang_detect` and `status`.
- A JSON endpoint `POST /stt/json` that takes base64 audio and returns `{"text", "lang"}`.

## Start the server

!!! warning "Alpha channel only"
    The `mcp` extra is only in the prerelease channel. Install the server
    from that channel:

    ```bash
    pip install --pre "ovos-stt-http-server[mcp]" ovos-stt-plugin-vosk
    ```

1. Start the server with the `--mcp` flag:

    ```bash
    ovos-stt-server --engine ovos-stt-plugin-vosk --mcp
    ```

2. Make sure that the server answers:

    ```bash
    curl -s http://localhost:8080/status
    ```

    ```json
    {"status":"ok","plugin":"ovos-stt-plugin-vosk","lang_plugin":null}
    ```

## Transcribe from Claude Code

1. Add the server to Claude Code:

    ```bash
    claude mcp add --transport http ovos-stt http://localhost:8080/mcp
    ```

2. Make sure that Claude Code can connect:

    ```bash
    claude mcp list
    ```

    ```text
    ovos-stt: http://localhost:8080/mcp (HTTP) - ✔ Connected
    ```

3. Ask Claude Code to transcribe a file, for example: "Transcribe /home/me/speech.wav with the ovos-stt tool". Give an absolute path. The server reads the file from its own disk.

## Transcribe from Claude Desktop

Claude Desktop starts MCP servers from `claude_desktop_config.json` as local commands. The `mcp-remote` bridge is a local command that connects to the HTTP endpoint. The bridge needs Node.js.

1. Add this entry to `claude_desktop_config.json`:

    ```json
    {
      "mcpServers": {
        "ovos-stt": {
          "command": "npx",
          "args": ["-y", "mcp-remote", "http://localhost:8080/mcp"]
        }
      }
    }
    ```

2. Restart Claude Desktop.

The bridge gives Claude Desktop the same `transcribe` tool. A call through the bridge returned this transcript for a WAV file of the words "turn on the kitchen light":

```text
on the kitchen life
```

The transcript comes from the small Vosk English model. A larger model gives better text.

## Transcribe from opencode

1. Add the server to `opencode.json` in your project folder:

    ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "mcp": {
        "ovos-stt": {
          "type": "remote",
          "url": "http://localhost:8080/mcp",
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
    ●  ✓ ovos-stt connected
    │      http://localhost:8080/mcp
    ```

## Transcribe from Mistral Vibe

1. Add the server to `~/.vibe/config.toml`:

    ```toml
    [[mcp_servers]]
    name = "ovos-stt"
    transport = "streamable-http"
    url = "http://localhost:8080/mcp"
    ```

    Write the entry in the file. Do not use `vibe mcp add` for this server: that command sets OAuth login for an HTTP server, and the OVOS server does not use OAuth.

2. Start `vibe`. Vibe loads the tools of the server when it starts. It gives each tool the server name as a prefix and changes each hyphen to `_`, for example `ovos_stt_transcribe`.

## Transcribe from your own MCP client

This script uses the `mcp` SDK (`pip install "mcp>=2.3.0"`):

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://localhost:8080/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "transcribe", {"audio_path": "/home/me/speech.wav", "lang": "en-us"})
            print(result.content[0].text)

asyncio.run(main())
```

```text
on the kitchen life
```

## Transcribe from a UTCP agent

The UTCP client reads the manual at `/utcp` and calls `POST /stt/json`. Install the client and its HTTP plugin:

```bash
pip install "utcp>=1.2.0" "utcp-http>=1.1.14"
```

```python
import asyncio, base64
from utcp.utcp_client import UtcpClient

async def main():
    client = await UtcpClient.create(config={"manual_call_templates": [{
        "name": "ovos_stt", "call_template_type": "http",
        "url": "http://localhost:8080/utcp", "http_method": "GET"}]})
    audio = base64.b64encode(open("/home/me/speech.wav", "rb").read()).decode()
    print(await client.call_tool("ovos_stt.stt", {"body": {"audio_b64": audio, "lang": "en-us"}}))

asyncio.run(main())
```

```text
{'text': 'on the kitchen life', 'lang': 'en-us'}
```

## Transcribe with plain HTTP

`POST /stt/json` takes the same body without an agent:

```bash
printf '{"audio_b64": "%s", "lang": "en-us"}' "$(base64 -w0 speech.wav)" > request.json
curl -s -X POST http://localhost:8080/stt/json -H 'Content-Type: application/json' -d @request.json
```

```json
{"text":"on the kitchen life","lang":"en-us"}
```

## Tool reference

| Tool | Protocol | Arguments | Result |
|---|---|---|---|
| `transcribe` | MCP | `audio_b64` or `audio_path`, `lang` (default `"auto"`), `sample_rate` (default `16000`), `sample_width` (default `2`) | The transcript as text |
| `stt` | UTCP | `body.audio_b64`, `body.lang`, `body.sample_rate`, `body.sample_width` | `{"text", "lang"}` |
| `lang_detect` | UTCP | raw PCM bytes in `body`, `valid_langs` | `{"lang", "conf"}` |
| `status` | UTCP | none | `{"status", "plugin", "lang_plugin"}` |

The server decodes a WAV file with the sample rate, sample width and channels of the file. It reads any other audio as raw 16-bit PCM at `sample_rate`. `audio_path` names a file on the disk of the server.

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `/mcp` returns `404` | The server started without `--mcp`, or the `mcp` extra is not installed | Install the `mcp` extra. Start the server with `--mcp`. Read the server log for the warning about the extra. |
| `claude mcp list` shows `Failed to connect` | The server is not running, or the port is different | Run `curl -s http://localhost:8080/status`. Use the port that the server prints when it starts. |
| The transcript is empty | The audio is not WAV and not 16-bit PCM at `sample_rate` | Convert the audio to WAV. |
| The UTCP client registers no tools for `http` | `utcp-http` is not installed | Install `utcp-http`. |

!!! danger "Any client can read files on the server"
    `audio_path` reads any file that the server process can read. Bind the server to `127.0.0.1`, or put a reverse proxy with authentication in front of it.

## More information

- [AI agent integration](https://github.com/OpenVoiceOS/ovos-stt-server#ai-agent-integration) in the `ovos-stt-server` README.
- [STT Server](stt-server.md) for all endpoints, the Docker image and the configuration.

---
**Read next:** [Let an AI agent speak](ai-agent-speak.md)
**Related:** [AI Agents](ai-agents.md) · [Translate text from an AI agent](ai-agent-translate.md) · [STT Server](stt-server.md)
