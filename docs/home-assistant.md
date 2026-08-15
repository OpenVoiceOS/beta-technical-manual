# OVOS & Home Assistant

!!! abstract "In a nutshell"
    OVOS and [Home Assistant](https://www.home-assistant.io/) (HA) are two different open-source
    projects. They can work together in **two separate, independent directions**: OVOS can
    *lend its speech engines to* Home Assistant's own voice pipeline, or a skill on OVOS can
    *control devices inside* Home Assistant. You can use either one alone, or both at once.
    They don't depend on each other. This page explains both directions and links to the
    details.

There is no single "OVOS + Home Assistant" switch. There are two unrelated integrations, and
it's easy to conflate them. Pick the one, or both, that matches what you're trying to do:

| Direction | What it does | Runs where | Details |
|---|---|---|---|
| **HA uses OVOS's engines** | Home Assistant's own [Assist](https://www.home-assistant.io/voice_control/) voice pipeline uses an OVOS wake word, speech-to-text, or text-to-speech plugin instead of (or alongside) its built-in ones | A small OVOS-side bridge process, reachable from HA over the network | [Wyoming Bridges](wyoming-bridges.md) |
| **OVOS controls HA devices** | Your OVOS assistant understands utterances like "turn on the lights" and relays them to your Home Assistant instance | A skill running inside OVOS | See below |

---

## Direction 1: Home Assistant uses OVOS's speech engines

Home Assistant's own voice assistant feature (Assist) can use external speech components over
the [Wyoming protocol](https://github.com/rhasspy/wyoming), the same protocol Rhasspy and other
open voice tools speak. OVOS ships three small bridge packages
(`wyoming-ovos-stt`, `wyoming-ovos-tts`, `wyoming-ovos-wakeword`) that each expose one installed
OVOS plugin as a Wyoming server. This lets Home Assistant point Assist at, say, an OVOS STT
plugin without knowing anything about the OVOS plugin system underneath.

This is useful if you already have OVOS plugins configured and tuned, such as a particular STT
model or TTS voice, and want Home Assistant's own Assist pipeline to use them. It saves you
from running a second, separately configured set of speech engines just for HA.

See [Wyoming Bridges](wyoming-bridges.md) for installation, configuration, and the exact HA-side
setup (adding a Wyoming integration pointed at the bridge's host and port).

!!! warning "Pick one brain, not both"
    The two directions correspond to two different architectures. With the Wyoming
    bridges, **Home Assistant is the brain**: HA's Assist pipeline runs the wake word
    and intents, borrowing OVOS's speech engines. With OVOS satellites
    ([HiveMind](satellites.md)), **OVOS is the brain** and controls HA as one of its
    skills. Do not combine a Wyoming wake-word bridge with a HiveMind mic satellite on
    the same device — you would run two competing wake-word pipelines. Decide which
    system owns the conversation first, then follow only that direction's pages.

---

## Direction 2: OVOS controls Home Assistant devices

To have your OVOS assistant turn on lights, adjust a thermostat, or run a scene, you install a
skill that talks to your existing Home Assistant instance over its REST/WebSocket API.

!!! note "The old PHAL plugin is gone"
    An earlier integration, `ovos-PHAL-plugin-homeassistant`, has been removed. The current,
    maintained path is the `skill-homeassistant` skill (maintained by OscillateLabs) listed
    below — see [Deprecated & Removed Repositories](deprecated-repos.md) for the retirement
    note.

### Setting it up

You need two things from your Home Assistant instance before installing the skill:

1. **The URL** of your Home Assistant instance (e.g. `http://homeassistant.local:8123`).
2. **A long-lived access token.** Generate one from your Home Assistant user profile page
   (*Settings → your profile → Long-Lived Access Tokens → Create Token*) and keep it secret. It
   grants the same access as your account.

With those two in hand, either:

- Tick the `homeassistant` feature in the [ovos-installer](ovos-installer-scenarios.md#feature-selection),
  offered for the `ovos`/`listener` profiles on the `virtualenv` or `containers` install
  method. The installer prompts you for the URL and token during setup, or

    !!! note "RaspOVOS users: this doesn't apply to you"
        The `homeassistant` feature above belongs to the `ovos-installer` flow, for setups
        installed via that installer. If you're on a RaspOVOS image (flashed straight to an
        SD card or USB drive), you never run `ovos-installer` — install the skill directly
        with the command below instead.

- Install the skill yourself afterwards. On RaspOVOS, use `ovos-install`, which installs with
  the correct version constraints:
  ```bash
  ovos-install skill-homeassistant
  ```
  On any other setup, use `pip install` instead:
  ```bash
  pip install skill-homeassistant
  ```
  Then configure it with your instance's URL and token (see the skill's own repository for the
  current configuration key names), and restart OVOS to load it.

### Example utterances

Actual phrasing and which devices respond depend entirely on how your own devices, areas, and
scenes are named inside Home Assistant:

- "Turn on the living room lights."
- "Turn off the kitchen lights."
- "Tell home assistant to set the thermostat to 20 degrees."
- "Tell home assistant to activate the movie night scene."

Thermostats and scenes have no dedicated intent in the skill: the "tell home assistant to
…" phrasing forwards the rest of the sentence to Home Assistant's own Assist conversation
API, which handles anything HA itself can parse. Lights, switches, and sensors get
dedicated intents with barer phrasing.

See [What can I say? — Smart Home](skill-examples.md#smart-home) for the skill's catalog entry.

---

---
**Read next:** [Wyoming Bridges](wyoming-bridges.md)
**Related:** [HiveMind](hivemind-agents.md) · [STT Server](stt-server.md) · [TTS Server](tts-server.md) · [Production Operations](production-operations.md)
