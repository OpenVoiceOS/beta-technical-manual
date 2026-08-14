# OpenVoiceOS [TTS](tts-plugins.md) Server

!!! abstract "In a nutshell"
    This is a small standalone program that turns any OVOS text-to-speech voice into a web
    service. Text-to-speech is the part that reads written text aloud. You send it some text
    over a simple web request, and it sends back the spoken audio. This lets one capable machine
    do the talking for many lightweight devices. It can also imitate popular cloud voice services
    (like ElevenLabs or OpenAI), letting software built for those use your own server instead.
    See [TTS plugins](tts-plugins.md) and the [Glossary](glossary.md).

**Lightweight HTTP microservice for any OVOS text‑to‑speech plugin, with optional caching.**

Wrap your favorite OVOS TTS engine in a FastAPI service. It is ready to deploy locally, in Docker, or behind a load balancer.

The OpenVoiceOS TTS HTTP Server exposes any OVOS TTS plugin over a simple HTTP API. Send text, receive audio. No extra
glue code is required.

---

## Usage Guide

**Install the server**

```bash
pip install ovos-tts-server

```

**Configure your TTS plugin**

In your `mycroft.conf` (or equivalent) under the `tts` section:

```json
{
 "tts": {
   "module": "ovos-tts-plugin-xxx",
   "ovos-tts-plugin-xxx": {
     "voice": "xxx"
   }
 }
}

```

**Launch the server**  

```bash
ovos-tts-server \
 --engine ovos-tts-plugin-xxx \
 --host 0.0.0.0 \
 --port 9666

```

**Verify it's running**  

Visit http://localhost:9666/status in your browser or run:

```bash
curl http://localhost:9666/status

```

---

## Command‑Line Options

```bash
$ ovos-tts-server --help
usage: ovos-tts-server [-h] [--engine ENGINE] [--port PORT] [--host HOST] [--cache] [--lang LANG] [--mcp]

options:
  -h, --help            show this help message and exit
  --engine ENGINE       tts plugin to be used
  --port PORT           port number
  --host HOST           host
  --cache               save every synth to disk
  --lang LANG           language the plugin serves; selects its default voice when no
                        voice is configured. Overrides the plugin's configured
                        language.
  --mcp                 mount MCP server at /mcp (requires ovos-tts-server[mcp])

```

Flag details the short help text leaves out: the port defaults to `9666` and the host to
`0.0.0.0`. The companion plugin defaults to `/v2/synthesize` on that port; if you point an
old client at the legacy `/synthesize/{utterance}` path, set `"v2": false` in its config.
When `--lang` is omitted, the plugin uses its own configured `lang`, then the top-level
config `lang`, then falls back to `"mul"`.

!!! example "A worked multi-flag invocation"
    Serve a specific engine, override its language to European Portuguese, and cache every
    synthesis to disk for later inspection:

    ```bash
    ovos-tts-server --engine ovos-tts-plugin-phoonnx --cache --lang pt-pt
    ```

---

## Technical Explanation

- **FastAPI Core**  
  Spins up a FastAPI application exposing RESTful endpoints for synthesis and status checks.

- **Plugin Loading**  
  `--engine` names any `opm.tts` plugin entry point. It is loaded dynamically via the OVOS Plugin Manager, so no code changes are needed when adding new voices. Plugin config is read from the `tts` section of your `mycroft.conf`.

- **Caching**  
  When `--cache` is enabled, every synthesis request is stored on disk for debugging or reuse.

- **Compatibility routers**  
  The app also mounts drop-in compatible routers so existing cloud-TTS clients work unchanged: ElevenLabs, OpenAI, Coqui, Google, Amazon Polly, Azure, MaryTTS, Cartesia, Deepgram Aura, and PlayHT. A `GET /utcp` manual advertises the endpoints to UTCP agents. `--mcp` mounts an MCP server at `/mcp` (requires the `mcp` extra).

- **Scalability**  
  Stateless by design — run multiple instances behind NGINX, Traefik, or Kubernetes with round‑robin or load‑based
  routing.

---

## HTTP API Endpoints

| Endpoint                  | Method | Description                                                          |
|---------------------------|--------|---------------------------------------------------------------------|
| `/status`                 | GET    | Returns loaded plugin name, supported `langs`, and `default_lang` / `default_model` / `default_voice`. |
| `/synthesize/{utterance}` | GET    | Legacy: URL‑encoded text in the path → synthesized audio file.      |
| `/v2/synthesize`          | GET    | `utterance` (required) plus optional query params → synthesized audio file. |
| `/utcp`                   | GET    | UTCP tool-discovery manual (JSON).                                  |
| `/docs`                   | GET    | Interactive OpenAPI (Swagger) docs.                                 |

