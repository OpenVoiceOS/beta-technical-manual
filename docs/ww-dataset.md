# Generate a Wake-word Dataset

--8<-- "snippets/alpha-only.md"

Make a wake-word dataset from the text of the phrase only. The dataset has synthetic clips of the phrase, clips of other sounds and speech, and sound-alike phrases. You can train with it, share it, or inspect it before you train. Use this task to train a model for a phrase that has no recordings. Also use it to see and control the training data before a training run uses it.

## What you get

- Clips of the phrase, spoken by many text-to-speech voices.
- Negative clips: noise, sounds, speech and silence.
- Near-miss phrases that sound like the wake word, as hard negatives.
- A train split and a test split, as CSV files that `ww_trainer-train` reads.

## Generate the dataset

1. Install `wakeforge` in its own virtual environment:

    ```bash
    pip install --pre "wakeforge[datagen,torchcodec]"
    ```

2. Install more text-to-speech plugins if you can. Each plugin adds voices, and more voices give a model that works for more people. With only `ovos-tts-plugin-edge-tts`, the generator warns that the voices are not varied.

3. Generate the dataset:

    ```bash
    ww_trainer-datagen --wake-word "hey luna" --output-dir hey_luna --n-positive 200 \
        --no-augmentation-data --adversarial
    ```

    `--n-positive 200` and `--no-augmentation-data` make a small dataset for a first test. For a model that you use every day, remove them. The default is 1000 positive clips, and the generator then also downloads background noise, music and room echo for augmentation.

## Generate the dataset in a notebook

If your computer is slow, run the [synthetic dataset notebook](https://github.com/OpenVoiceOS/ngi0-notebooks/blob/dev/notebooks/synthetic_ww_dataset.ipynb) in a free Kaggle or Colab session. The notebook makes the clips with the OmniVoice text-to-speech model and writes CSV files that `ww_trainer-train` reads.

Do not use the archived `TigreGotico/synthetic_dataset_generator` repository. Use `wakeforge`.

## What is in the dataset

This is the dataset that `ww_trainer-quickstart --wake-word "hey luna" --n-positive 200 --no-augmentation-data` made. The quickstart runs the same generator before it trains.

| Folder | Clips | Content |
|---|---|---|
| `positives/` | 200 | "hey luna" from 37 edge-tts voices at six speaking rates, from -20% to +30%; `synthesis.csv` lists the voice and rate of each clip |
| `negatives/AudioSet/` | 200 | Everyday sounds |
| `negatives/ESC-50/` | 200 | Environmental sounds |
| `negatives/NAR/` | 200 | Sounds in 42 classes, for example a refrigerator alarm |
| `negatives/not-wake-words-speech-en/` | 200 | English speech without the wake word |
| `negatives/adversarial/` | 60 | Near-miss phrases, for example "hez luna" and "ey vluna" |
| `negatives/silence/` | 900 | Digital silence and low noise at -60 dBFS and -40 dBFS |
| `positives/processed/`, `negatives/processed/` | 2702 | Fixed-length windows cut from the clips above; the training uses these |

The dataset used 276 MB of disk. `train/metadata.csv` has 2881 rows (160 positive) and `test/metadata.csv` has 721 rows (40 positive). Each row is a file path and a label, 1 for the wake word and 0 for all other audio.

## Make better sound-alike phrases

Without a language model, `--adversarial` makes near-miss phrases by changing two or three letters in the phrase. Some of them, for example "hezzjuna", are not phrases that a person says. With a language model, the generator also asks the model for phrases that sound like the wake word. Point the generator at an Ollama server:

```bash
ww_trainer-datagen --wake-word "hey luna" --output-dir hey_luna --adversarial \
    --llm-url http://localhost:11434 --llm-model gemma3:4b
```

You can also write the phrases yourself, one for each line, and give the file with `--adversarial-file`. Use the phrases that wake your assistant by mistake. To find them, see [Stop Wake-ups from the TV](ww-tv.md).

## Train on the dataset

Give the two CSV files to the trainer:

```bash
ww_trainer-train --wake-word "hey luna" --metadata hey_luna/train/metadata.csv \
    --test-metadata hey_luna/test/metadata.csv --output-dir hey_luna/model
```

[Train a Wake Word for Your Name](ww-own-name.md) does the generation and the training in one command.

## Know the limits

- Synthetic voices are cleaner than a person in a room. Test the model on recordings of real people before you use it every day. See [Compare Wake-word Engines on Your Audio](ww-compare.md).
- A dataset from few voices gives a model that knows few voices. Add text-to-speech plugins, or give recordings of your household with `--vc-refs` to make voice-converted copies.
- The negatives come from public datasets on the Hugging Face Hub. The first run downloads them, so it needs a network connection and some time.

## Related pages

- [Train a Wake Word for Your Name](ww-own-name.md)
- [Compare Wake-word Engines on Your Audio](ww-compare.md)
- [Wake Word Guide](wake-word-guide.md)
