# Text-to-Speech Vendor APIs

!!! abstract "In a nutshell"
    Code written for the OpenAI, ElevenLabs or Amazon Polly speech APIs can speak through your own OVOS TTS plugin. A device or client that speaks MaryTTS can do the same. Point the client at `ovos-tts-server`, and the audio comes from the plugin that the server runs.

## What you can do

`ovos-tts-server` mounts each vendor API under its own prefix. The voice and the language come from the OVOS plugin. The server accepts vendor model names and voice names, and the plugin speaks with its own voice.

## User stories

The recipes ran against `ovos-tts-server --engine ovos-tts-plugin-espeakng`. The audio comes from espeak-ng, so the voice and the sample rate change with another plugin.

### I have code for the OpenAI SDK

Set `base_url` to the `/openai/v1` prefix. This recipe used `openai` 3.35.1.

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://localhost:9666/openai/v1")
audio = client.audio.speech.create(model="tts-1", voice="alloy",
                                   input="Hello from OVOS.", response_format="wav")
open("hello.wav", "wb").write(audio.content)
```

```text
WAV 22050 Hz, 1 ch, 1.28 s
```

The default `response_format` is `mp3`, as in the OpenAI API. `client.audio.speech.with_streaming_response.create(...)` also works. An empty `input` gets a 422 error, as the OpenAI API gives.

### I have an OVOS device that uses the MaryTTS plugin

`ovos-tts-plugin-marytts` reads the voices from `/voices` and then calls `/process`. Set `voice` to `default`, which is the voice that the OVOS server lists when its plugin has no named voices.

```json
{
  "tts": {
    "module": "ovos-tts-plugin-marytts",
    "ovos-tts-plugin-marytts": {"url": "http://localhost:9666/marytts", "voice": "default"}
  }
}
```

The plugin was driven with the language tags that OVOS passes:

```text
OK   | en-US | 1.39 s at 22050 Hz
OK   | en-GB | 1.41 s at 22050 Hz
OK   | de-DE | 1.58 s at 22050 Hz
```

Without `voice`, the plugin asks for `cmu-slt-hsmm`, a voice of the upstream MaryTTS server, and refuses to speak.

### I have a client that speaks the MaryTTS HTTP protocol

Send `LOCALE` as a Java locale, as MaryTTS clients do. `GET /marytts/locales` and `GET /marytts/voices` list the plugin languages as Java locales, as an upstream MaryTTS 5.2 server does.

```bash
curl -G http://localhost:9666/marytts/process \
  --data-urlencode "INPUT_TEXT=hello world" --data-urlencode "LOCALE=en_US" -o out.wav
curl http://localhost:9666/marytts/voices | head -1
```

```text
default en_US m ovos-tts-plugin-espeakng
```

### I have code for the ElevenLabs SDK

Set `base_url` to the `/elevenlabs` prefix. This recipe used `elevenlabs` 2.73.1.

```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="unused", base_url="http://localhost:9666/elevenlabs")
print([v.voice_id for v in client.voices.get_all().voices])
audio = b"".join(client.text_to_speech.convert(voice_id="default", model_id="x",
                                               text="Hello from ElevenLabs API."))
open("hello.mp3", "wb").write(audio)
```

```text
['default']
mp3, 1.99 s
```

### I have code for Amazon Polly through boto3

Set `endpoint_url` to the `/amazon-polly` prefix. Any credentials work. This recipe used `boto3` 1.43.115.

```python
import boto3

polly = boto3.client("polly", endpoint_url="http://localhost:9666/amazon-polly",
                     region_name="us-east-1", aws_access_key_id="x", aws_secret_access_key="x")
print([v["Id"] for v in polly.describe_voices()["Voices"]])
speech = polly.synthesize_speech(Text="Hello from Polly API.", OutputFormat="mp3", VoiceId="Joanna")
open("hello.mp3", "wb").write(speech["AudioStream"].read())
```

```text
['default']
mp3, 1.64 s
```

## Endpoint status

| Vendor | Client | Status |
| :--- | :--- | :--- |
| OpenAI | `openai` SDK `audio.speech`, plain and streaming | Works |
| MaryTTS | `ovos-tts-plugin-marytts`, raw HTTP | Works |
| ElevenLabs | `elevenlabs` SDK 2: `voices.get_all`, `text_to_speech.convert` | Works |
| ElevenLabs | `elevenlabs` SDK 3, voice list | Fails. SDK 3 lists voices with `GET /v2/voices`, and the server does not serve that path |
| Amazon Polly | `boto3` `describe_voices`, `synthesize_speech` | Works |

[Server Compatibility Layers](server-compat-layers.md) lists the other TTS prefixes.

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| MP3 output is WAV | The server has no MP3 encoder | Install the `audio` extra of `ovos-tts-server` and `ffmpeg` |
| The MaryTTS plugin says `unsupported voice 'cmu-slt-hsmm'` | `voice` is not set | Set `"voice": "default"` |
| A MaryTTS request gets 500 | The plugin cannot speak that locale | Use a locale from `GET /marytts/locales` |

---
**Read next:** [Speech-to-text vendor APIs](vendor-api-stt.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [TTS Server](tts-server.md) · [Server Compatibility Layers](server-compat-layers.md)
