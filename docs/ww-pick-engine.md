# Pick a Wake-word Engine from the Benchmark

--8<-- "snippets/alpha-only.md"

Use the public Plugin Arena board to choose a wake-word engine and its configuration for a phrase. Use this task for a wake word that already has trained models, such as "hey Jarvis" or "Alexa", when several engines can detect it. The board shows which configuration makes fewer errors, and which runs faster.

## What you get

- A ranked list of the engine configurations for your phrase.
- The exact `hotwords` configuration of the configuration that you select.

## How the board ranks engines

The [Plugin Arena](plugin-arena.md) runs each engine configuration, called a competitor, on a labelled evaluation set. Each clip is a wake word, a different phrase, or a phrase that sounds almost the same. The arena feeds the clips to the plugin in 80 ms chunks. Then it compares the competitors in pairs, called battles, and ranks them on two ladders:

- `error_rate`: the share of clips with a wrong decision. A competitor with fewer errors wins the battle.
- `rtf`: the real-time factor, the processing time divided by the audio time. A faster competitor wins the battle.

A competitor is a full configuration. The same plugin with a different threshold is a different competitor.

## Find the best configuration for your phrase

1. Get the English (US) wake-word board:

    ```bash
    curl -s https://openvoiceos.github.io/ovos-plugin-arena/data/leaderboard-wake_word-en-US.json -o board.json
    ```

2. List the competitors for your phrase on the `error_rate` ladder. This example uses "jarvis":

    ```bash
    jq -r '.metric_ladders.error_rate.entries[]
           | select(.competitor_id | test("jarvis"))
           | [.rank, .competitor_id, .wins, .losses] | @tsv' board.json
    ```

    ```text
    3	openwakeword-hey-jarvis	746	162
    4	microwakeword-hey-jarvis	613	131
    5	microwakeword-hey-jarvis-silero	613	137
    7	microwakeword-hey-jarvis-thr07	429	132
    13	vosk-ww-jarvis	157	170
    25	precise-onnx-jarvis	0	214
    ```

3. Do the same query on the `rtf` ladder. Replace `error_rate` with `rtf`:

    ```text
    1	microwakeword-hey-jarvis
    2	microwakeword-hey-jarvis-thr07
    3	microwakeword-hey-jarvis-silero
    10	precise-onnx-jarvis
    22	vosk-ww-jarvis
    36	openwakeword-hey-jarvis
    ```

    In this example, `openwakeword-hey-jarvis` makes the fewest errors and is the slowest. `microwakeword-hey-jarvis` is second for errors and first for speed. On a Raspberry Pi or a satellite, speed can be more important.

4. Make sure that the phrase is the one you will say. `precise-onnx-jarvis` detects "jarvis", not "hey jarvis".

5. Read the board status:

    ```bash
    jq '{generated_at, provisional, vote_count, human_vote_count}' board.json
    ```

    `provisional: true` tells you that the ranks can change. `human_vote_count: 0` tells you that only the automatic battles set the ranks.

## Use the configuration

1. Get the configuration of the competitor that you selected:

    ```bash
    curl -s https://raw.githubusercontent.com/OpenVoiceOS/ovos-plugin-arena/dev/registry/competitors/wake_word/microwakeword-hey-jarvis.json | jq .config
    ```

    ```json
    {
      "listener": {
        "wake_word": "hey_jarvis"
      },
      "hotwords": {
        "hey_jarvis": {
          "module": "ovos-ww-plugin-microwakeword",
          "listen": true,
          "model": "https://github.com/esphome/micro-wake-word-models/raw/main/models/hey_jarvis.tflite",
          "model_name": "hey_jarvis",
          "model_version": 1,
          "probability_cutoff": 0.5,
          "sliding_window_size": 10,
          "refractory_frames": 40
        }
      }
    }
    ```

2. Install the plugin that `module` names. Copy the `listener` and `hotwords` blocks into `~/.config/mycroft/mycroft.conf`.

3. Restart the listener:

--8<-- "snippets/restart-ovos.md"

## Limits of the board

- The board contains only the phrases and engines that have a competitor file. If your phrase is not on the board, read [Train a Wake Word for Your Name](ww-own-name.md).
- The evaluation clips are synthetic voices. Your voice, microphone and room are different. Measure the configuration on your own audio before you depend on it: see [Compare Wake-word Engines on Your Audio](ww-compare.md).
- The board does not count false activations per hour of household audio. See [Tune False Activations](ww-tune.md).

## Related pages

- [Plugin Arena](plugin-arena.md): how the arena works and how to add a competitor.
- [Wake-word Plugins](wake-word-plugins.md): the configuration keys of each engine.
- [Wake Word Guide](wake-word-guide.md): all the wake-word tasks.
