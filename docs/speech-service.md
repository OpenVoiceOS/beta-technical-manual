# Speech Service

!!! abstract "In a nutshell"
    The speech service is the "ears" of OpenVoiceOS. It listens through the microphone, waits for a wake word (like "Hey Mycroft"), and then turns whatever you say next into text so the rest of the system can act on it. Think of it as the part that hears you and writes down your request. From here that text is handed off to the [Intent Service](intent-service.md), which works out what to do. New to the terms? See the [Glossary](glossary.md).

??? info "📐 Formal specification"
    The capture → audio-transformer chain → STT → utterance flow and the listening-lifecycle signals are specified by **[OVOS-AUDIO-IN-1 — Audio Input Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md)**; the audio-transformer chain that runs on the raw audio before STT by **[OVOS-TRANSFORM-1 — Transformer Plugins](https://github.com/OpenVoiceOS/architecture/blob/dev/transformer.md)** (§3.1). See also the [spec index](architecture-specs.md). `ovos-dinkum-listener` is the reference implementation; the spec topic names below are canonical, with the legacy name noted once.

`ovos-dinkum-listener` is the service responsible for audio capture, [Wake Word](wake-word-plugins.md) detection, and [Speech-to-Text](stt-plugins.md) ([STT](stt-plugins.md)). It is the default, full-featured listener; `ovos-simple-listener` is a lighter alternative that emits the same `recognizer_loop:*` bus events but without the full state machine.

A third, even more minimal option is `mycroft-classic-listener` — the original mycroft-core listener ported to the OVOS plugin ecosystem. It implements the same `recognizer_loop:*` contract but does **not** support `instant_listen`, multiple hotwords, VAD, listening modes, or fallback STT (fallback hotwords via OPM are supported).

---

??? abstract "Technical Reference"

    - `OVOSDinkumVoiceService` — [`ovos_dinkum_listener/service.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — the service `Thread`; `run()` connects to the bus and drives the voice loop.


    - `DinkumVoiceLoop.run()` — [`ovos_dinkum_listener/voice_loop/voice_loop.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/voice_loop/voice_loop.py) — the per-chunk state machine that drives [VAD](vad-plugins.md), [Wake Word](wake-word-plugins.md) and [STT](stt-plugins.md) via per-state handlers.


    - `OVOSDinkumVoiceService._stt_text()` — [`ovos_dinkum_listener/service.py`](https://github.com/OpenVoiceOS/ovos-dinkum-listener/blob/dev/ovos_dinkum_listener/service.py) — emits the utterance message after [STT](stt-plugins.md) returns text: the listener emits the spec topic `ovos.utterance.handle` (`SpecMessage.UTTERANCE`) directly, and `ovos-bus-client`'s `NamespaceTranslator` (see [Bus Service](bus-service.md#namespace-migration)) also emits the legacy `recognizer_loop:utterance` alias for old consumers.
    
    ---
    

## Overview

The speech service is the "ears" of OpenVoiceOS. It continuously listens to the environment, waiting for a specific [Wake Word](wake-word-plugins.md). When the word is detected, it records the user's command and sends it to an [STT](stt-plugins.md) engine for transcription.

### Key Components

- **Microphone Plugin**: Captures raw audio from the hardware.


- **[Voice Activity Detection](vad-plugins.md) ([VAD](vad-plugins.md))**: Identifies when a user starts and stops speaking.


- **[Wake Word](wake-word-plugins.md) Plugin**: Monitors the audio stream for the trigger phrase.


- **[STT](stt-plugins.md) Plugin**: Transcribes the recorded command into text.

## Architecture

```text
[Microphone] --(audio)--> [VAD/Wake Word] --(trigger)--> [Recording]
                                                            |
                                                            +--(audio)--> [Audio-transformer chain] --> [STT Plugin] --(text)--> [MessageBus]
                                                                          (TRANSFORM-1 §3.1)            emits ovos.utterance.handle

```

## Listening State Machine

`DinkumVoiceLoop` is a per-chunk state machine, not a single "listen" call. It has a
global **mode** (set in `listener.mode` / over the bus) and an internal **state** that
advances chunk by chunk:

- **Modes** (`ListeningMode`): `wakeword` (default — wait for the wake word),
  `continuous` (always transcribe), `hybrid` (continuous but only act after the wake
  word), `sleeping`.


- **States** (`ListeningState`): `wakeword` → `recording` → `in_cmd` → `after_cmd`,
  plus `sleeping` / `wake_up`, `confirmation`, `before_cmd`, `pre_wake_vad`, and
  `WAITING_CMD = "continuous"` — the state used while continuous/hybrid listening waits
  for an utterance without a wake word.

Source: `ovos_dinkum_listener/voice_loop/voice_loop.py:36` (`ListeningState`) and `:53`
(`ListeningMode`).

## Bus Events

The listener emits its activity on the OVOS [messagebus](bus-service.md). The most
useful events for downstream services:

Canonical (spec) names are shown first, with the legacy name in parentheses. The `ovos.listener.*` and `ovos.utterance.handle` names come from [OVOS-AUDIO-IN-1 §5–§6](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-in.md). `ovos-dinkum-listener` emits the spec `ovos.*` topics directly for the record/awoken/utterance events (via `SpecMessage`), and emits the wake-word event under its legacy `recognizer_loop:wakeword` name. Either way both topics reach subscribers: `ovos-bus-client`'s `NamespaceTranslator` runs on every client with both directions on by default (see [Bus Service](bus-service.md#namespace-migration)) — emitting a spec topic also emits its legacy alias, and emitting a legacy topic also emits its spec alias.

| Message | Payload | Meaning |
|---|---|---|
| `ovos.listener.record.started` (legacy: `recognizer_loop:record_begin`) | none | Command recording started (§6.1) |
| `ovos.listener.record.ended` (legacy: `recognizer_loop:record_end`) | none | Command recording ended (§6.2) |
| `recognizer_loop:wakeword` (spec alias: `ovos.listener.wakeword`) | `{"utterance": str, "key_phrase": str, …}` | Wake word detected; capture is opening (§6.5). `utterance` is the spoken key phrase (underscores/hyphens spaced out), `key_phrase` its raw form; `filename` is added when `listener.record_wake_words` is on. A per-wake-word `stt_lang` override, when configured, rides the message context (surfaced as `session.request_lang`) rather than the payload |
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `{"utterances": [str], "lang"}` | Transcribed command — the main result (§5, OVOS-PIPELINE-1 §9.1) |
| `recognizer_loop:speech.recognition.unknown` | none | STT returned nothing (silence / failure) |
| `ovos.listener.awoken` (legacy: `mycroft.awoken`) | none | Listener woke from sleep (§6.4) |

It also reacts to inbound commands: `ovos.listener.sleep` (legacy: `recognizer_loop:sleep`)
suspends capture, `recognizer_loop:wake_up` resumes it, plus `recognizer_loop:record_stop`
and `recognizer_loop:state.get`. The full table lives in the bus-message spec
(`message_spec/dinkum.md`).

!!! note "Sleep is device-scoped, not session-scoped"

    `ovos.listener.sleep` rides a session like every other message, but sleep mode is a
    **physical device state**: a sleeping listener captures nothing, for any session
    (AUDIO-IN-1 §6.3). Entering or leaving sleep therefore affects the whole device, not
    only the session that carried the request. Sleep entry is unacknowledged by design —
    the only sleep-related emission is `ovos.listener.awoken` on the sleep→awake
    transition.

!!! note "Gotcha — utterance namespace"

    The listener publishes the transcribed command on the spec topic
    `ovos.utterance.handle`. `ovos-bus-client`'s namespace translator (on by default)
    also emits the legacy `recognizer_loop:utterance` alias, so subscribers can use
    either topic name — see [Bus Service — Namespace migration](bus-service.md#namespace-migration)
    for how to turn that aliasing off once every consumer speaks the spec namespace.

## Configuration

The speech service is configured in the `listener`, `hotwords`, and `stt` sections of `mycroft.conf`.

```json
{
  "listener": {
    "microphone": {
      "module": "ovos-microphone-plugin-alsa"
    },
    "VAD": {
      "module": "ovos-vad-plugin-silero"
    }
  },
  "stt": {
    "module": "ovos-stt-plugin-server"
  }
}

```

!!! tip "Saving wake-word audio locally"
    Set `listener.record_wake_words: true` and the listener writes each detected
    wake-word clip to disk (under its `wake_words` save directory) and adds the
    `filename` to the wake-word message — handy for gathering training data or
    debugging false triggers. The clips stay on the device; the listener itself does
    not upload anything.
