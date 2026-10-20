# Make OVOS Answer Only Your Voice

!!! abstract "In a nutshell"
    Anyone in the room can say the wake word. A speaker verifier checks *who* said it. You record a few clips of each person in your household once. After that, when someone else says the wake word, the assistant stays silent. The voice samples stay on your device as numbers, never as audio.

The speaker verifier is the plugin `ovos-ww-verifier-plugin-speaker`. It runs after the wake-word engine fires and before the assistant starts to listen. It compares the voice in the wake-word audio with the voices you enrolled. If no enrolled voice matches, the listener drops the activation. See [Wake-word Verifiers](ww-verifier.md) for how verifiers fit into the listener. The listener can run more than one verifier: the Silero VAD verifier `ovos-ww-verifier-silero`, from `ovos-vad-plugin-silero`, rejects wake words with no speech in them. The blog post [Only you can order the cheeseburgers: Speaker verification comes to OVOS](https://blog.openvoiceos.org/posts/2026-09-26-speaker-verifier) shows the verifier in use.

!!! warning "Alpha channel only"
    Only the prerelease channel of `ovos-dinkum-listener` loads verifiers. Install the listener with `pip install --pre ovos-dinkum-listener`.

## Before you start

- A working wake word. See [Change your wake word](wake-word-plugins.md#change-your-wake-word).
- Three or more recordings of each person, 16 kHz mono WAV. Ordinary sentences work. The wake word itself is not necessary. Five to thirty seconds of speech per person in total gives a better profile.

## Set it up

1. Install the plugin into the environment that OVOS runs in:

    ```bash
    pip install --pre ovos-ww-verifier-plugin-speaker
    ```

2. Enroll each person. Give a name, then the clips:

    ```bash
    ovos-speaker-enroll Alice alice1.wav alice2.wav alice3.wav
    ovos-speaker-enroll Bob bob1.wav bob2.wav bob3.wav
    ```

    The command prints the stored profiles:

    ```text
    Enrolled 'Alice' from 3 clip(s).
    Profile dim=256  norm=1.000000
    Profiles saved to: /home/<user>/.local/share/ovos_speaker_verifier/profiles.json
    Enrolled speakers: ['Alice']
    ```

    The first run downloads the speaker model. The profiles file holds one vector of 256 numbers per person and no audio.

3. Add the verifier to `~/.config/mycroft/mycroft.conf`:

    ```json
    {
      "listener": {
        "ww_verifiers": {
          "ovos-ww-verifier-speaker": {
            "threshold": 0.45,
            "fail_open": false
          }
        }
      }
    }
    ```

4. Restart OVOS:

    --8<-- "snippets/restart-ovos.md"

5. Say the wake word. The listener log has one `INFO` line for each decision, with the name of the best match, the score and the threshold:

    ```text
    speaker verifier accepted Alice (score 0.738, threshold 0.45)
    speaker verifier rejected unknown speaker (best match Alice score 0.116, threshold 0.45)
    ```

    These two lines come from a test with three synthetic voices and Alice enrolled. Alice's "Hey Jarvis, what time is it?" scored 0.738. The two other voices scored 0.116 and 0.170.

## What happens to a rejected wake word

A rejected speaker removes the wake word event itself. The bus gets no `recognizer_loop:wakeword` and no `recognizer_loop:record_begin`, so no skill sees the activation.

| Speaker | Profiles enrolled | `fail_open` | Result |
|---|---|---|---|
| An enrolled person | yes | any | The assistant listens |
| Anyone else | yes | any | The assistant stays silent |
| Anyone | none | `true` | The assistant listens |
| Anyone | none | `false` | The assistant stays silent |

!!! note "Installing the plugin turns it on"
    The listener runs every installed verifier unless its config sets `"enabled": false`. With `fail_open` at its default of `true`, the verifier accepts everyone until you enroll the first person. Enroll first, then set `fail_open` to `false`.

## Tune the threshold

The `threshold` is a cosine similarity between 0 and 1. A higher value rejects more guests and also more of your own wake words. A lower value does the opposite. Lower it for a distant or noisy microphone.

The default of 0.45 is for the default model, `wespeaker-resnet34`. **Each model has its own score scale.** If you change `model`, find the threshold for that model: compare the scores in the log for your own voice and for a guest, and choose a value between them. Set a different value for one person with `per_profile_thresholds`, for example `{"Bob": 0.5}`.

## Configuration keys

| Key | Default | What it does |
|---|---|---|
| `model` | `wespeaker-resnet34` | Speaker model: a `speakeronnx` alias or a path to an `.onnx` file |
| `threshold` | `0.45` | Lowest similarity that counts as a match |
| `fail_open` | `true` | Accept every wake word when no profile is enrolled |
| `profiles_path` | `~/.local/share/ovos_speaker_verifier/profiles.json` | Where the profiles are stored |
| `per_profile_thresholds` | `{}` | A threshold for each name |
| `enabled` | `true` | Set `false` to keep the plugin installed but inactive |

The plugin README lists the other speaker models and the audio format keys.

## Limits

- The verifier checks a voice, not a password. A recording of an enrolled person can pass.
- Enroll clips recorded on the microphone that OVOS uses, so the profile matches what the verifier hears.
- The verifier sees only the wake-word audio. A short wake word gives less speech to compare.

**Related:** [Wake-word Verifiers](ww-verifier.md) · [Wake-word Plugins](wake-word-plugins.md) · [Change the Wake Word Without Training](change-wake-word-without-training.md) · [Make It Yours](personalize.md)