> Both synthesis endpoints respond with a `FileResponse` (the audio file written by the plugin, WAV by default).
> Any extra query parameters on `/v2/synthesize` (besides `utterance`) are forwarded to the plugin's `get_tts` method as kwargs.
> 💡 This allows `"voice"` and `"lang"` to be set per-request at runtime rather than only by plugin config at load time (for plugins that support it). A missing `utterance` returns HTTP 400.

---

## Transformer Pipelines

The server can run OVOS [dialog and TTS transformer](tts-transformers.md) plugins around
synthesis, on every synthesis surface (native endpoints and vendor-compat routers alike):

- **Dialog transformers** rewrite the *text* before it reaches the TTS plugin (e.g. text
  normalization, profanity filtering, per-locale rewrites).
- **TTS transformers** post-process the *synthesized audio* (e.g. loudness normalization,
  effects).

Loading is config-gated and opt-in via the standard `mycroft.conf` sections. With no config
the server behaves exactly as before:

```json
{
  "dialog_transformers": {
    "ovos-dialog-transformer-openai-plugin": {}
  },
  "tts_transformers": {
    "ovos-tts-transformer-sox-plugin": {}
  }
}

```

---

## ElevenLabs Streaming (`stream-input`)

Every ElevenLabs-compatible route sits behind the `/elevenlabs` prefix. Point an ElevenLabs
SDK at `http://<host>:9666/elevenlabs`, not at the server root. See [Server Compatibility
Layers](server-compat-layers.md).

The plain HTTP routes are `/elevenlabs/v1/voices`, `/elevenlabs/v1/models` and
`/elevenlabs/v1/text-to-speech/{voice_id}`. The server also implements ElevenLabs' WebSocket
streaming protocol, at `/elevenlabs/v1/text-to-speech/{voice_id}/stream-input`. This lets clients written
against the real ElevenLabs streaming SDK work unmodified.

The client connects with the voice in the path and synthesis options in the query string
(`model_id`, `output_format`, `language_code`, `sync_alignment`, …), then sends JSON text
frames:

1. **BOS**: `{"text": " ", "voice_settings": {...}, "generation_config": {...}}` opens the
   stream (its text payload is a single space and carries no content).
2. **Content**: `{"text": "Hello there "}`, repeated. Text accumulates until a generation
   is triggered.
3. `{"flush": true}` (optionally with more text) forces the buffered text to synthesize
   immediately.
4. **EOS**: `{"text": ""}` closes the stream. Whatever is buffered is generated, then the
   connection terminates.

The server answers with JSON frames carrying base64-encoded audio
(`{"audio": "<base64>", "isFinal": null, ...}`) and a final frame with no audio and
`isFinal: true`. The `xi-api-key` header (or `xi_api_key` in the BOS message) is accepted
but ignored. A self-hosted server has no keys to check.

---

!!! tip "Deploying this server"
    Pointing an OVOS instance at this server with the companion client plugin, or running
    the server itself in Docker? See [TTS Server Deployment](tts-server-deployment.md).

## Tips & Caveats

- **Audio Formats**: By default, outputs WAV (PCM). If you need MP3 or OGG, wrap with an external converter or check
  plugin support.

- **Disk Usage**: `--cache` saves every synthesis to disk, and that directory grows unbounded. Omit the flag to disable caching. There is no `--no-cache` flag. Caching is simply off by default.


- **Security**: Consider adding API keys or putting a reverse proxy (NGINX, Traefik) in front for SSL termination and
  rate limiting. See [stt-server: a minimal NGINX server block](stt-server.md#tips-caveats) for a worked example.
  The same shape applies here, just point `proxy_pass` at port 9666 instead of 8080.

- **Plugin Dependencies**: Some voices require native libraries (e.g., TensorFlow). Bake them into your Docker image to
  avoid runtime surprises.

---

## Links & References

- **TTS Server GitHub**: https://github.com/OpenVoiceOS/ovos-tts-server


- **Companion Plugin**: https://github.com/OpenVoiceOS/ovos-tts-server-plugin


- **Docker Images**: https://github.com/OpenVoiceOS/ovos-docker-tts


- **OVOS Plugin Manager**: https://github.com/OpenVoiceOS/ovos-plugin-manager

---
**Read next:** [Translate Server](translate-server.md)
**Related:** [TTS Server Deployment](tts-server-deployment.md) · [STT Server](stt-server.md) · [Server Compatibility Layers](server-compat-layers.md) · [TTS Plugins](tts-plugins.md) · [Privacy & Security](privacy-security.md)