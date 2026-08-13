
# `ovos-translate-server` — HTTP Translation Server

!!! abstract "In a nutshell"
    This is a small standalone program. It puts OVOS's language tools online as a web service:
    translating text between languages, and guessing what language a piece of text is in. Other
    devices send it text over a simple web request and get back the translation (or the detected
    language), so one machine can do this work for many. It can also imitate popular translation
    services (like DeepL, Google Translate, or LibreTranslate), so software written for those
    works against your own server unchanged. See [Translation Plugins](translation-plugins.md)
    and the [Glossary](glossary.md).

## What it Does

`ovos-translate-server` wraps any OVOS translation plugin and language-detection plugin. It exposes them as a FastAPI HTTP service (served by `uvicorn`). It is the standard way to make OVOS language plugins available to remote clients, or to use them as a microservice in a Docker-based deployment.

The companion client plugin `ovos-translate-server-plugin` can point an OVOS device at this server so that translation and language detection are offloaded from the device. Left unconfigured, that client plugin falls back to a built-in list of public community-run servers rather than failing (see [Translation Plugins](translation-plugins.md)). Set it to your own server, deployed as taught below, for anything beyond a quick test.

--8<-- "snippets/community-servers.md"

---

## Installation

```bash
pip install ovos-translate-server
```

Also install the translation plugin(s) you intend to serve:

```bash
pip install ovos-translate-plugin-nllb
pip install ovos-lang-detector-classics-plugin
```

---

## Running the Server

### Command Line

```bash
ovos-translate-server \
  --tx-engine ovos-translate-plugin-nllb \
  --detect-engine ovos-lang-detector-classics-plugin \
  --host 0.0.0.0 \
  --port 9686
```

CLI arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--tx-engine` | required | OPM translation plugin (`opm.lang.translate`) entry-point name |
| `--detect-engine` | `None` | OPM language detection plugin (`opm.lang.detect`) entry-point name (optional) |
| `--host` | `0.0.0.0` | Host to bind |
| `--port` | `9686` | TCP port |

If `--detect-engine` is omitted, no dedicated detection plugin is loaded. `/detect` and `/classify` fall back to the translation plugin's own `detect()` / `detect_probs()` methods.

### Python API

```python
import uvicorn
from ovos_translate_server import start_translate_server

app, engine = start_translate_server(
    tx_engine="ovos-translate-plugin-nllb",
    detect_engine="ovos-lang-detector-classics-plugin",
)
uvicorn.run(app, host="0.0.0.0", port=9686)
```

`start_translate_server()` loads the plugins and returns `(app, engine)` where `app` is a FastAPI application. You run it with `uvicorn` (the `ovos-translate-server` CLI does exactly this). The translate and detect plugins are instantiated with an empty config (`config={}`); the server does not read plugin configuration from `mycroft.conf`.

---

## HTTP API Endpoints

All endpoints accept `GET` requests. There is no authentication.

### `GET /status`

Health check. Returns the translation plugin name and its supported languages.

Response (JSON):
```json
{
  "plugin": "ovos-translate-plugin-nllb",
  "langs": ["en", "pt", "fr"]
}
```

---

### `GET /detect/{utterance}`

Detect the language of the given text.

| Path parameter | Description |
|----------------|-------------|
| `utterance` | The text string to classify |

Response: a language code string (e.g. `"pt"`, `"en"`, `"fr"`), returned directly from `LanguageDetector.detect()`.

Example:
```text
GET /detect/o meu nome é Casimiro
→ "pt"
```

---

### `GET /classify/{utterance}`

Return per-language confidence scores for the given text.

| Path parameter | Description |
|----------------|-------------|
| `utterance` | The text string to classify |

Response: a JSON object mapping language codes to confidence floats, returned from `LanguageDetector.detect_probs()`.

Example:
```text
GET /classify/hello world
→ {"en": 0.95, "de": 0.03, ...}
```

---

### `GET /translate/{tgt_lang}/{utterance}`

Translate text to the target language, auto-detecting the source language.

| Path parameter | Description |
|----------------|-------------|
| `tgt_lang` | Target language code (e.g. `"en"`, `"pt"`) |
| `utterance` | Text to translate |

Response: translated string, returned directly from `LanguageTranslator.translate(utterance, target=lang)`.

Example:
```text
GET /translate/en/o meu nome é Casimiro
→ "my name is Casimiro"
```

---

### `GET /translate/{src_lang}/{tgt_lang}/{utterance}`

Translate text with an explicit source language.

| Path parameter | Description |
|----------------|-------------|
| `src_lang` | Source language code (e.g. `"pt"`) |
| `tgt_lang` | Target language code (e.g. `"en"`) |
| `utterance` | Text to translate |

Response: translated string, returned from `LanguageTranslator.translate(utterance, target=lang, source=src)`.

Example:
```text
GET /translate/pt/en/o meu nome é Casimiro
→ "my name is Casimiro"
```

---

### `GET /utcp`

Returns the UTCP (Universal Tool Calling Protocol) manual describing every HTTP endpoint. UTCP-compatible agents can use it to discover and invoke the translation tools. No extra dependency is required.

---

## Vendor-Compatible Routers

Beyond the native endpoints above, the app mounts drop-in compatible routers. Clients written for hosted translation APIs can talk to this server unchanged: DeepL, DeepLX, LibreTranslate, Lingva, Amazon Translate, Google Translate, and Azure Translator. See the server's `/docs` (OpenAPI) for their exact paths.

---

## MCP Server

A Model Context Protocol endpoint exposes the translate/detect tools to MCP clients, served with
the third-party `fastmcp` package (`fastmcp>=3,<4`). It requires the `mcp` extra:

```bash
pip install 'ovos-translate-server[mcp]'
```

!!! note "The `mcp` extra installs `fastmcp`, not the `mcp` SDK"
    The extra name is unchanged, but it resolves `fastmcp`, not the official `mcp` SDK — MCP SDK
    2.0 removed `mcp.server.fastmcp.FastMCP`, so a server still importing that symbol fails to
    start on the 2.x SDK. This server serves with `fastmcp`; a client consuming a different MCP
    server (like `ovos-mcp-toolbox`, see [Agent Tool Plugins](tool-plugins.md)) uses the official
    `mcp` SDK instead.

With the extra installed, the HTTP server auto-mounts MCP at `/mcp` on its own port
(`0.0.0.0:9686` by default) — no separate flag or process needed, and no action if the extra is
missing beyond a log line. A standalone MCP-only process is also available, useful for running
MCP on its own host/port without exposing the HTTP API:

```bash
python -m ovos_translate_server.mcp_server \
  --tx-engine ovos-translate-plugin-nllb \
  --host 127.0.0.1 \
  --port 9687
