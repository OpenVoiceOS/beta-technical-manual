# Change the Wake Word Without Training

!!! abstract "In a nutshell"
    You want the assistant to answer to a name you choose, like "Hey Jarvis" or "Hey Computer". Usually a custom wake word needs a trained model and many recordings. Two plugins skip that step: you type the wake word in the config and the assistant listens for it. WakePhoneHuBERT is the better choice. Vosk is simpler but works for fewer phrases.

## Try it in your browser first

The [WakePhoneHuBERT Space](https://huggingface.co/spaces/TigreGotico/wakephonehubert-space) runs the model in your web browser. Type a wake word, or its IPA phones, then say it into the microphone or upload a WAV file. The page marks each detection and shows the score, the phones it hears and the voice activity. The audio does not leave your device. Use it to check that a phrase works for your voice before you change your device.

The [WakeHuBERT wake words Space](https://huggingface.co/spaces/OpenVoiceOS/wakehubert-wakewords-space) does the same for the trained wake words in [OpenVoiceOS/wakehubert-wakewords](https://huggingface.co/OpenVoiceOS/wakehubert-wakewords). If your phrase is in that list, a trained model is more accurate than a zero-shot wake word. See [Wake-word Plugins](wake-word-plugins.md).

## Option 1: WakePhoneHuBERT

[WakePhoneHuBERT](https://huggingface.co/TigreGotico/wakephonehubert) is a small speech model that hears the sounds of speech, written as IPA phones. The zero-shot engine of `ovos-ww-plugin-wakeforge` compares those sounds with the phones of your wake word. You give the phones; no recordings and no training are necessary.

!!! warning "Alpha channel only"
    The zero-shot engine `ovos-ww-plugin-wakeforge-zeroshot` is in the prerelease channel of `ovos-ww-plugin-wakeforge` only. Install the plugin with `--pre`, as in step 1.

1. Install the plugin into the environment that OVOS runs in:

    ```bash
    pip install --pre ovos-ww-plugin-wakeforge
    ```

2. Get the phones of your wake word with eSpeak NG:

    ```bash
    espeak-ng -q --ipa -v en-us "hey jarvis"
    ```

    ```text
    hˈeɪ dʒˈɑːɹvɪs
    ```

    The engine accepts this output as it is, stress marks included. You can also write the phones with spaces, for example `h eɪ dʒ ɑːɹ v ɪ s`. eSpeak NG is necessary only for this step. The device does not need it.

3. Add the wake word to `~/.config/mycroft/mycroft.conf`:

    ```json
    {
      "listener": { "wake_word": "hey_jarvis" },
      "hotwords": {
        "hey_jarvis": {
          "module": "ovos-ww-plugin-wakeforge-zeroshot",
          "ipa": "hˈeɪ dʒˈɑːɹvɪs",
          "listen": true
        }
      }
    }
    ```

4. Restart OVOS:

    --8<-- "snippets/restart-ovos.md"

    The first start downloads the WakePhoneHuBERT model. The listener log then names the wake word, the number of phones and the threshold:

    ```text
    wakeforge zero-shot wake word 'hey_jarvis' loaded: 1 pronunciation(s), phones [7], thresholds [-0.2]
    ```

5. Say the wake word.

### Choose a good phrase

- Use at least six phones, ideally two words. "Hey Jarvis" has seven. Short single words are unreliable: train a model for them with [wakeforge](https://github.com/TigreGotico/wakeforge).
- Give more than one pronunciation as a list when people say the word in different ways: `"ipa": ["h eɪ dʒ ɑːɹ v ɪ s", "h eɪ dʒ ɑː v ɪ s"]`.
- Use phones that eSpeak NG gives. The default thresholds were set with eSpeak NG phones, on English speech. For other languages, check the scores in the Space and set `threshold`.

### Tune it

| Key | Default | What it does |
|---|---|---|
| `ipa` | none, required | The phones of the wake word, or a list of pronunciations |
| `threshold` | from the number of phones | The score that fires the wake word. 0 is a perfect match. A value nearer to 0 gives fewer false activations and fewer detections |
| `confirm_blocks` | `2` | How many 80 ms windows in a row must reach the threshold. A higher value gives fewer false activations |
| `debounce_sec` | `2.0` | The shortest time between two detections |

The default threshold is −0.05 for each phone above three, and it stops at −0.29 from nine phones. Use the Space to see the scores your voice gets, then set `threshold` between your scores and the scores of other speech.

Two listener features also cut false activations with any wake-word engine. The pre-wake VAD gate sends audio to the engine only when someone speaks: see [Pre-Wake VAD](ww-verifier.md#pre-wake-vad) and the blog post [OVOS Just Got a Noise Filter](https://blog.openvoiceos.org/posts/2025-11-06-prewake-vad). Verifier plugins check each detection after the engine fires: see [Wake-word Verifiers](ww-verifier.md) and [Make OVOS Answer Only Your Voice](answer-only-your-voice.md).

## Option 2: Vosk

`ovos-ww-plugin-vosk` runs the Vosk speech recognizer on short pieces of audio and compares the text with your wake word.

1. Install the plugin:

    ```bash
    pip install --pre ovos-ww-plugin-vosk
    ```

2. Add the wake word to `~/.config/mycroft/mycroft.conf`. Set `time_between_checks` to 3:

    ```json
    {
      "listener": { "wake_word": "hey_jarvis" },
      "hotwords": {
        "hey_jarvis": {
          "module": "ovos-ww-plugin-vosk",
          "samples": ["hey jarvis"],
          "time_between_checks": 3,
          "listen": true
        }
      }
    }
    ```

3. Restart OVOS and say the wake word. The first start downloads the small Vosk model for your language, 68 MB for English.

!!! warning "Set the check interval, keep the default rule"
    The plugin transcribes the audio that arrived since its last check. With the default `time_between_checks` of 1 second, a two-word phrase is often cut across two checks: in the measurement below it detected 1 of 7 voices. With 3 seconds, it detected 6 of 7.

    When `samples` is set and `full_vocab` is `false`, which is the default, the plugin limits the recognizer to the words of your phrase. Most speech then comes out as some of those words. The default rule, `equals`, needs the full phrase and nothing else, so this does little harm. With `"rule": "contains"`, a transcript that holds the phrase anywhere fires the wake word. In the measurement below, that rule gave about 1100 false activations an hour. Use `contains` only with `"full_vocab": true`.

**What Vosk needs and which phrases work:**

- Every word of the phrase must be in the vocabulary of the Vosk model. A made-up name cannot be detected.
- The plugin listens only for the words in `samples`. Add the ways the recognizer writes your phrase, for example `["hey computer", "a computer"]`. Set `"debug": true` and set the listener log level to `DEBUG` to see the text in the listener log.
- A phrase that falls across two checks can be missed, even with `time_between_checks` at 3.
- Vosk works in each language that has a Vosk model.

## How they compare

The table shows one measurement of each engine with the config above, with `ovos-ww-plugin-wakeforge` 0.18.0a1 and `ovos-ww-plugin-vosk` 0.1.10. The audio was fed as the listener feeds it, in 4096-byte chunks.

- **Detections:** "hey jarvis" and "hey computer", each spoken by 7 synthetic neural voices (US, UK, Australian and Indian English), with 1 second of silence before and after.
- **False activations:** 1 hour of English read speech that does not contain the wake word (LibriSpeech dev-other, 545 files).

| Engine | Detections, hey jarvis | Detections, hey computer | False activations in 1 hour of speech | Time to process 1 hour of audio, one laptop process |
|---|---|---|---|---|
| WakePhoneHuBERT zero-shot | 7 of 7 | 7 of 7 | 0 and 0 | about 12 minutes |
| Vosk, `time_between_checks` 3 | 6 of 7 | 6 of 7 | 0 and 0 | under 2 minutes |
| Vosk, defaults | 1 of 7 | 1 of 7 | 0 and 0 | about 3 minutes |
| Vosk, `"rule": "contains"` | 7 of 7 | 7 of 7 | 1101 and 1103 | about 3 minutes |

Synthetic voices and one hour of read speech are a small test. A real room has noise, music and television. On a larger test, 31 hours of speech and other sound over 28 wake words, the zero-shot engine gave a median of 0.61 false activations an hour, and "alexa" gave 7.7. Its mean detection rate was 88% on synthetic voices and 54% on recorded voices. For a wake word that must work every time, use a trained model.

**Related:** [Wake-word Plugins](wake-word-plugins.md) · [Make OVOS Answer Only Your Voice](answer-only-your-voice.md) · [Make It Yours](personalize.md)
