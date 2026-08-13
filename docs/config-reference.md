# Configuration Reference

!!! abstract "In a nutshell"
    This is the settings catalog for OVOS: a lookup table of the main options you can adjust (your language, units, microphone, wake word, and which speech and voice engines to use), with each option's default value and a short note on what it does. You don't need to set most of them. Use this page when you want to find the name of a particular setting and what it controls. For how to apply these settings, see [Configuration Management](config.md). For unfamiliar terms, see the [Glossary](glossary.md).

OVOS uses a layered configuration system, typically stored in `mycroft.conf`.

---

## 1. Core Settings

| Key | Default | Description |
|---|---|---|
| `lang` | `"en-US"` | Primary BCP-47 language code for STT and TTS. |
| `secondary_langs` | `[]` | Extra languages whose resource files are loaded. Intents are only matched when the utterance is tagged with that lang at STT. |
| `system_unit` | `"metric"` | Measurement units (`metric` or `imperial`). |
| `temperature_unit`| `"celsius"`| Temperature units (`celsius` or `fahrenheit`). |
| `date_format` | `"MDY"` | Date format for display and parsing. |
| `time_format` | `"half"` | Clock format for display (`half` = 12-hour, `full` = 24-hour). |
| `confirm_listening`| `true` | Play a beep when the system starts listening. |

---

## 2. Intent Pipeline

The `intents.pipeline` defines the order in which matchers are evaluated.

!!! note "This orders matchers. It does not control which pipeline plugins load"
    Every installed pipeline plugin is loaded and initialized regardless of whether it's
    listed here. `intents.pipeline` only decides the order candidates are tried in, and
    filters which of the loaded ones actually get a turn. To stop a pipeline plugin from
    running at all, including any background work it does on load such as downloading a
    model, uninstall its package. Leaving it installed but absent from this list may still
    let it initialize.

```jsonc
"intents": {
  "pipeline": [
    "ovos-stop-pipeline-plugin-high",
    "ovos-converse-pipeline-plugin",
    "ovos-ocp-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-high",
    "ovos-m2v-pipeline-high",
    "ovos-ocp-pipeline-plugin-medium",
    "ovos-fallback-pipeline-plugin-high",
    "ovos-stop-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-fallback-pipeline-plugin-medium",
    "ovos-fallback-pipeline-plugin-low"
  ]
}

```

### Adapt Settings

- `conf_high`: 0.65


- `conf_med`: 0.45


- `conf_low`: 0.25

### Padatious Settings

- `stem`: `false` (Use snowball stemmer)


- `cast_to_ascii`: `false` (Normalize to ASCII)

---

## 3. Listener & Microphone

All of these live under the top-level `listener` key:

| Key | Default | Description |
|---|---|---|
| `listener.sample_rate` | `16000` | Audio sampling rate in Hz. |
| `listener.fake_barge_in` | `true` | Mute output during recording. |
| `listener.recording_timeout`| `10.0` | Max seconds for a single recording. |
| `listener.remove_silence` | `true` | Strip leading/trailing silence before sending audio to STT. |
| `listener.wake_word` | `"hey_mycroft"` | Default wake word (matches an entry under `hotwords`). |

### Microphone Plugin

The microphone plugin is nested under `listener.microphone`:

```jsonc
"listener": {
  "microphone": {
    "module": "ovos-microphone-plugin-alsa"
  }
}

```

---

## 4. Speech Activity (VAD)

The timing thresholds that `ovos-dinkum-listener` reads to decide when a command
starts and ends are top-level `listener` keys, not nested under `VAD`:

| Key | Default | Description |
|---|---|---|
| `listener.speech_begin` | `0.3` | Seconds of detected speech before a command is considered started. |
| `listener.silence_end` | `0.7` | Seconds of silence before a command is considered ended. |

The shipped config also carries a `listener.VAD` block (`silence_method`, `speech_seconds`,
`silence_seconds`, plus a per-VAD-plugin `module`/fallback chain such as
`ovos-vad-plugin-silero` → `ovos-vad-plugin-precise` → `ovos-vad-plugin-webrtcvad` →
`ovos-vad-plugin-noise`). This block selects and configures the [VAD plugin](vad-plugins.md)
itself, a separate concern from the `speech_begin`/`silence_end` timing above.

!!! tip "Which one do I edit?"
    To change when a command is considered to start or end, touch the two `listener.*` keys
    above. To change which [VAD plugin](vad-plugins.md) does that detection, or its
    plugin-specific thresholds, touch the generated `listener.VAD.*` block below instead.
    It's a different config subtree from the same-named `listener.VAD` section title.

---

## 5. Plugin Selection

### STT (Speech-to-Text)

```jsonc
"stt": {
  "module": "ovos-stt-plugin-server",
  "fallback_module": ""
}

```

