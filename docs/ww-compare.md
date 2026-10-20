# Compare Wake-word Engines on Your Audio

--8<-- "snippets/alpha-only.md"

This page measures wake-word engines on recordings that you supply. It gives the recall and the false activations per hour of each engine on the same audio.

## Who this is for

You have two or more engines that can detect your phrase. The [benchmark board](ww-pick-engine.md) uses synthetic voices. You want numbers for your voices, your microphone and your room.

## What you get

- One line per engine: recall on your wake-word clips, and false activations per hour on your other audio.
- A script that runs any wake-word plugin with any configuration.

## Collect the audio

1. Make a folder `positives/`. Put one WAV file in it for each time a person says the wake word. Use the device microphone. 50 clips from several people is a good start.
2. Make a folder `negatives/`. Put WAV files of audio with no wake word in it: TV, radio, talk in the room. One hour or more gives a useful false-activation rate.
3. Convert all the files to 16 kHz mono, for example:

    ```bash
    ffmpeg -i in.wav -ar 16000 -ac 1 positives/clip01.wav
    ```

## Score an engine

1. Save this script as `ww_score.py`:

    ```python
    """Score a wake-word plugin on folders of WAV files: recall and false activations per hour."""
    import json
    import sys
    from pathlib import Path

    import numpy as np
    import soundfile as sf
    from ovos_plugin_manager.wakewords import load_wake_word_plugin

    CHUNK = 1024  # samples per chunk, 64 ms at 16 kHz


    def detections(engine, path: Path) -> int:
        audio, rate = sf.read(path, dtype="int16", always_2d=True)
        if rate != 16000:
            sys.exit(f"{path} is {rate} Hz; convert it to 16 kHz mono first")
        silence = np.zeros(16000, dtype=np.int16)
        audio = np.concatenate([silence, audio[:, 0], silence])
        found = 0
        for start in range(0, len(audio) - CHUNK + 1, CHUNK):
            engine.update(audio[start:start + CHUNK].tobytes())
            found += bool(engine.found_wake_word())
        return found


    module, config, positives, negatives = sys.argv[1], json.loads(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    engine = load_wake_word_plugin(module)("my_wake_word", config=config)
    pos = sorted(positives.glob("*.wav"))
    neg = sorted(negatives.glob("*.wav"))
    hits = sum(detections(engine, p) > 0 for p in pos)
    false = sum(detections(engine, n) for n in neg)
    hours = sum(sf.info(n).duration + 2 for n in neg) / 3600  # each file gets 2 s of silence
    print(f"{module}: recall {hits}/{len(pos)} = {hits / len(pos):.1%}, "
          f"false activations {false} in {hours:.2f} h = {false / hours:.2f}/h")
    ```

2. Run it once for each engine. The second argument is the same JSON that goes in the `hotwords` entry of `mycroft.conf`, without `module`:

    ```bash
    python ww_score.py ovos-ww-plugin-wakeforge '{"model": "wakehubert_hey_floyd"}' positives/ negatives/
    python ww_score.py ovos-ww-plugin-wakeforge-zeroshot '{"ipa": "hˈeɪ flˈɔɪd"}' positives/ negatives/
    ```

## Example result

These lines come from the commands above. The positives are 96 recordings of "hey floyd" by people from the OVOS community. The negatives are 30 minutes of read English speech from LibriSpeech test-clean. Speech is the audio that is most like a wake word, so this is a hard test.

```text
ovos-ww-plugin-wakeforge: recall 90/96 = 93.8%, false activations 1 in 0.64 h = 1.56/h
ovos-ww-plugin-wakeforge-zeroshot: recall 19/96 = 19.8%, false activations 0 in 0.64 h = 0.00/h
```

The trained model `wakehubert_hey_floyd` finds the most wake words, with one false activation in the 30 minutes. The zero-shot engine has no false activations, but at its default threshold it finds only one wake word in five from these voices. Its `threshold` changes this a lot:

| Zero-shot `threshold` | Recall | False activations per hour |
|---|---|---|
| -0.15 (default for "hey floyd") | 19.8% | 0 |
| -0.3 | 96.9% | 4.68 |
| -0.45 | 100% | 184 |
| -0.6 | 100% | 741 |

## Read the result

- Compare engines only on the same folders. A rate from different audio is a different test.
- A small negative set gives a rough rate. With 30 minutes, one false activation is 2 per hour. Use more audio before you decide between two engines that are near each other.
- The script feeds audio straight to the engine. It does not use the pre-wake VAD or the verifiers. To measure those, see [Stop Wake-ups from the TV](ww-tv.md).

## Related pages

- [Pick a Wake-word Engine from the Benchmark](ww-pick-engine.md)
- [Tune False Activations](ww-tune.md)
- [Wake Word Guide](wake-word-guide.md)