```

The standalone process defaults to host `127.0.0.1` and port `9687`, distinct from the HTTP
server's `0.0.0.0:9686`. The `FastMCP` instance can also be embedded into an existing FastAPI app.

Either way it exposes two tools: `translate(text, target_lang, source_lang=None)` returns the
translated string (omit `source_lang` to auto-detect), and `detect_language(text)` returns a
BCP-47 tag. A minimal MCP client call to `translate` looks like:

```json
{
  "name": "translate",
  "arguments": {
    "text": "Hello, how are you?",
    "target_lang": "pt"
  }
}
```

which returns a plain-string result such as `"Olá, como você está?"`.

---

## How It Wraps OVOS Translation Plugins

`start_translate_server()` uses two `ovos-plugin-manager` loader functions:

```python
from ovos_plugin_manager.language import load_lang_detect_plugin, load_tx_plugin
```

- `load_tx_plugin(name)`: looks up the `opm.lang.translate` entry-point group for the named plugin
- `load_lang_detect_plugin(name)`: looks up the `opm.lang.detect` entry-point group

Both return the plugin class. Each class is instantiated with an empty config:

```python
self.tx = tx_cls(config={})
self.detect = detect_cls(config={})   # only when --detect-engine is given
```

The translator (`engine.tx`) and optional detector (`engine.detect`) are held on a `TranslateEngineWrapper`. All FastAPI route handlers use them. When no detection plugin is configured, `/detect` and `/classify` call the translator's own `detect()` / `detect_probs()`.

---

## Plugin Interface

Translation plugins must implement `LanguageTranslator` from `ovos_plugin_manager.templates.language`:

```python
class LanguageTranslator:
    def translate(self, text, target="en", source="auto") -> str: ...
```

Detection plugins must implement `LanguageDetector`:

```python
class LanguageDetector:
    def detect(self, text) -> str: ...          # returns language code
    def detect_probs(self, text) -> dict: ...   # returns {lang: confidence}
```

---

## Docker

A minimal Dockerfile for serving a single plugin:

```dockerfile
FROM python:3.11

RUN pip install ovos-translate-server
RUN pip install <plugin-package>

ENTRYPOINT ovos-translate-server --tx-engine <plugin-name>
```

Build and run:

```bash
docker build . -t my-translate-server
docker run -p 9686:9686 my-translate-server
```

!!! note "Upcoming — Docker Compose"
    A default Docker Compose setup and custom-container documentation are in progress
    ([ovos-translate-server#33](https://github.com/OpenVoiceOS/ovos-translate-server/pull/33)).

---

## Gotchas

- **All endpoints are `GET` with the text in the URL path.** Long or special-character utterances must be URL-encoded by the client. There is no request body and no authentication. Don't expose this server directly to untrusted networks. Front it with a reverse proxy.
- With the `mcp` extra installed, MCP is mounted at `/mcp` on the same HTTP server and port
  (`9686`) automatically — nothing extra to run. The standalone MCP-only process (`python -m
  ovos_translate_server.mcp_server`, default `127.0.0.1:9687`) is a separate, optional way to run
  MCP without the HTTP API; running one does not start the other.

---

*Source code: [OpenVoiceOS/ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server).*

---
**Read next:** [Server Compatibility Layers](server-compat-layers.md)
**Related:** [STT Server](stt-server.md) · [TTS Server](tts-server.md) · [Translation Plugins](translation-plugins.md) · [Bidirectional Translation](bidirectional-translation.md)
