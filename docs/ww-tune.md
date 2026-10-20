# Tune False Activations

--8<-- "snippets/alpha-only.md"

Change the threshold of a wake-word engine to get fewer false activations or fewer missed wake words. Use this task when the assistant wakes up when nobody said the wake word, or does not wake up when you say it. The threshold moves the balance between the two.

## What you get

- A threshold that is correct for your room and your voices.
- Numbers that show what the change costs.

## The trade-off

Each engine gives a score for each window of audio. The engine fires when the score is more than the threshold. A higher threshold gives fewer false activations and more missed wake words. A lower threshold gives more of both. No threshold removes both kinds of error.

The name of the setting is different for each engine:

| Engine | Key | A higher value gives |
|---|---|---|
| `ovos-ww-plugin-wakeforge` | `threshold` (0 to 1) | fewer false activations |
| `ovos-ww-plugin-wakeforge-zeroshot` | `threshold` (negative, 0 is a perfect match) | fewer false activations |
| `ovos-ww-plugin-precise-onnx` | `sensitivity` (0 to 1) | more false activations |
| `ovos-ww-plugin-precise-onnx` | `trigger_level` (chunks) | fewer false activations |
| `ovos-ww-plugin-microwakeword` | `probability_cutoff` (0 to 1) | fewer false activations |

For the Precise keys, see [`sensitivity` vs `trigger_level`](wake-word-plugins.md#sensitivity-vs-trigger_level-the-technical-breakdown).

## What a wakeforge threshold means

The ready models of `ovos-ww-plugin-wakeforge` are calibrated. On a calibrated model, a threshold of 0.5 gives about one false activation per hour on the held-out speech and noise of the model card. Each model has its own default threshold. The default gives the best F2 score, which counts recall as more important than precision. The model card at [OpenVoiceOS/wakehubert-wakewords](https://huggingface.co/OpenVoiceOS/wakehubert-wakewords) gives the default of each model and its results at the default and at 0.8.

## Measured example

The model `wakehubert_hey_floyd` has a default threshold of 0.43. These rates come from the `ww_score.py` script of [Compare Wake-word Engines on Your Audio](ww-compare.md). The positives are 96 recordings of "hey floyd" by real people. The negatives are all of LibriSpeech test-clean, 2620 files of read English speech. The script adds 2 s of silence to each file, so the negatives total 6.86 h.

| `threshold` | Recall | False activations per hour |
|---|---|---|
| 0.3 | 93.8% | 0.87 (6 in 6.86 h) |
| 0.5 | 89.6% | 0.29 (2 in 6.86 h) |
| 0.7 | 86.5% | 0.15 (1 in 6.86 h) |
| 0.9 | 72.9% | 0 |

From 0.3 to 0.7, the false activations fall from 6 to 1, and the recall falls by 7 points. Above 0.7, the recall falls fast for little gain. For this model, a value from 0.5 to 0.7 is a good range on speech. With only a few false activations in 6.86 hours, each rate is rough: one more or one fewer changes it by 0.15 per hour.

## Change the threshold

1. Measure your start point with [Compare Wake-word Engines on Your Audio](ww-compare.md). Use your own recordings.
2. Set the threshold in the `hotwords` entry of `~/.config/mycroft/mycroft.conf`:

    ```json
    {
      "hotwords": {
        "hey_floyd": {
          "module": "ovos-ww-plugin-wakeforge",
          "model": "wakehubert_hey_floyd",
          "threshold": 0.7,
          "listen": true
        }
      }
    }
    ```

3. Measure again with the same audio. Change the threshold in small steps. Stop at the first value where the rates are acceptable to you.
4. Restart the listener:

--8<-- "snippets/restart-ovos.md"

## Other ways to get fewer false activations

A threshold change costs recall. These changes can also remove false activations:

- Train the model with more voices and sound-alike phrases. See [Train a Wake Word for Your Name](ww-own-name.md).
- Let only enrolled voices wake the assistant. See [Make OVOS Answer Only Your Voice](answer-only-your-voice.md).
- Use the pre-wake VAD against noise. See [Stop Wake-ups from the TV](ww-tv.md).

## Related pages

- [Wake-word Plugins](wake-word-plugins.md): the configuration keys of each engine.
- [Wake Word Guide](wake-word-guide.md): all the wake-word tasks.
