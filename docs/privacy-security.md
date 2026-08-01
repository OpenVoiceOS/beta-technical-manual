# Privacy & Security

!!! abstract "In a nutshell"
    OVOS is designed to run locally and without a cloud account, but a **default
    install still talks to the network** for speech recognition and speech
    synthesis unless you change the plugins, and the [messagebus](bus-service.md)
    that skills use to talk to each other has **no authentication**. Anything
    that can reach it, or any skill you install, has full control of the
    assistant. This page inventories what a stock install actually sends over
    the network, who you're trusting when you install a skill, and how to
    lock things down. See the [Glossary](glossary.md) for unfamiliar terms.

This page describes the **`ovos` profile installed by the [`ovos-installer`](ovos-installer.md)
with its bundled defaults**, the most common path. Anything below can be
changed by picking different plugins or a different [profile](composable-deployments.md),
so where behavior depends on a choice you made, this page says so instead of
guessing.

None of this is unusual for a local-only Linux service. The trust model below is the same
one any local daemon or dev server has. It mostly starts to matter once you expose a port
to a network you don't control, or install a skill whose source you haven't vetted.

---

## Network surface of a default install

| What | Default behavior | Offline? |
| --- | --- | --- |
| Speech-to-text (STT) | `ovos-stt-plugin-server`, which by default talks to a **public whisper server** run by the OVOS community | **No**, your voice audio leaves the device |
| Text-to-speech (TTS) | `ovos-tts-plugin-server`, which by default talks to a **public Piper server** (the "Alan Pope" voice) | **No**, the text you want spoken leaves the device |
| Translation / language detection | `language.translation_module` defaults to `ovos-translate-plugin-server` and `language.detection_module` to `ovos-lang-detector-plugin-server`, both pointed at **public servers** run by the OVOS community. The declared fallbacks are `ovos-google-translate-plugin` / `ovos-google-lang-detector-plugin` | **No**. Text to be translated or language-detected leaves the device. Self-host [ovos-translate-server](https://github.com/OpenVoiceOS/ovos-translate-server) and point the plugins at it, or pick an offline plugin |
| LLM / persona solvers | Not configured by default, but as soon as an LLM-backed solver or persona plugin is configured (e.g. an OpenAI-compatible `llm.module`), the user's query and/or conversation text is sent to whichever third-party cloud LLM provider that plugin points at. This includes the pre-built `Remote Llama` demo persona shipped with [`ovos-openai-plugin`](openai-plugin.md), which is pointed at a public ollama/LLama server by default | Depends on the plugin. See the [LLM transformers](llm-transformers.md), [personas](personas.md) and [OpenAI plugin](openai-plugin.md) pages for offline vs. cloud options |
| Wake word | `ovos-ww-plugin-precise-onnx` (or `precise-lite`), running fully on-device | **Yes**, once the model file is downloaded on first run |
| Connectivity checks | `network_tests` polls `https://api.ipify.org`, `1.1.1.1`, `8.8.8.8`, `http://nmcheck.gnome.org/check_network_status.txt` and `https://checkonline.home-assistant.io/online.txt` to decide whether the device is online and behind a captive portal | **No**, but every URL is a config key. Point `network_tests` at your own infrastructure |
| Backend / pairing | OVOS is **backendless** by default. There is no backend key in the shipped `mycroft.conf` at all, nothing is paired, and no account exists unless you add one yourself | **Yes** |
| Remote config | OVOS has no remote/backend config layer. Nothing on the network can push settings into your `mycroft.conf` | **Yes** |
| Update checks | The installer does **not** automatically contact a server. You re-run it manually to check for a newer release | **Yes** |
| Install-time telemetry | One-time, opt-in, see below | Depends on your answer |
| Ongoing usage telemetry | Opt-in, continues to run after install, see below | Depends on your answer |

!!! warning "Default STT, TTS and translation send your voice and words to a public server"
    Out of the box, speech recognition, speech synthesis **and** translation /
    language detection are all configured against **public servers operated by
    the OVOS community**, not services running on your device. If you care about
    audio or text never leaving the machine, switch to an offline plugin. See
    [STT plugins](stt-plugins.md) and [TTS plugins](tts-plugins.md) for the
    offline options (for example `onnx-asr`-based STT or `ovos-tts-plugin-piper`
    running locally), or point the server plugins at a server you run yourself
    (see [`stt-server`](stt-server.md) / [`tts-server`](tts-server.md)). The same
    applies to `language.translation_module` and `language.detection_module`:
    either self-host a [translate server](translate-server.md) and configure the
    plugins against it, or choose an offline
    [translation plugin](translation-plugins.md).

--8<-- "snippets/community-servers.md"

### A fully offline stack

Each row above links to its own offline alternative, but assembling all of them into one
working config means cross-referencing four separate catalog pages. Here they are combined
into a single `~/.config/mycroft/mycroft.conf`: offline STT, TTS, VAD, wake word, and
translation/language-detection, all running on-device:

```jsonc
// ~/.config/mycroft/mycroft.conf: fully offline stack
{
  "stt": {
    "module": "ovos-stt-plugin-onnx-asr"
  },
  "tts": {
    "module": "ovos-tts-plugin-phoonnx"
  },
  "listener": {
    "wake_word": "hey_mycroft",
    "VAD": {
      "module": "ovos-vad-plugin-silero"
    }
  },
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-onnx"
    }
  },
  "language": {
    "translation_module": "ovos-translate-plugin-nllb",
    "detection_module": "ovos-lang-detector-fasttext-plugin"
  }
}
```

LLM-backed solvers and personas are not part of this table because they're not configured
by default at all. See [LLM transformers](llm-transformers.md) and [personas](personas.md).
If you do want one, it's still possible to keep the whole stack offline: point it at a
**local** model (for example one served by `llama.cpp` on the same machine) instead of a
cloud provider, so the query and conversation text never leave the device.

!!! tip "depends on selected profile"
    A `server` or `satellite` install ([composable deployments](composable-deployments.md))
    changes which of these components even run on this particular device. The
    table above describes the all-in-one `ovos` profile.

### Point a device at your own LAN servers

If you run your own [STT server](stt-server.md) and [TTS server](tts-server.md) on a
machine on your local network (say `192.168.1.50`), keep your voice and text off the public
internet without giving up the server model. Both companion plugins go in the same
`~/.config/mycroft/mycroft.conf`, but note the client-side config keys differ: the STT
plugin uses `urls` (a list), the TTS plugin uses `host`.

```jsonc
// ~/.config/mycroft/mycroft.conf: LAN speech backend at 192.168.1.50
{
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "urls": ["http://192.168.1.50:8080/stt"]
    }
  },
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
      "host": "http://192.168.1.50:9666"
    }
  }
}
```

After saving the file, restart the client (`ovos-restart` on raspOVOS, or
`systemctl --user restart ovos.service` elsewhere) and check the voice/audio logs to
confirm requests go to `192.168.1.50`, not a public server. See
[production-operations: thin clients + a shared speech backend](production-operations.md#thin-clients-a-shared-speech-backend)
for the server-side Docker Compose setup.

---

## Install-time telemetry vs. ongoing usage telemetry

The installer asks two separate yes/no questions, and they are easy to
conflate because both are about "sharing anonymous data." They are not the
same thing:

- **Install-time telemetry** (`share_telemetry`) is a **one-time** report sent
  when the installer finishes: things like CPU architecture, OS, the chosen
  channel/profile, and which features were enabled. It is sent once, during
  installation, to a metrics endpoint run by the community, and nothing about
  this is ongoing. See the field table on the
  [installer page](ovos-installer.md#anonymous-telemetry) for the exact list.
- **Ongoing usage telemetry** (`share_usage_telemetry`) is different. Saying
  yes here adds an `open_data.intent_urls` entry to your installed
  `mycroft.conf`, which makes the **running assistant** report intent-matching
  data on an ongoing basis, not just during setup. If you want telemetry to
  really stop after installation, decline both prompts, or set both
  `share_telemetry: false` and `share_usage_telemetry: false` if you use a
  [scenario file](ovos-installer.md#non-interactive-scenario-install).

Either way, `country` in the install-time report is derived from a public IP
geolocation lookup performed by the installer at install time (not from any
setting you type in), so it reflects wherever the machine's internet
connection is at that moment.

---

## Opt-in wake-word and STT sample donation

Beyond intent-matching metrics, `ovos-dinkum-listener` can optionally upload the
audio samples it captures (wake-word detections and transcribed utterances) to
an [ovos-opendata-server](https://github.com/OpenVoiceOS/ovos-opendata-server)
instance, so contributors can help improve wake-word and STT plugins with real
recordings. This is exclusively opt-in and off by default: nothing is ever
uploaded unless `open_data.ww_urls` or `open_data.stt_urls` is explicitly
configured with at least one server, and there is no default server. Uploads run
in a background thread and never block the listener. Failures are logged and
otherwise ignored. See [`open_data.ww_urls` / `open_data.stt_urls`](config-reference.md#all-keys-generated) for the exact config keys.

---

## What is written to disk

Separate from what goes over the network, the listener can write captured audio to
local storage. The relevant paths sit under the listener's `save_path`, which defaults
to `~/.local/share/mycroft/listener/`.

| Path | Written when | Config key |
| --- | --- | --- |
| `<save_path>/wake_words/` | Only if `listener.record_wake_words` is enabled | `listener.record_wake_words` (off by default) |
| `<save_path>/utterances/` | Only if `listener.save_utterances` is enabled | `listener.save_utterances` (off by default) |
| `<save_path>/recordings/` | Whenever a recording session runs | none, always written |

Because `record_wake_words` and `save_utterances` are both off by default, ordinary
wake-word detections and spoken commands are **not** written to disk on a stock install.

A **recording session**, the dictation-style listener state a skill enters to capture a
block of audio rather than the normal wake-word-then-command flow, is different. It
writes the captured audio as a `.wav` plus a JSON sidecar of its metadata into
`<save_path>/recordings/`, and this does not depend on the two keys above. Nothing prunes
that directory, so the files stay until you remove them. On shared or multi-user devices,
audit and clear it as part of your routine, and set restrictive permissions on `save_path`.

---

## The messagebus is a trust boundary, not a security boundary

Everything inside OVOS (skills, plugins, the voice pipeline) talks over the
local [messagebus](bus-service.md). As documented there:

!!! danger "The bus has no authentication and no encryption"
    Any process that can open a WebSocket connection to the bus (default
    `127.0.0.1:8181`) has full control of the assistant. It can trigger any
    skill, read everything crossing the bus, and, through plugins that expose
    subprocess or file access, potentially run arbitrary code.

    This is not limited to skill-level mischief. If any
    [AdminPHAL](phal.md#security-model) system plugin is enabled (for example
    `ovos-PHAL-plugin-system`), the same unauthenticated bus can trigger
    reboot, shutdown or factory-reset with root privilege. An exposed bus is
    a root-privileged attack surface, not just an assistant-control one.

    Never bind the bus to `0.0.0.0` or port-forward it to the internet. For
    remote access (satellites, phones, other rooms) use
    [HiveMind](hivemind-agents.md) instead, which adds authentication and
    encryption on top of the same bus protocol.

## Skills are not sandboxed

There is no sandbox, permission model, or capability system for skills.
**Installing a skill means running arbitrary Python code as the OVOS user**,
with the same filesystem and network access as the rest of the assistant.
This is exactly like installing a Python package from PyPI or `pip install`ing
something from GitHub, because that is literally the mechanism (see
[Skill Installer](skill-installer.md)). Only install skills whose source you
trust, the same way you'd vet any other code you run.

### `allow_pip` + the unauthenticated bus is a remote-code-execution chain

The [Skill Installer](skill-installer.md#configuration) is disabled by default,
guarded behind the `skills.installer.allow_pip` config key. If you turn it on
**and** the bus is reachable by someone untrusted (bound to `0.0.0.0`, exposed
through port-forwarding, or reachable on a shared/untrusted network), that is
a remote-code-execution chain: anyone who can speak to the bus can emit
`ovos.skills.install` with a URL of their choosing and have OVOS `pip install`
and load it. Treat `allow_pip: true` as equivalent to giving bus access
root-equivalent power over the device, and only combine it with a bus that is
kept strictly local.

---

## `mycroft.conf` can contain plaintext secrets

Anything you configure for cloud integrations (LLM API keys (`llm.key`), a
Home Assistant long-lived access token, custom STT/TTS server credentials,
an [`ovos-opendata-server`](https://github.com/OpenVoiceOS/ovos-opendata-server)
`open_data.api_key`) is stored **as plaintext** in your user config, typically
`~/.config/mycroft/mycroft.conf` (see [Configuration Management](config.md#file-locations)).
There is no secrets manager or encryption layer.

!!! warning "Treat mycroft.conf like a credentials file"
    - Set restrictive file permissions on it (`chmod 600 ~/.config/mycroft/mycroft.conf`)
      if the account is shared with anyone else.
    - **Don't sync it as part of your dotfiles** to a public repository. A
      GitHub search for `llm.key` or a Home Assistant token is exactly how
      these things leak. If you version-control your dotfiles, exclude this
      file (or template it and inject secrets from an untracked source) instead
      of committing it directly.
    - Anyone with read access to the device's filesystem, or with bus access to
      request the config, can read these values.

---

## Summary checklist

- [ ] Decide whether public STT/TTS servers are acceptable for your use case.
      switch to offline or self-hosted plugins if not ([STT plugins](stt-plugins.md),
      [TTS plugins](tts-plugins.md)).
- [ ] Keep the messagebus bound to `127.0.0.1`. Never expose port `8181`
      directly to the internet ([Bus Service](bus-service.md)).
- [ ] Set `gui_websocket.host` to `127.0.0.1`. It ships bound to `0.0.0.0` (all
      interfaces). Leave it wide only behind a VPN or an authenticating proxy. That
      socket carries the same authority as the bus
      ([GUI Service](gui-service.md)).
- [ ] Point `network_tests` at your own infrastructure if the default connectivity
      probes are not acceptable.
- [ ] Audit and clear `~/.local/share/mycroft/listener/recordings/` on shared
      devices. Nothing prunes it.
- [ ] Leave `allow_pip` off unless you specifically need runtime skill
      installation, and never combine it with a non-local bus
      ([Skill Installer](skill-installer.md)).
- [ ] Only install skills whose source you trust. There is no sandbox.
- [ ] Protect `mycroft.conf`'s file permissions and keep it out of shared
      dotfile repositories.
- [ ] Decide independently on install-time telemetry and ongoing usage
      telemetry. They are separate opt-ins ([installer telemetry](ovos-installer.md#anonymous-telemetry)).
- [ ] For remote/multi-room setups, use [HiveMind](hivemind-agents.md) instead
      of exposing the bus directly.

Found an actual vulnerability rather than a documentation gap? Use the affected
repository's Security tab → **Report a vulnerability** on
[github.com/OpenVoiceOS](https://github.com/OpenVoiceOS) to report it privately.

---
**Read next:** [STT Server](stt-server.md)
**Related:** [Production Operations](production-operations.md) · [Server Compatibility Layers](server-compat-layers.md) · [HiveMind](hivemind-agents.md) · [MessageBus Service](bus-service.md)
