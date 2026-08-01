# Wyoming Wake-word Bridge

!!! abstract "In a nutshell"
    `wyoming-ovos-wakeword` is one of the three [Wyoming Bridges](wyoming-bridges.md): it exposes
    any installed OVOS wake-word plugin as a Wyoming wake-word detection server, so Home
    Assistant and other Wyoming clients can use an OVOS hotword without knowing anything about
    the OVOS plugin system. See [Wyoming Bridges](wyoming-bridges.md) for the STT and TTS
    bridges and the shared background on the Wyoming protocol.

## Wake-word Bridge (`wyoming-ovos-wakeword`)

Exposes any OVOS wake-word plugin as a Wyoming wake-word detection server.
Supports **multiple simultaneous wake-word models** loaded on demand per client session.

### Architecture

```text
Wyoming client                   wyoming-ovos-wakeword              OVOS plugin layer
(Home Assistant,           ┌────────────────────────────────┐
 rhasspy, etc.)            │  AsyncServer (wyoming lib)      │
                           │                                │
 Describe    ─────────────►  OVOSWakeWordEventHandler        │
 Info        ◄─────────────   ._get_info()                  │
                           │                                │
 Detect([names]) ─────────►   .active_detectors = names     │
                           │   .load_wakewords(names) ──────►  OVOSWakeWordFactory
                           │                                │  .create_hotword(name, cfg)
 AudioStart  ─────────────►   reset all active models       │
 AudioChunk* ─────────────►   HotWordEngine.update(chunk)   │
                           │   HotWordEngine.found_wake_word()│
 Detection   ◄─────────────   (if detected)                 │
 AudioStop   ─────────────►   (if no detection)             │
 NotDetected ◄─────────────   send NotDetected               │
                           └────────────────────────────────┘
```

**`OVOSWakeWordEventHandler`**

One instance per client connection. Maintains a dict of loaded `HotWordEngine` instances,
keyed by wake-word name (lazy-loaded on first use). The connection is persistent. The
handler keeps running (`return True`) for continuous detection.

| Event type | Action |
|---|---|
| `Describe` | Send `Info` with all configured hotwords from `mycroft.conf["hotwords"]` |
| `Detect` | Update `active_detectors`, lazy-load requested models |
| `AudioStart` | Reset `_detection = False`, call `model.reset()` on all active models |
| `AudioChunk` | Convert audio, feed to each active `HotWordEngine.update()`, check `found_wake_word()`, send `Detection` if triggered |
| `AudioStop` | If no detection occurred, send `NotDetected` |

### Lazy model loading

Models are loaded the first time they are requested. Once loaded, they are cached for
the lifetime of the connection. All hotwords in `mycroft.conf["hotwords"]` are available.
Clients select which to activate with the `Detect` event.

### Running

```bash
pip install wyoming-ovos-wakeword
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--uri` | No | `stdio://` | `tcp://HOST:PORT` or `unix:///path/to/socket` |
| `--zeroconf` | No | disabled | Enable mDNS/zeroconf service discovery (optional: service name) |
| `--debug` | No | `False` | Enable DEBUG log level |
| `--log-format` | No | `BASIC_FORMAT` | Format string for log messages |

Examples:

```bash

# Standard TCP server
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893

# With zeroconf mDNS discovery (default service name)
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893 --zeroconf

# With custom zeroconf service name
wyoming-ovos-wakeword --uri tcp://0.0.0.0:7893 --zeroconf my-ovos-wakeword
```

> Zeroconf requires a `tcp://` URI.

### Configuration

Configuration is read entirely from `mycroft.conf`:

- `mycroft.conf["listener"]["wake_word"]`: default active wake-word name (if no `Detect` event is sent)


- `mycroft.conf["hotwords"]`: dict of all configured hotword definitions

```json
{
  "listener": {
    "wake_word": "hey_mycroft"
  },
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite",
      "expected_duration": 3,
      "trigger_level": 3,
      "sensitivity": 0.5,
      "listen": true
    },
    "hey_mycroft_vosk": {
      "module": "ovos-ww-plugin-vosk",
      "samples": ["hey mycroft"],
      "rule": "fuzzy",
      "listen": true
    },
    "wake_up": {
      "module": "ovos-ww-plugin-vosk",
      "rule": "fuzzy",
      "samples": ["wake up"],
      "lang": "en-US",
      "wakeup": true
    }
  }
}
```

All configured hotwords are advertised via `Describe`/`Info` and are selectable by name.

### Wyoming message flow

```text
Client → Describe
Server → Info(wake=[WakeProgram(models=[WakeModel(name="hey_mycroft", phrase="Hey Mycroft"), ...])])

Client → Detect(names=["hey_mycroft"])
Client → AudioStart(rate=16000, width=2, channels=1)
       → AudioChunk (raw PCM bytes)
       → AudioChunk ...
       → AudioStop
Server → Detection(name="hey_mycroft")   ← if detected

       | NotDetected                      ← if not detected
```

### Zeroconf / mDNS Discovery

When `--zeroconf` is passed, the bridge calls
`wyoming.zeroconf.register_server(name, port, host)` to announce itself on the local
network. Home Assistant and other Wyoming clients can discover the service automatically
without manual IP configuration.

---
**Read next:** [Wyoming Bridges](wyoming-bridges.md)
**Related:** [Wake-word Plugins](wake-word-plugins.md) · [Home Assistant](home-assistant.md) · [Plugin Manager](plugin-manager.md)
