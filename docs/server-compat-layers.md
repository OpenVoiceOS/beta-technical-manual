# Server Compatibility Layers

!!! abstract "In a nutshell"
    The OVOS servers (for speech-to-text, text-to-speech, translation, and chat personas) can *impersonate* popular commercial services such as OpenAI, Google, DeepL, and ElevenLabs. This page lists which imitations each server offers. The benefit is simple: an app written to talk to one of those services can point at your own OVOS server instead, with no code changes. Think of it as a power adapter that lets the same plug fit a different socket. See the [STT Server](stt-server.md), [TTS Server](tts-server.md), [Translate Server](translate-server.md), and [Persona Server](persona-server.md) pages, or the [Glossary](glossary.md).

Each OVOS service server exposes vendor-prefixed routers. Existing clients and integrations can connect without modification. Every router accepts the vendor's original request format and translates it to the native OVOS plugin call.

!!! warning "A compatible wire format does not guarantee identical capabilities"
    Matching a vendor's request and response shape does not always mean the *behavior*
    underneath matches, especially around streaming. For example, the TTS server's
    ElevenLabs `stream-input` WebSocket router accepts text incrementally. It sends audio
    back in frames, exactly like the real ElevenLabs protocol. Underneath, though, each
    buffered chunk of text is still synthesized with one ordinary, blocking call to the
    configured OVOS TTS plugin. Only the resulting complete audio is sliced into
    fixed-size frames afterward. Most OVOS TTS plugins do not support true incremental,
    word-by-word synthesis. The first audio frame is not available until that chunk has
    finished generating in full. Clients built around the real API's low first-byte
    latency may not see the same latency here. Check the specific router and the
    underlying plugin's capabilities before assuming parity beyond the wire format.

---

## Pattern

Each compat router is a self-contained FastAPI `APIRouter` mounted under a fixed vendor prefix. The router:

1. Accepts the vendor's HTTP contract (paths, query params, request/response bodies).
2. Translates to the server's internal `process()` call.
3. Returns the vendor's expected response format.

All compat routers are always loaded. No feature flag is needed.

---

## STT Server Compat Routes

`pip install ovos-stt-http-server`. Routers are implemented in `ovos_stt_http_server.routers`.

| Prefix | Vendor |
|--------|--------|
| `/openai` | OpenAI Whisper (`/openai/v1/audio/transcriptions`, plus `/openai/v1/audio/translations` — transcribes then translates to English via the configured OVOS translate plugin) |
| `/deepgram` | Deepgram |
| `/google` | Google Cloud Speech |
| `/assemblyai` | AssemblyAI |
| `/speechmatics` | Speechmatics |
| `/azure-stt` | Microsoft Azure Speech |
| `/aws` | AWS Transcribe |
| `/watson/speech-to-text` | IBM Watson STT |
| `/wit` | Wit.ai |
| `/vosk` | Vosk-server WebSocket |
| `/vosk-webrtc` | Vosk WebRTC variant |
| `/whisper-cpp` | whisper.cpp HTTP server |
| `/gladia` | Gladia |
| `/groq` | Groq Whisper |
| `/elevenlabs` | ElevenLabs Scribe |
| `/speech-api` | Chromium/Google `speech-api` |
| `/client` | Kaldi GStreamer Server |

---

## TTS Server Compat Routes

`pip install ovos-tts-server`. Routers are implemented in `ovos_tts_server.routers`.

| Prefix | Vendor |
|--------|--------|
| `/elevenlabs` | ElevenLabs (HTTP `/v1/text-to-speech/{voice_id}` plus the `stream-input` WebSocket streaming protocol) |
| `/openai` | OpenAI TTS |
| `/coqui` | Coqui TTS |
| `/google-tts` | Google Cloud TTS |
| `/amazon-polly` | Amazon Polly |
| `/azure-tts` | Microsoft Azure TTS |
| `/cartesia` | Cartesia |
| `/deepgram` | Deepgram Aura |
| `/playht` | PlayHT |
| `/marytts` | MaryTTS (`/marytts/process`, `/voices`, `/locales`) |

---

## Translate Server Compat Routes

`pip install ovos-translate-server`. Routers are implemented in `ovos_translate_server.routers`.

| Prefix | Vendor |
|--------|--------|
| `/libretranslate` | LibreTranslate |
| `/deepl` | DeepL v2 |
| `/deeplx` | DeepLX |
| `/google` | Google Translate v2 |
| `/azure` | Azure Translator v3 |
| `/amazon` | Amazon Translate |
| `/lingva` | Lingva Translate |

---

## Persona Server Compat Routes

`pip install ovos-persona-server`. `create_persona_app()` mounts the routes below.
It mounts a chat router at prefix `/v1` (`POST /v1/chat/completions`, OpenAI-compatible),
an Ollama router at prefix `/api`, and a UTCP router at `/tools`. It also mounts `/mcp`
when the `mcp` extra is installed.

| Prefix | Vendor |
|--------|--------|
| `/v1` | OpenAI-compatible chat (`POST /v1/chat/completions`) |
| `/api` | Ollama |
| `/tools` | UTCP tool manifest and invocation |
| `/mcp` | MCP server (requires the `mcp` extra) |

!!! note "Other vendor routers exist but are not mounted"
    The source tree also has vendor-specific router modules for Anthropic, Gemini,
    Cohere, HuggingFace TGI, and AWS Bedrock. `create_persona_app()` does not mount
    any of them yet, so their routes are not reachable in the shipped app.

### OpenAI-compatible example

```python
import openai

client = openai.OpenAI(api_key="", base_url="http://localhost:8337/v1")
response = client.chat.completions.create(
    model="",
    messages=[{"role": "user", "content": "tell me a joke"}]
)
print(response.choices[0].message.content)
```

---

## Related Pages

- [STT Server](stt-server.md)
- [TTS Server](tts-server.md)
- [Translate Server](translate-server.md)
- [Persona Server](persona-server.md)
- [Agent Interoperability](agent-interop.md): MCP/UTCP endpoints on these same servers

---

*Source code: [ovos-stt-http-server](https://github.com/OpenVoiceOS/ovos-stt-http-server), [ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server), [ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server), [ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server).*
