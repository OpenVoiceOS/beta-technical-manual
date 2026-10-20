# Train a Wake Word for Your Name

--8<-- "snippets/alpha-only.md"

Make the assistant wake up on a phrase that you select, for example "hey Luna". There are two methods. Each has measured rates. The first needs no training and works in minutes. The second trains a model on synthetic speech. Use this task to call the assistant by a name that no ready model knows, when you have no recordings of other people who say it.

## What you get

- A wake word from its pronunciation only, with the zero-shot engine.
- A trained wake-word model, made from text with `wakeforge`, that the listener runs.

## Method 1: zero-shot, no training

The `ovos-ww-plugin-wakeforge-zeroshot` engine compares the phones that it hears with the phones of your phrase. It needs no model for the phrase, only its pronunciation as an IPA string. [Change the Wake Word Without Training](change-wake-word-without-training.md) gives the steps.

### How well zero-shot works

These rates come from 30 minutes of read English speech from LibriSpeech test-clean as negatives:

| Phrase and voices | Clips | Recall | False activations per hour |
|---|---|---|---|
| "hey luna", 37 edge-tts voices | 50 | 94.0% | 0 |
| "hey luna", 10 other edge-tts voices | 10 | 100% | 0 |
| "hey floyd", real people, default threshold -0.15 | 96 | 19.8% | 0 |
| "hey floyd", real people, `"threshold": -0.3` | 96 | 96.9% | 4.68 |

The engine finds the phrase in clean synthetic speech. Real voices in real rooms score lower, so the default threshold can miss most of them. If the engine misses you, set `threshold` lower in steps of 0.05, for example `-0.2`, then `-0.25`. Each step gives more false activations. At `-0.45`, the engine woke up 184 times per hour on speech. See [Tune False Activations](ww-tune.md).

## Method 2: train a model from text

`wakeforge` makes a dataset with text-to-speech voices, trains a small model on it and exports the model as two ONNX files. See [Generate a Wake-word Dataset](ww-dataset.md) for the data part.

1. Install `wakeforge` in its own virtual environment. It needs PyTorch, FFmpeg and about 3 GB of RAM:

    ```bash
    pip install --pre "wakeforge[datagen,torchcodec]"
    ```

2. Train the model:

    ```bash
    ww_trainer-quickstart --wake-word "hey luna" --output-dir hey_luna
    ```

    To check your setup first, add `--n-positive 200 --no-augmentation-data`. That run takes about 16 minutes on a laptop CPU, but its model is not usable. At a threshold that found 88% of the wake words, it woke up 520 times per hour on read speech.

    The default run took 3 hours 18 minutes on a laptop CPU and wrote a 2.3 GB dataset. It ends with two lines like these:

    ```text
    ✓ Dataset: /home/you/hey_luna/dataset
    ✓ Model:   /home/you/hey_luna/model/best_f1.onnx  (F1=0.978)
    ```

    The model folder holds `best_f1.onnx` and `best_f1_featurizer.onnx`. You need both files.

3. Copy the two ONNX files to the device, for example to `~/hey_luna/`.

4. Add the wake word to `~/.config/mycroft/mycroft.conf`:

    ```json
    {
      "listener": {"wake_word": "hey_luna"},
      "hotwords": {
        "hey_luna": {
          "module": "ovos-ww-plugin-wakeforge",
          "model": "~/hey_luna/best_f1.onnx",
          "featurizer": "~/hey_luna/best_f1_featurizer.onnx",
          "threshold": 0.2,
          "listen": true
        }
      }
    }
    ```

5. Restart the listener and say the phrase 20 times. Count the detections.

The plugin does not get a threshold from the training run. At the plugin default threshold of 0.5, the "hey luna" model from the default run found none of the wake words. Set `threshold` to 0.2, as in the example above. The table shows the results for that model. The false activations are from 30 minutes of read English speech.

| Setting | Test voices | Voices not in training | False activations per hour |
|---|---|---|---|
| plugin default, threshold 0.5 | 0 of 60 | 0 of 10 | 0 |
| `"threshold": 0.35` | 33 of 60 | 1 of 10 | 0 |
| `"threshold": 0.2` | 60 of 60 | 9 of 10 | 28 |

A model that wakes up 28 times per hour during speech is too sensitive for a room where people talk all day. To make fewer false activations, add a speaker verifier, see [Make OVOS Answer Only Your Voice](answer-only-your-voice.md). You can also try [Method 1](#method-1-zero-shot-no-training) first: zero-shot found "hey luna" from voices it did not know with no false activations.

## Make the model better

- Install more text-to-speech plugins before you train. With only `ovos-tts-plugin-edge-tts`, `wakeforge` warns that the voices are not varied.
- Measure the model on your own recordings with [Compare Wake-word Engines on Your Audio](ww-compare.md).
- Train in a free Kaggle notebook with the [Kaggle quickstart notebook](https://github.com/OpenVoiceOS/ngi0-notebooks/blob/dev/notebooks/kaggle_quickstart_ww.ipynb), if your computer is slow.

## Related pages

- [Generate a Wake-word Dataset](ww-dataset.md)
- [Tune False Activations](ww-tune.md)
- [Wake-word Plugins](wake-word-plugins.md)
- [Wake Word Guide](wake-word-guide.md)
