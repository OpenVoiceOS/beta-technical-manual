# Wake Word Verifier Plugins

!!! abstract "In a nutshell"
    A "wake word" is the phrase that gets the assistant's attention, like "Hey Mycroft". Sometimes the assistant thinks it heard that phrase when it didn't. A wake word verifier is a second pair of ears: after the wake word seems to have been detected, it double-checks the recorded audio and can cancel a false alarm before the assistant starts listening. This cuts down on the device waking up by accident. See the [Wake Word plugins](wake-word-plugins.md) for the detectors themselves, or the [Glossary](glossary.md) for terms.

The wake word verifier framework lets one or more secondary plugins inspect the audio captured during a wake-word detection event and veto false triggers. This is separate from the detection plugin itself and runs as a post-detection gate.

---

## Pre-Wake VAD

Before the wake word detector even fires, an optional VAD gate can filter frames that are clearly silent, reducing the detection surface for false activations.

```json
{
  "listener": {
    "vad_pre_wake_enabled": true
  }
}
```

When enabled, audio frames pass through the configured VAD plugin before reaching the wake word model. A 5-second fallback returns the listener to the pre-wake VAD state if no wake word is detected.

---

## Verifier Configuration

```json
{
  "listener": {
    "ww_verifiers": {
      "ovos-ww-verifier-silero": {"threshold": 0.1}
    },
    "vad_pre_wake_enabled": false
  }
}
```

Multiple verifiers can be listed; a detection is accepted only if all verifiers pass. Combine either `ww_verifiers` or `vad_pre_wake_enabled` — enabling both is redundant.

---

## OPM Verifier Interface

```python
from ovos_plugin_manager.templates.hotwords import HotWordVerifier

class MyVerifier(HotWordVerifier):
    def verify(self, chunk: bytes) -> bool:
        """Return True to accept the detection, False to veto it."""
        ...
```

Plugin entry point group: `opm.wake_word.verifier`.

```python
# pyproject.toml
[project.entry-points."opm.wake_word.verifier"]
my-verifier = "my_package:MyVerifier"
```

---

## Silero Verifier

The reference verifier wraps the Silero VAD model to confirm that captured audio contains actual speech, not silence or transient noise:

```json
{
  "listener": {
    "ww_verifiers": {
      "ovos-ww-verifier-silero": {"threshold": 0.1}
    }
  }
}
```

A lower `threshold` accepts quieter speech; raise it to require stronger speech confidence.

!!! note
    `ovos-ww-verifier-silero` is the reference verifier used throughout the listener's own examples and end-to-end tests. It is not a separate PyPI package — it is an `opm.wake_word.verifier` entry point registered by [`ovos-vad-plugin-silero`](vad-plugins.md), so `pip install ovos-vad-plugin-silero` is what makes it available.

---

## Speaker Verification

The `ovos-ww-verifier-plugin-speaker` plugin gates wake-word detections against enrolled household profiles — only recognized household members can activate the assistant; guests are silently ignored. With no profiles enrolled the verifier fails open (everyone allowed).

Enrollment is a one-time CLI step per person:

```bash
ovos-speaker-enroll Alice clip1.wav clip2.wav clip3.wav
```

Profiles are stored as embedding vectors in `~/.local/share/ovos_speaker_verifier/profiles.json` — no audio is retained. The plugin registers under `opm.wake_word.verifier` as `ovos-ww-verifier-speaker`, so wire it like any other verifier:

```json
{
  "listener": {
    "ww_verifiers": {
      "ovos-ww-verifier-speaker": {
        "model": "wespeaker-resnet34",
        "threshold": 0.45,
        "fail_open": false
      }
    }
  }
}
```

!!! warning "Fail-open is the default"
    `fail_open` defaults to **`true`**: an installed-but-unenrolled plugin accepts *every* activation. Set `"fail_open": false` to reject all detections until at least one profile is enrolled.

### Config keys

| Key | Type | Default | Purpose |
| --- | --- | --- | --- |
| `model` | str | `wespeaker-resnet34` | speakeronnx model alias or `.onnx` path |
| `threshold` | float | `0.45` | Global cosine-similarity acceptance threshold |
| `fail_open` | bool | `true` | Accept all activations when no profiles are enrolled |
| `per_profile_thresholds` | dict | `{}` | Per-name threshold overrides, e.g. `{"Alice": 0.5}` |
| `profiles_path` | str | XDG data dir | Override the profile-storage location |
| `sample_rate` / `sample_width` / `channels` | int | `16000` / `2` / `1` | PCM format of the incoming audio chunk |

The `model` key accepts any alias from [`speakeronnx`](https://github.com/TigreGotico/speakeronnx)'s model registry — `wespeaker-resnet34` (default), `wespeaker-ecapa512`, `campplus`, `titanet-small`/`titanet-large`, `eres2net`, `redimnet-b2`, and others — or a direct `.onnx` path.

!!! note "Threshold is model-specific"
    The `threshold` does **not** transfer between models. Cosine-similarity scales differ enormously by architecture — the same enrolled-vs-guest pair scored ~0.95 on `titanet-small` but ~0.17 on `campplus`. The default `0.45` is calibrated only for `wespeaker-resnet34`; if you change `model`, you must re-tune `threshold`.

Use case: household authorization — a shared-wake-word deployment where each registered user's voice profile allows or denies activation.

---

## Precise-ONNX Plugin

`ovos-ww-plugin-precise-onnx` provides high-accuracy wake word detection from `.onnx` model files, without TensorFlow Lite dependency.

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-onnx",
      "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.onnx",
      "trigger_level": 3,
      "sensitivity": 0.5
    }
  }
}
```

---

## microWakeWord Plugin

> **Status:** [OpenVoiceOS/ovos-ww-plugin-microwakeword](https://github.com/OpenVoiceOS/ovos-ww-plugin-microwakeword) — in development, not yet published to PyPI.

OVOS wake-word plugin wrapping [microWakeWord](https://github.com/kahrendt/microWakeWord) TFLite streaming models from the ESPHome ecosystem. Enables zero-cost sub-1 MB wake word models originally designed for microcontrollers.

---

## Related Pages

- [Wake Word Plugins](wake-word-plugins.md) — detection plugin reference
- [VAD Plugins](vad-plugins.md)
- [Listener / Speech Service](speech-service.md)

## Further reading

- [A Noise Filter for Better Listening (Pre-Wake VAD)](https://blog.openvoiceos.org/posts/2025-11-06-prewake-vad) — OVOS blog