### TTS (Text-to-Speech)

```jsonc
"tts": {
  "module": "ovos-tts-plugin-server",
  "ovos-tts-plugin-mimic": {
    "voice": "ap"
  }
}

```

---

## 6. messagebus (Websocket)

| Key | Default | Description |
|---|---|---|
| `host` | `"127.0.0.1"` | Host for the core messagebus. |
| `port` | `8181` | Port for the core messagebus. |
| `shared_connection`| `true` | If true, all skills share one websocket. |

---

## 7. Logging

```jsonc
"logging": {
  "log_level": "DEBUG",
  "logs": {
    "path": "/opt/ovos/logs/",
    "max_bytes": 50000000,
    "backup_count": 6
  },
  "audio": {
    "log_level": "INFO",
    "logs": { "path": "/var/log/ovos/" }
  }
}
```

| Key | Default | Description |
|---|---|---|
| `logging.log_level` | `"INFO"` | Global log level. |
| `logging.logs.path` | `"stdout"` | Log directory. Set to `"stdout"` to log to console only. |
| `logging.logs.max_bytes` | `50000000` | Max log file size, in bytes, before rotation. |
| `logging.logs.backup_count` | `3` | Number of rotated log files to keep. |
| `logging.<service_name>` | (none) | A section named after a service (for example `logging.audio`) overrides the global `log_level` and `logs` settings for that service only. |

---

## 8. GUI

The `gui` key controls the on-screen interface. The `gui_websocket` key controls the separate socket that GUI clients connect to.

| Key | Default | Description |
|---|---|---|
| `gui.idle_display_skill` | `"ovos-skill-homescreen.openvoiceos"` | Skill ID of the homescreen shown when no skill is active. |
| `gui.extension` | `"generic"` | GUI platform extension. Enclosures can set a different one for their own screen. |
| `gui.generic.homescreen_supported` | `true` | Whether the `generic` extension shows a homescreen. |
| `gui.disable_gui` | `false` | On a headless device, set to `true` to stop all GUI bus messages. |
| `gui_websocket.host` | `"127.0.0.1"` | Host the GUI websocket binds to. Loopback-only by default, matching the core bus. Widen to `0.0.0.0` only when a display client runs on another machine. See [Bus Service](bus-service.md) for network-exposure guidance. |
| `gui_websocket.base_port` | `18181` | Base port for the GUI websocket. Each connected GUI client gets its own port from this point up. |
| `gui_websocket.route` | `"/gui"` | URL route for the GUI websocket. |
| `gui_websocket.ssl` | `false` | Enable TLS on the GUI websocket. |

!!! warning "Widening `gui_websocket.host` exposes an unauthenticated socket"
    The GUI websocket is unauthenticated. Setting `gui_websocket.host` to `"0.0.0.0"`
    (needed for a remote display) makes it reachable by any device on the network unless
    you firewall the port. Configs written before the loopback default may still carry
    `"0.0.0.0"` — check after upgrades.

Source: `mycroft.conf` lines 356 to 361 (`gui_websocket`) and lines 609 to 627 (`gui`) in [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).

---

## 9. PHAL (Hardware Abstraction Layer)

PHAL plugins read their settings from the top-level `PHAL` key, and PHAL admin plugins from `PHAL.admin`. Neither key has a default block in the shipped `mycroft.conf`. With no `PHAL` key present, every PHAL plugin loads with an empty config and its own internal defaults.

```jsonc
"PHAL": {
  "some-phal-plugin-id": {
    "enabled": true
  },
  "admin": {
    "some-admin-plugin-id": {
      "enabled": true
    }
  }
}
```

A PHAL plugin is disabled by setting `"enabled": false` under its plugin ID. Admin plugins run with elevated privileges and are read from a nested `admin` block, not the top level.

Source: `Configuration().get("PHAL")` in `ovos_PHAL/service.py` line 60 and the `PHAL.admin` docstring in `ovos_PHAL/admin.py` lines 32 to 46, [OpenVoiceOS/ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL). No `PHAL` block appears in the shipped `mycroft.conf`.

---

## 10. OCP / Media

