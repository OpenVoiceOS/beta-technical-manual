# Stop Wake-ups from the TV

--8<-- "snippets/alpha-only.md"

This page reduces the false activations that come from a TV, a radio, music or noise in the room. It tells you which filter to use for which sound, and what each filter costs.

## Who this is for

The assistant wakes up when nobody spoke to it. It happens during a film, a podcast or a noisy meal.

## What you get

- The pre-wake VAD against noise, music and other sounds that are not speech.
- A verifier against voices that are not yours.
- Measured rates for each filter, so you can see what it removes and what it costs.

## Know the sound that wakes it

Different sounds need different filters:

| Sound that wakes the assistant | Filter that helps |
|---|---|
| Noise, music, taps, coughs | Pre-wake VAD |
| A voice on the TV or radio | Speaker verifier |
| A phrase that sounds like the wake word | A higher threshold, or a model trained with sound-alike phrases |

To find the sound, set `listener.record_wake_words` to `true`. The listener then saves the audio of each detection, and you can listen to the false activations. See [Listener Service](speech-service.md).

## Filter 1: pre-wake VAD

The pre-wake VAD runs the wake-word engine only after it hears speech. When it hears no wake word for 5 s after the speech, it stops the engine again. The default `mycroft.conf` turns it on:

```json
{
  "listener": {
    "vad_pre_wake_enabled": true
  }
}
```

The pre-wake VAD cannot stop a false activation from speech. A TV voice is speech, so the VAD lets it through to the engine.

## Filter 2: speaker verifier

The speaker verifier accepts a wake word only from a voice that you enrolled. A TV voice is not enrolled, so the verifier rejects its wake words. See [Make OVOS Answer Only Your Voice](answer-only-your-voice.md) for the setup.

These rates come from the plugin's own embedder and cosine score on LibriSpeech test-clean. The test set has 40 speakers. Each speaker was enrolled from 3 whole utterances. Each test is a 1.5 s window from a different utterance, about the length of a wake word. A household is 4 enrolled speakers, and an outsider is any of the other 36 speakers. Each of 20 random households gives 40 member tests and 360 outsider tests, 800 and 7,200 in total.

| `threshold` | Household member rejected | Outsider accepted |
|---|---|---|
| 0.35 | 2.8% | 3.8% |
| 0.40 | 3.6% | 1.3% |
| **0.45 (default)** | **5.0%** | **0.36%** |
| 0.50 | 11.5% | 0.04% |
| 0.55 | 20.0% | 0.0% |

At the default threshold, about 1 wake word in 20 from a household member is rejected, and about 1 in 280 from an outsider is accepted. With 1.0 s windows, the default threshold rejects 16.5% of member wake words, so a short wake word gives the verifier less to work with. LibriSpeech is clean read speech: a far microphone or a noisy room can make the member reject rate higher.

## Filter 3: Silero verifier

The `ovos-ww-verifier-silero` verifier rejects a detection when the wake-word audio holds too little speech. It scores the audio before the detection: the last 15 microphone chunks, 1.92 s with the default 128 ms chunks. With the pre-wake VAD on, the window starts where the VAD heard speech, so it is shorter. The default `mycroft.conf` turns the verifier off, because the pre-wake VAD does a similar job.

## Measured effect

These rates come from the real listener loop. The positives are recordings of real people from the [OVOS community wake-word dataset](https://huggingface.co/datasets/OpenVoiceOS/ovos-community-wakewords-dataset). The noise negatives are 1 hour of [wake_word_noise](https://huggingface.co/datasets/OpenVoiceOS/wake_word_noise): audio that woke real devices by mistake, spoken near-misses, microphone taps and background noise. The speech negatives are 5.4 hours of read English from LibriSpeech test-clean. The listener got the audio in 128 ms chunks, as from the default microphone plugins, with a -60 dBFS noise floor before each wake word.

| Wake word | Negatives | Setup | Recall | False activations per hour |
|---|---|---|---|---|
| hey chatterbox | noise, 1 h | engine only | 81.0% | 4.93 |
| hey chatterbox | noise, 1 h | pre-wake VAD | 81.9% | 4.93 |
| hey chatterbox | noise, 1 h | Silero verifier | 69.8% | 4.93 |
| hey chatterbox | noise, 1 h | pre-wake VAD and Silero verifier | 78.4% | 4.93 |
| hey floyd | noise, 1 h | engine only | 91.7% | 0.99 |
| hey floyd | noise, 1 h | pre-wake VAD | 93.8% | 0 |
| hey floyd | noise, 1 h | Silero verifier | 79.2% | 0.99 |
| hey floyd | noise, 1 h | pre-wake VAD and Silero verifier | 82.3% | 0 |
| hey floyd | speech, 5.4 h | engine only | 91.7% | 0.56 |
| hey floyd | speech, 5.4 h | pre-wake VAD | 93.8% | 0.56 |
| hey floyd | speech, 5.4 h | Silero verifier | 79.2% | 0.56 |
| hey floyd | speech, 5.4 h | pre-wake VAD and Silero verifier | 82.3% | 0.56 |

- The pre-wake VAD loses no wake words. It removed the false activation of "hey floyd" in the noise. Against speech it removes nothing: the audio is speech, so it lets it through.
- The Silero verifier removed no false activation that the pre-wake VAD did not also remove. It cost 11 to 13 points of recall on its own, and 3 to 12 points behind the pre-wake VAD. Leave it off unless your own measurement shows a gain.
- Three of the five false activations of "hey chatterbox" come from the spoken phrase "a cheddar block". All five are spoken words. No VAD or verifier rejects a phrase like that, because it is speech. Use a higher threshold, or train the model with that phrase as a negative.

## Measure your own setup

The script `examples/measure_false_activations.py` in [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) gave the table above. It runs the real listener loop with your engine, VAD and verifiers on your recordings:

```bash
python measure_false_activations.py \
    --module ovos-ww-plugin-wakeforge --ww-config '{"model": "wakehubert_hey_floyd"}' \
    --verifier ovos-ww-verifier-silero \
    --positives hey_floyd/ --negatives tv_audio/ --out results.json
```

Record an hour of your own TV as the negatives. A rate from your own audio is a better guide than the rates on this page.

## Related pages

- [Wake-word Verifier Plugins](ww-verifier.md): all verifier configuration keys.
- [Tune False Activations](ww-tune.md): the threshold.
- [Wake Word Guide](wake-word-guide.md): all the wake-word tasks.
