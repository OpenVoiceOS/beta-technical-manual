# Speech-to-Text Vendor APIs

!!! abstract "In a nutshell"
    Code written for the OpenAI, Groq, Deepgram, ElevenLabs, IBM Watson or AssemblyAI speech-to-text APIs can get its transcript from your own OVOS STT plugin. Point the SDK at `ovos-stt-server`. The request and the response keep the shape of the vendor API.

## What you can do

`ovos-stt-server` mounts each vendor API under its own prefix. The transcript comes from the OVOS plugin that the server runs. The server accepts vendor model names and ignores them.

## User stories

The recipes ran against `ovos-stt-server --engine ovos-stt-plugin-vosk`, with a 16 kHz mono WAV clip of the words "turn on the kitchen light".

### I have code for the OpenAI SDK

Set `base_url` to the `/openai/v1` prefix. This recipe used `openai` 3.35.1.

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://localhost:8080/openai/v1")
with open("kitchen.wav", "rb") as f:
    print(client.audio.transcriptions.create(model="whisper-1", file=f).text)
with open("kitchen.wav", "rb") as f:
    print(client.audio.transcriptions.create(model="whisper-1", file=f, response_format="text"))
```

```text
turn on the kitchen light
turn on the kitchen light
```

`response_format` can be `json`, `text`, `verbose_json`, `srt` or `vtt`. `client.audio.translations.create(...)` returns English text. When the server has a translation plugin, it translates the transcript. When it has none, it returns the transcript.

### I have code for the Groq SDK

Set `base_url` to the `/groq` prefix. The response has the `x_groq` block that the Groq SDK expects. This recipe used `groq` 1.7.0.

```python
from groq import Groq

client = Groq(api_key="unused", base_url="http://localhost:8080/groq")
with open("kitchen.wav", "rb") as f:
    print(client.audio.transcriptions.create(model="whisper-large-v3", file=f).text)
```

```text
turn on the kitchen light
```

### I have code for another vendor SDK

These SDKs sent the same clip to the same server. Each line is the transcript that the SDK returned.

| SDK | Setting | Call | Output |
| :--- | :--- | :--- | :--- |
| `deepgram-sdk` 7.13.0 | `DeepgramClientEnvironment(base="http://localhost:8080/deepgram", ...)` | `client.listen.v1.media.transcribe_file(request=wav, model="nova-3")` | `turn on the kitchen light` |
| `elevenlabs` 3.0.0a1 | `ElevenLabs(base_url="http://localhost:8080/elevenlabs")` | `client.speech_to_text.convert(file=f, model_id="scribe_v1")` | `turn on the kitchen light` |
| `ibm-watson` 11.2.0 | `stt.set_service_url("http://localhost:8080/watson/speech-to-text")` | `stt.recognize(audio=f, content_type="audio/wav")` | `turn on the kitchen light` |
| `assemblyai` 1.6.5 | `aai.settings.base_url = "http://localhost:8080/assemblyai"` | `aai.Transcriber().transcribe("kitchen.wav")` | `turn on the kitchen light` |

The Deepgram SDK needs all four URLs of `DeepgramClientEnvironment`: `base`, `production`, `agent` (with `ws://`) and `agent_rest`. Each points at the `/deepgram` prefix.

## Endpoint status

| Vendor | Client | Status |
| :--- | :--- | :--- |
| OpenAI | `openai` SDK `audio.transcriptions`, `audio.translations` | Works |
| Groq | `groq` SDK | Works |
| Deepgram (REST) | `deepgram-sdk` | Works |
| ElevenLabs Scribe | `elevenlabs` SDK | Works |
| IBM Watson (REST) | `ibm-watson` SDK | Works |
| AssemblyAI | `assemblyai` SDK | Works |

[Server Compatibility Layers](server-compat-layers.md) lists the other STT prefixes, the streaming routes among them.

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| The SDK gets 404 | `base_url` does not include the vendor prefix | Use `http://<host>:8080/openai/v1` for OpenAI, `http://<host>:8080/groq` for Groq |
| The transcript is empty or wrong | The STT plugin cannot read the audio format | Send 16 kHz 16-bit mono WAV |

---
**Read next:** [Translation vendor APIs](vendor-api-translate.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [STT Server](stt-server.md) · [Server Compatibility Layers](server-compat-layers.md)