The OCP intent pipeline plugin reads its config from `intents.ovos-ocp-pipeline-plugin`
(the plugin ID). `intents.OCP` survives only as a back-compat fallback that is shadowed
whenever the plugin-ID key exists — and the shipped `mycroft.conf` always ships it, so on a
stock install keys placed under `intents.OCP` change nothing (see
[OCP Pipeline](ocp-pipeline.md#configuration)). `Audio` selects the legacy audio service backend, which OCP still uses for actual playback.

| Key | Default | Description |
|---|---|---|
| `intents.ovos-ocp-pipeline-plugin.legacy` | `false` | Force the old audio-service bus API instead of OCP. |
| `intents.ovos-ocp-pipeline-plugin.min_score` | `40` | Minimum confidence score, 0-100, for OCP to accept an utterance as a media request. |
| `intents.ovos-ocp-pipeline-plugin.filter_media` | `true` | Filter out results OCP judges not to be playable media. |
| `intents.ovos-ocp-pipeline-plugin.filter_SEI` | `true` | Filter results by Search Engine Index compatibility. |
| `intents.ovos-ocp-pipeline-plugin.playback_mode` | `0` | Playback mode passed to the audio backend. |
| `intents.ovos-ocp-pipeline-plugin.search_fallback` | `true` | Fall back to a general media search when no skill claims the request. |

```jsonc
"Audio": {
  "native_sources": ["debug_cli", "audio", "mycroft-gui"],
  "default-backend": "mpv",
  "backends": {
    "OCP": {
      "type": "ovos_common_play",
      "preferred_audio_services": ["mpv", "vlc", "simple"],
      "active": true
    }
  }
}
```

| Key | Default | Description |
|---|---|---|
| `Audio.default-backend` | `"mpv"` | Audio backend used for playback. |
| `Audio.backends.OCP.type` | `"ovos_common_play"` | Backend type for the OCP entry. Do not set this to the string `"OCP"`. That name is only valid as the key under `backends`. |
| `Audio.backends.OCP.preferred_audio_services` | `["mpv", "vlc", "simple"]` | Order in which OCP tries local media players. |
| `Audio.backends.OCP.active` | `true` | Whether the OCP backend is available for selection. |

Source: `mycroft.conf` lines 188 to 203 (`intents.ovos-ocp-pipeline-plugin`) and lines 705 to 726 (`Audio`) in [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).

---

## 11. Skills

All of these live under the top-level `skills` key.

| Key | Default | Description |
|---|---|---|
| `skills.blacklisted_skills` | `["skill-ovos-stop.openvoiceos"]` | Skill IDs that never load, even if installed. The stop skill is blacklisted because stop handling is now built into core. |
| `skills.fallbacks.fallback_mode` | `"accept_all"` | Which skills may act as a fallback handler: `accept_all`, `whitelist`, or `blacklist`. |
| `skills.fallbacks.fallback_whitelist` | `[]` | Skill IDs allowed as fallback handlers when `fallback_mode` is `whitelist`. |
| `skills.fallbacks.fallback_blacklist` | `[]` | Skill IDs excluded from fallback handling when `fallback_mode` is `blacklist`. |
| `skills.fallbacks.fallback_priorities` | `{}` | Per-skill-ID override of a skill's own default fallback priority. |
| `skills.converse.timeout` | `300` | Seconds a skill stays active for converse before it is deactivated, if the user does not interact with it. |
| `skills.converse.converse_mode` | `"accept_all"` | Which skills may take part in converse: `accept_all`, `whitelist`, or `blacklist`. |
| `skills.converse.converse_whitelist` | `[]` | Skill IDs allowed to converse when `converse_mode` is `whitelist`. |
| `skills.converse.converse_blacklist` | `[]` | Skill IDs excluded from converse when `converse_mode` is `blacklist`. |
| `skills.converse.converse_activation` | `"accept_all"` | How a skill may activate itself: `accept_all`, `priority`, `whitelist`, or `blacklist`. |
| `skills.converse.max_activations` | `-1` | Times per minute a skill may self-activate. `-1` means no limit. `0` disables self-activation. |
| `skills.converse.cross_activation` | `true` | If `true`, any skill may activate any other skill, not only itself. |
| `skills.converse.cross_deactivation` | `true` | If `true`, any skill may deactivate any other skill, not only itself. |

Source: `mycroft.conf` lines 235 to 304 (`skills`) in [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).

---

## 12. Session

| Key | Default | Description |
|---|---|---|
| `session.ttl` | `-1` | Time to live, in seconds, for a remote session. `-1` means sessions do not expire. |

Source: `mycroft.conf` lines 643 to 646 (`session`) in [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).

---

## 13. Personas / Agents

The shipped `mycroft.conf` has no `persona` key and no default persona values. Persona and LLM-agent settings are read from the persona service's own config file, not from `mycroft.conf`. See [Personas](personas.md) for that service's settings and file location.

---

## All Keys

The curated sections above cover the settings you're most likely to touch. `mycroft.conf`
has many more keys than that, most of them defaults you never need to change.

**See [All Configuration Keys](config-all-keys.md) for the full, auto-generated table of
every key in the shipped `mycroft.conf`, with defaults and descriptions where available.**

---
**Read next:** [All Configuration Keys](config-all-keys.md) · [Locations](locations-ref.md) · [Configuration Overview](config.md)
**Related:** [Bus Events Reference](bus-events.md) · [Intent Service](intent-service.md) · [Audio Service](audio-service.md)
