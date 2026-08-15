# Wyoming Bridges

!!! abstract "In a nutshell"
    "Wyoming" is a common language (a network protocol) that voice gadgets use to talk to each other. Home Assistant's voice features are the best-known example. These bridges are small adapter programs that let OVOS's own engines speak that common language. Home Assistant and similar tools can then use an OVOS wake word, speech-to-text, or text-to-speech engine without knowing anything about OVOS. Think of them as translators that let OVOS plug into the wider voice-assistant world. See [STT plugins](stt-plugins.md), [TTS plugins](tts-plugins.md), and the [Glossary](glossary.md).

[Wyoming](https://github.com/rhasspy/wyoming) is a simple TCP-based peer-to-peer protocol
for voice assistant components, originally developed for Home Assistant's voice pipeline.
It defines a small set of typed events that flow over a socket connection, covering the
three main voice pipeline stages: wake-word detection, speech-to-text, and text-to-speech.

OVOS provides three Wyoming bridge packages that expose any installed OVOS plugin as a
Wyoming-compatible server. This allows Home Assistant, Rhasspy, and other Wyoming clients
to use OVOS engines without knowing anything about the OVOS plugin system.

| Bridge | Package | Example port | OPM plugin group loaded |
|---|---|---|---|
| `wyoming-ovos-stt` | `wyoming-ovos-stt` | 7891 | `opm.stt` |
| `wyoming-ovos-tts` | `wyoming-ovos-tts` | 7892 | `opm.tts` |
| `wyoming-ovos-wakeword` | `wyoming-ovos-wakeword` | 7893 | `opm.wake_word` |

!!! warning "The ports are conventions, not built-in defaults"
    You set the port with the `--uri` flag. The values above are the conventional ports used
    in this manual's examples (the upstream READMEs use overlapping values). `wyoming-ovos-stt`
    **requires** `--uri`; `wyoming-ovos-tts` and `wyoming-ovos-wakeword` default to `stdio://`,
    which Home Assistant cannot reach — pass a `tcp://` URI for HA use.

These three are standalone Wyoming **servers** (console-script entry points), not
OVOS plugins themselves. Each loads an installed OVOS plugin from the matching OPM
entry-point group and re-exposes it over the Wyoming protocol.

All three bridges:

- Are installed via `pip install <package-name>`


- Read plugin configuration from `mycroft.conf` (standard OVOS config file)


- Run as standalone async Wyoming servers (TCP, Unix socket, or stdio) using the `wyoming` library

---

## STT Bridge (`wyoming-ovos-stt`)

Exposes any OVOS STT plugin as a Wyoming ASR server.

### Architecture

```text
Wyoming client                    wyoming-ovos-stt                 OVOS plugin layer
(Home Assistant,           ┌─────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)   │
                           │                             │
 AudioChunk* ─────────────►  STTAPIEventHandler          │
 AudioStop   ─────────────►    .handle_audio_chunk()     │
 Transcript  ◄─────────────    .handle_stt()  ──────────►  STT.execute(AudioData)
                           │    .handle_audio_end()       │  (OVOSSTTFactory)
 Describe    ─────────────►    → write Info event         │
                           └─────────────────────────────┘
```

**`STTAPIEventHandler`** (`wyoming_ovos_stt/handler.py`)

One instance per client connection. Accumulates incoming audio chunks (converted to
16 kHz / 16-bit / mono via `AudioChunkConverter`), then on `AudioStop` calls
`STT.execute(AudioData)` and sends a `Transcript` event.

| Event type | Action |
|---|---|
| `AudioChunk` | Convert to 16 kHz/16-bit/mono, append to `self.audio` |
| `AudioStop` | Call `STT.execute()`, send `Transcript`, reset accumulator |
| `Transcribe` | Acknowledge (no-op). Signals start of a new request |
| `Describe` | Send `Info` advertising the loaded plugin as an ASR model |

Plugin loading happens once at startup. The plugin instance is shared across all connections.

### Running

```bash
pip install wyoming-ovos-stt
wyoming-ovos-stt --plugin-name <ovos-stt-plugin-name> --uri tcp://0.0.0.0:7891
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--plugin-name` | Yes | (none) | OVOS STT plugin module name (e.g. `ovos-stt-plugin-whisper`) |
| `--uri` | Yes | (none) | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--debug` | No | `False` | Enable DEBUG log level |
| `--log-format` | No | `BASIC_FORMAT` | Format string for log messages |
| `--version` | No | (none) | Print version and exit |

Examples:

```bash

# Whisper locally (no audio leaves the machine)
wyoming-ovos-stt --uri tcp://0.0.0.0:7891 --plugin-name ovos-stt-plugin-whisper

# Unix socket
wyoming-ovos-stt --uri unix:///run/wyoming-stt.sock --plugin-name ovos-stt-plugin-vosk

# Proxy to a server plugin — set "urls" to YOUR OWN stt-server (see stt-server.md);
# leaving "urls" unset falls back to public community servers
wyoming-ovos-stt --uri tcp://0.0.0.0:7891 --plugin-name ovos-stt-plugin-server
```

### Configuration

Plugin configuration is read from `mycroft.conf["stt"][<plugin-name>]`.
Language is taken from `cfg["lang"]` if present, otherwise from `mycroft.conf["lang"]`.

```json
{
  "lang": "en-US",
  "stt": {
    "ovos-stt-plugin-server": {
      "urls": ["http://localhost:8080/stt"]
    },
    "ovos-stt-plugin-whisper": {
      "model": "base"
    }
  }
}
```

!!! warning "`ovos-stt-plugin-server` without `urls` uses public servers"
    As on the [STT server](stt-server.md) page: if you don't set `urls`, this plugin falls back
    to public community-run STT servers rather than failing. Set `urls` to your own
    [stt-server](stt-server.md) instance for anything other than a quick test.

--8<-- "snippets/community-servers.md"

### Wyoming message flow

```text
Client → AudioChunk (rate=16000, width=2, channels=1, PCM bytes)
       → AudioChunk ...
       → AudioStop
Server → Transcript (text="hello world")

Client → Describe
Server → Info(asr=[AsrProgram(name=plugin_name, models=[AsrModel(...)])])
```

Audio must be 16 kHz / 16-bit / mono PCM. The bridge converts incoming audio automatically.

---

## TTS Bridge (`wyoming-ovos-tts`)

Exposes any OVOS TTS plugin as a Wyoming TTS server.

### Architecture

```text
Wyoming client                    wyoming-ovos-tts                  OVOS plugin layer
(Home Assistant,           ┌──────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)    │
                           │                              │
 Describe    ─────────────►  OVOSTTSEventHandler           │
 Info        ◄─────────────   .handle_event()             │
                           │                              │
 Synthesize  ─────────────►   .handle_synth()  ───────────►  TTS.synth(text)
 AudioStart  ◄─────────────   wav_to_chunks()             │  (OVOSTTSFactory)
 AudioChunk* ◄─────────────                               │
 AudioStop   ◄─────────────                               │
                           └──────────────────────────────┘
```

**`OVOSTTSEventHandler`**

One instance per client connection. On `Synthesize`, calls `TTS.synth(text)` which returns
a path to a WAV file. The WAV is split into fixed 1024-sample chunks and streamed
back as `AudioStart` + `AudioChunk`* + `AudioStop`.

| Event type | Action |
|---|---|
| `Describe` | Send `Info` advertising the loaded plugin as a TTS voice |
| `Synthesize` | Call the plugin's synth, then stream the WAV back as `AudioChunk`s (1024 samples per chunk, fixed) |

!!! note "Whole-utterance synthesis only"
    `wyoming-ovos-tts` handles the plain `Synthesize` event only: the full text is
    synthesized in one call and the resulting WAV is chunked back over the wire.
    Wyoming's streaming-synthesis protocol
    (`SynthesizeStart`/`SynthesizeChunk`/`SynthesizeStop`) is not implemented.

### Running

```bash
pip install wyoming-ovos-tts
wyoming-ovos-tts --plugin-name <ovos-tts-plugin-name> --uri tcp://0.0.0.0:7892
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--plugin-name` | Yes | (none) | OVOS TTS plugin module name (e.g. `ovos-tts-plugin-piper`) |
| `--uri` | No | `stdio://` | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--debug` | No | `False` | Enable DEBUG log level |

Examples:

```bash

# Piper locally (no text leaves the machine)
wyoming-ovos-tts --uri tcp://0.0.0.0:7892 --plugin-name ovos-tts-plugin-piper

# Unix socket
wyoming-ovos-tts --uri unix:///run/wyoming-tts.sock --plugin-name ovos-tts-plugin-espeak

# Proxy to a server plugin — set "host" to YOUR OWN tts-server (see tts-server.md);
# leaving "host" unset falls back to public community servers
wyoming-ovos-tts --uri tcp://0.0.0.0:7892 --plugin-name ovos-tts-plugin-server
```

### Configuration

Plugin configuration is read from `mycroft.conf["tts"][<plugin-name>]`.

```json
{
  "lang": "en-US",
  "tts": {
    "ovos-tts-plugin-server": {
      "host": "http://localhost:9666"
    },
    "ovos-tts-plugin-piper": {
      "voice": "en_US-lessac-medium"
    }
  }
}
```

!!! warning "`ovos-tts-plugin-server` without `host` uses public servers"
    As on the [TTS server](tts-server.md) page: if you don't set `host`, this plugin falls back
    to public community-run TTS servers rather than failing. Set `host` to your own
    [tts-server](tts-server.md) instance for anything other than a quick test.

--8<-- "snippets/community-servers.md"

### Wyoming message flow

```text
Client → Synthesize(text="Hello world", voice=VoiceSettings(...))
Server → AudioStart(rate=22050, width=2, channels=1)
       → AudioChunk (1024 samples)
       → AudioChunk ...
       → AudioStop

Client → Describe
Server → Info(tts=[TtsProgram(name=plugin_name, voices=[TtsVoice(...)])])
```

---

## Wake-word Bridge (`wyoming-ovos-wakeword`)

Exposes any OVOS wake-word plugin as a Wyoming wake-word detection server, supporting
**multiple simultaneous wake-word models** loaded on demand per client session. Its full
architecture, running instructions, configuration and message-flow reference now live on
their own page: [Wyoming Wake-word Bridge](wyoming-wakeword-bridge.md).

---

## On the Home Assistant side

Once a bridge is running with a `tcp://` URI, register it in Home Assistant through the
**Wyoming Protocol** integration: **Settings → Devices & Services → Add Integration**, search
for "Wyoming Protocol", and enter the bridge machine's host and the port from your `--uri`.
Repeat once per bridge (STT, TTS, and wake word are three separate Wyoming services). The new
entities then become selectable in **Settings → Voice assistants** when building an Assist
pipeline. For the HA side in more depth, see the
[Home Assistant Wyoming integration docs](https://www.home-assistant.io/integrations/wyoming/).

## Keeping the bridges running

The commands on this page run in the foreground and die with the terminal. For a permanent
setup, wrap each bridge in a systemd unit (or your init system's equivalent) so it starts on
boot and restarts on failure — the same pattern [Production Operations](production-operations.md)
uses for the OVOS services themselves.

## OVOS Plugin Types Used

| Bridge | Entry point group | Base class | Factory |
|---|---|---|---|
| STT | `opm.stt` | `ovos_plugin_manager.templates.stt.STT` | `OVOSSTTFactory` |
| TTS | `opm.tts` | `ovos_plugin_manager.templates.tts.TTS` | `OVOSTTSFactory` |
| Wake word | `opm.wake_word` | `ovos_plugin_manager.templates.hotwords.HotWordEngine` | `OVOSWakeWordFactory` |

All three bridges use `OVOSSTTFactory` / `OVOSTTSFactory` / `OVOSWakeWordFactory` from
`ovos-plugin-manager` for plugin discovery and instantiation. See
[Plugin Manager](plugin-manager.md) for the plugin packaging reference.

---
**Read next:** [Plugins Index & Overview](plugins-index.md)
**Related:** [Wyoming Wake-word Bridge](wyoming-wakeword-bridge.md) · [Home Assistant](home-assistant.md) · [STT Server](stt-server.md) · [TTS Server](tts-server.md) · [STT Plugins](stt-plugins.md)
