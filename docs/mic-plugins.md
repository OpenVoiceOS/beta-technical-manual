# Microphone Plugins in OVOS

!!! abstract "In a nutshell"
    A microphone plugin is the part that listens. It grabs the sound coming in from your device's microphone and hands it to the rest of the assistant so it can hear you. Different devices and setups need different ways of capturing that sound, so these plugins let you switch the "ears" without changing anything else. Think of it like choosing which microphone to plug into a recorder. See the [Glossary](glossary.md) for unfamiliar terms.

Microphone plugins in Open Voice OS (OVOS) are responsible for capturing audio input and feeding the raw PCM stream to the listener. They let you swap audio backends and platforms without touching the rest of the voice stack.

> The audio-capture mechanism is **deployer-defined** and sits outside the formal audio-input service contract. The listener consumes whatever a microphone plugin produces. See the [OVOS-AUDIO-IN-1](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md) specification for how captured audio enters the utterance lifecycle.

## Usage Guide

To use a microphone plugin in OVOS:

- Install the desired plugin with `pip`:

```bash
pip install ovos-microphone-plugin-<name>

```

- Update your `mycroft.conf` (or `mycroft.conf`) to specify the plugin:

```jsonc
{
 "listener": {
   "microphone": {
     "module": "ovos-microphone-plugin-alsa"  // or another plugin
   }
 }
}

```

- Restart OVOS to apply the new microphone plugin configuration.

## Supported Microphone Plugins

| Plugin | Description | OS Compatibility | Maturity |
|--------|-------------|------------------|----------|
| [ovos-microphone-plugin-alsa](https://github.com/OpenVoiceOS/ovos-microphone-plugin-alsa) | Based on [pyalsaaudio](http://larsimmisch.github.io/pyalsaaudio). Offers low-latency and high performance on ALSA-compatible devices. | Linux | Stable |
| [ovos-microphone-plugin-pyaudio](https://github.com/OpenVoiceOS/ovos-microphone-plugin-pyaudio) | Uses the [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) PortAudio bindings directly (no `speech_recognition` dependency). Good cross-platform general-purpose plugin. | Linux, macOS, Windows | Beta |
| [ovos-microphone-plugin-sounddevice](https://github.com/OpenVoiceOS/ovos-microphone-plugin-sounddevice) | Built on [python-sounddevice](https://github.com/spatialaudio/python-sounddevice). Offers cross-platform support. | Linux, macOS, Windows | Stable |
| [ovos-microphone-plugin-files](https://github.com/OpenVoiceOS/ovos-microphone-plugin-files) | Uses audio files as input instead of a live microphone. Ideal for testing and debugging. | Linux, macOS, Windows | Stable |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).


!!! tip "Writing your own microphone plugin"
    Building a plugin for a new audio backend instead of using one from the table? The
    `Microphone` interface, a full walkthrough, and standalone usage patterns live on the
    [Microphone Plugin Development](mic-plugin-development.md) page.

## Configuration Notes

Most plugins in the table above need no extra configuration beyond `module`. When you do
need to override something — for example pinning a specific input device on
`ovos-microphone-plugin-sounddevice` — the plugin's settings go in a nested block keyed by
the plugin name (omit the block entirely when you have nothing to override):

### ovos-microphone-plugin-sounddevice

```json
{
  "listener": {
    "microphone": {
      "module": "ovos-microphone-plugin-sounddevice",
      "ovos-microphone-plugin-sounddevice": {"device": "hw:1,0"}
    }
  }
}

```

---
**Read next:** [VAD Plugins](vad-plugins.md)
**Related:** [Microphone Plugin Development](mic-plugin-development.md) · [Choosing Plugins](choosing-plugins.md) · [Wake-word Plugins](wake-word-plugins.md) · [STT Plugins](stt-plugins.md)