# TTS Server Deployment

!!! abstract "In a nutshell"
    This page covers pointing a live OVOS instance at your [TTS Server](tts-server.md) through the companion client plugin, and running the server itself in Docker. For the server's own usage, CLI options, and HTTP API, see [TTS Server](tts-server.md).

## Companion Plugin

Point your OVOS instance at this TTS server with the companion client plugin
(repo `ovos-tts-server-plugin`, class `OVOSServerTTS`, entry point and PyPI package
`ovos-tts-plugin-server`):

```bash
pip install ovos-tts-plugin-server

```

!!! note "Key name: `host`, not `urls`"
    This TTS companion plugin reads the **`host`** key. The
    [STT companion plugin](stt-server.md#companion-plugin) reads a different key,
    **`urls`** (a list). The two are not interchangeable. If you set the wrong key, the
    plugin does not error. It silently ignores the value and falls back to the
    public servers described below.

**Configuration** `mycroft.conf`:

```json
{
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
        "host": "http://localhost:9666",
        "voice": "xxx",
        "v2": true,
        "verify_ssl": true,
        "tts_timeout": 5
     }
 } 
}

```

**Restart and verify**

After editing the config, restart the client so it picks up the change, then confirm it
is actually talking to your server:

```bash
# raspOVOS
ovos-restart

# any other systemd-managed install
systemctl --user restart ovos.service
```

Ask the assistant to say something and check the voice/audio logs, or watch live traffic
with [`ovos-busmon`](bus-service.md), to confirm the configured `host` server is the one
receiving the request, not a public fallback.

!!! warning "No `host` configured → public servers, not local failure"
    If you omit `host`, the plugin does **not** fail. It silently falls back to a built-in
    list of **public** OVOS TTS servers run by community members, shuffled and tried in order.
    That's fine for a quick test, but every sentence your assistant speaks is sent to a
    third-party server by default until you set `host` yourself. Always set `host` explicitly
    (as in the localhost example above) for any real deployment.

--8<-- "snippets/community-servers.md"

See [TTS plugins](tts-plugins.md) for fully offline voices if you'd rather not depend on any server.

## MCP

The STT, translate, and persona servers all moved to explicit opt-in, and so did this one.
`ovos-tts-server` mounts its MCP endpoint only when started with the `--mcp` flag (installing
the `mcp` extra alone is not enough):

```bash
pip install 'ovos-tts-server[mcp]'
ovos-tts-server --engine {YOUR_TTS_PLUGIN} --mcp
```

The endpoint lands at `/mcp`, on the same host and port as the HTTP API. Installing the extra
without the flag does nothing observable at startup — the server starts and the HTTP API works
normally — but `/mcp` returns `404`, which looks like a routing problem rather than a missing
flag. If MCP tool calls 404, check that `--mcp` was actually passed.

!!! note "The `mcp` extra installs `fastmcp`, not the `mcp` SDK"
    The extra keeps the name `mcp`, but it resolves the third-party `fastmcp>=3,<4` package, not
    the official `mcp` SDK. MCP SDK 2.0 removed `mcp.server.fastmcp.FastMCP`, so a server still
    importing that symbol fails to start on the 2.x SDK. This server *serves* MCP with `fastmcp`.
    A client consuming a different MCP server (like `ovos-mcp-toolbox`, see
    [Agent Tool Plugins](tool-plugins.md)) uses the official `mcp` SDK instead.

Config keys:

| Key | Default | Description |
|-----|---------|-------------|
| `host` | public servers | Server base URL, or a list of URLs to try in order. If unset, a built-in list of public OVOS TTS servers is shuffled and used. |
| `v2` | `true` | Use `/v2/synthesize` (utterance as a query param); set `false` to use the legacy `/synthesize/{utterance}` path. |
| `voice` | plugin default | Voice name forwarded as a query param (omitted when unset or `"default"`). |
| `verify_ssl` | `true` | Verify the server's TLS certificate. |
| `tts_timeout` | `5` | Per-request timeout in seconds. |

!!! note "Upcoming — universal server adapter"
    A `server_type` option (plus first-class `api_key` support) is planned for the companion
    plugin, so a single config shape can target different self-hosted or cloud TTS server APIs
    without a dedicated plugin per vendor.


## Docker Deployment

Plain Docker works today. A working `Dockerfile` follows below. What is still **upcoming** is
only a ready-made Docker *Compose* proxy setup for this server.

!!! tip "An interim path: some TTS plugins ship their own Docker image"
    A few TTS plugin repositories (for example the eSpeak NG, S.A.M., and Mimic engines)
    already ship their own `Dockerfile` and `docker-compose.yml` that build a ready-made
    container serving that engine behind `ovos-tts-server`. Until the compose proxy above
    lands, check a plugin's own repository for a Dockerfile before building one by hand.

**Create a Dockerfile**

```dockerfile
FROM python:3.11-slim
RUN pip install ovos-tts-server
RUN pip install {YOUR_TTS_PLUGIN}
ENTRYPOINT ["ovos-tts-server", "--engine", "{YOUR_TTS_PLUGIN}"]

```

**Build & Run**

```bash
docker build -t my-ovos-tts .
docker run -p 9666:9666 my-ovos-tts

```

Pre-built containers are also available via the [ovos-docker-tts](https://github.com/OpenVoiceOS/ovos-docker-tts)
repository.

!!! note "Upcoming — Docker Compose"
    A default Docker Compose setup and custom-container documentation are **Upcoming**.

---

---
**Read next:** [TTS Server](tts-server.md)
**Related:** [STT Server](stt-server.md) · [TTS Plugins](tts-plugins.md) · [Server Compatibility Layers](server-compat-layers.md)
