# OVOS Number Parser

!!! abstract "In a nutshell"
    Computers store numbers as digits (`123`), but people say them as words ("one hundred and twenty-three"). The words differ in every language. This library is the translator between the two: it can read a number out loud for the assistant to speak, or pick a number out of something you said ("set a timer for twenty-five minutes") and turn it back into digits. It also understands fractions and ordinals like "third". See the [Glossary](glossary.md) for unfamiliar terms.

`ovos-number-parser` converts numbers between digits and spoken words across many languages. It speaks a number aloud (`123` → "one hundred and twenty-three"), pulls a number out of free text ("I have twenty apples" → `20`), and detects fractions and ordinals.

**What you get in 30 seconds:**

```python
from ovos_number_parser import pronounce_number, extract_number

pronounce_number(123, "en")            # "one hundred and twenty three"
extract_number("I have twenty apples", "en")   # 20
```

Every function takes an explicit `lang` (a BCP-47 code such as `"en"` or `"pt-br"`). There is no global default language. When a language lacks a hand-written implementation for `pronounce_number`/`pronounce_ordinal`, the library falls back to [unicode-rbnf](https://github.com/rhasspy/unicode-rbnf). For functions without a fallback (`extract_number`, `is_fractional`), an unsupported language raises `NotImplementedError`. `numbers_to_digits` never raises. An unsupported language is left unchanged.

## Features

- **Pronounce Numbers:** Converts numerical values to their spoken forms (`pronounce_number`).


- **Pronounce Ordinals:** Converts numbers to their ordinal forms (`pronounce_ordinal`).


- **Pronounce Fractions:** Speaks a fraction string such as `"3/2"` (`pronounce_fraction`). Hand-written for `pt`, `ast`, `ca`, `oc`, `an`, `mwl`, `gl`, and `ro`. Every other language uses a generic fallback.


- **Extract Numbers:** Extracts a number from text (`extract_number`).


- **Words to Digits:** Rewrites spelled-out numbers in a sentence as digits (`numbers_to_digits`).


- **Detect Fractions:** Identifies exact fractional expressions (`is_fractional`).


- **Detect Ordinals:** Checks if a text input is an ordinal number (`is_ordinal`).

## Supported Languages

- yes - supported




- WIP - imperfect placeholder, usually a language agnostic implementation or external library


| Language Code           | Pronounce Number | Pronounce Ordinal | Extract Number | numbers_to_digits |
|-------------------------|------------------|-------------------|----------------|-------------------|
| `en` (English)          | yes               | WIP                | yes             | yes                |
| `kab` (Kabyle)          | yes               | yes                | yes             | yes                |
| `az` (Azerbaijani)      | yes               | WIP                | yes             | WIP                |
| `ca` (Catalan)          | yes                | yes                 | yes              | WIP                 |
| `gl` (Galician)         | yes                | yes                | yes              |  yes                  |
| `cs` (Czech)            | yes                | yes                 | yes              | WIP                 |
| `da` (Danish)           | yes                | yes                 | yes              | WIP                 |
| `de` (German)           | yes                | yes                 | yes              | yes                 |
| `es` (Spanish)          | yes                | WIP                 | yes              | WIP                 |
| `eu` (Euskara / Basque) | yes                | yes                 | yes              | WIP                 |
| `fa` (Farsi / Persian)  | yes                | yes                 | yes              | WIP                 |
| `fr` (French)           | yes                | WIP                 | yes              | WIP                 |
| `hu` (Hungarian)        | yes                | yes                 | yes              | WIP                 |
| `it` (Italian)          | yes                | WIP                | yes              | WIP                 |
| `mwl` (Mirandese)       | yes                | yes                 | yes              | yes                 |
| `nl` (Dutch)            | yes                | yes                 | yes              | WIP                 |
| `pl` (Polish)           | yes                | yes                 | yes              | WIP                 |
| `pt` (Portuguese)       | yes                | yes                 | yes              | yes                 |
| `ru` (Russian)          | yes                | WIP                 | yes              | yes                 |
| `sv` (Swedish)          | yes                | yes                 | yes              | WIP                 |
| `sl` (Slovenian)        | yes                | yes                 | yes              | WIP                 |
| `uk` (Ukrainian)        | yes                | yes                 | yes              | yes                 |


> If a language is not implemented for `pronounce_number` or `pronounce_ordinal` then [unicode-rbnf](https://github.com/rhasspy/unicode-rbnf) will be used as a fallback.

> This table is a curated subset. `pronounce_number` and `extract_number` dispatch cover ~41 languages in total (including `an`, `ar`, `ast`, `bg`, `el`, `et`, `fi`, `fy`, `he`, `hr`, `id`, `ms`, `nb`, `nn`, `no`, `oc`, `ro`, `sk`, and `tr`). See [`docs/languages.md`](https://github.com/OpenVoiceOS/ovos-number-parser/blob/dev/docs/languages.md) in the repo for the full per-language matrix.

### If your language is not listed

`pronounce_number` and `pronounce_ordinal` fall back to [unicode-rbnf](https://github.com/rhasspy/unicode-rbnf)
for a language with no hand-written module, so those two functions usually still work.
`extract_number` and `is_fractional` have no fallback: an unsupported language raises
`NotImplementedError`. `numbers_to_digits` never raises; an unsupported language is left
unchanged. See the [Supported languages](https://github.com/OpenVoiceOS/ovos-number-parser#supported-languages)
section of the repo README for the current full list.

!!! note
    Several Romance languages (`ast`, `an`, `oc`, `fr`, `it`, `ca`, `es`, `gl`, `pt`, `mwl`, `ro`) share a common `RomanceNumberExtractor`/`NumberVocabulary` engine internally, so their extraction logic stays consistent across languages that inflect numbers similarly.

## Installation

To install OVOS Number Parser, use:

```bash
pip install ovos-number-parser

```

## Usage

### Pronounce a Number

Convert a number to its spoken equivalent.

```python
def pronounce_number(number: Union[int, float], lang: str, places: int = 3, short_scale: Optional[bool] = None,
                     scientific: bool = False, ordinals: bool = False,
                     digits: Optional[DigitPronunciation] = None,
                     gender: GrammaticalGender = GrammaticalGender.MASCULINE,
                     scale: Optional[Scale] = None,
                     case: Optional[str] = None) -> str:
    """
    Convert a number to its spoken equivalent.

    Args:
        number: The number to pronounce.
        lang (str): A BCP-47 language code.
        places (int): Number of decimal places to express. Default is 3.
        short_scale (bool): DEPRECATED, use the `scale` enum instead. Short (True) or long scale (False) for large numbers. When left `None`, the language's canonical convention applies (e.g. `pt-br` short, `pt-pt` long), not an unconditional short scale.
        scientific (bool): Pronounce in scientific notation if True.
        ordinals (bool): Pronounce as an ordinal if True.
        digits (DigitPronunciation): Digit-reading style (e.g. read digit-by-digit). Honored by pt/mwl.
        gender (GrammaticalGender): Grammatical gender for languages that inflect numbers. Honored by pt/mwl.
        scale (Scale): Preferred way to select short/long scale; resolved to an effective
            scale for every language whose backend takes one.

    Returns:
        str: The pronounced number.

    Raises:
        NotImplementedError: if the language has neither an implementation nor a unicode-rbnf fallback.
    """

```

> The `digits` and `gender` arguments (`DigitPronunciation`/`GrammaticalGender`, importable from `ovos_number_parser.util`) currently only affect Portuguese (`pt`) and Mirandese (`mwl`). `scale` (`Scale`, same module) is different: every dispatch function resolves it to an effective short/long scale and threads it into the majority of language backends (English, German, Dutch, the Nordic and Slavic families, and more); only backends that take no scale parameter at all ignore it, and that set differs per function.

> `pronounce_number` also accepts a Python `complex` value and speaks it in rectangular `a+bi` form, e.g. `pronounce_number(complex(3, 2), "en")` → `"three plus two i"`. The number itself is composed from the per-language cardinal pronunciation. Only the "plus"/"minus"/"i" connectives are language-specific (English used as the default).

**Example Usage:**

```python
from ovos_number_parser import pronounce_number

# Example
result = pronounce_number(123, "en")
print(result)  # "one hundred and twenty three"

```

### Pronounce an Ordinal

Convert a number to its ordinal spoken equivalent.

```python
def pronounce_ordinal(number: Union[int, float], lang: str, short_scale: Optional[bool] = None,
                      gender: GrammaticalGender = GrammaticalGender.MASCULINE,
                      scale: Optional[Scale] = None) -> str:
    """
    Convert an ordinal number to its spoken equivalent.

    Args:
        number: The number to pronounce.
        lang (str): A BCP-47 language code.
        short_scale (bool): DEPRECATED, use the `scale` enum instead. Short (True) or long scale (False) for large numbers.
        gender (GrammaticalGender): Grammatical gender (honored by pt/mwl).

    Returns:
        str: The pronounced ordinal number.

    Raises:
        NotImplementedError: if the language has neither an implementation nor a unicode-rbnf fallback.
    """

```

Hand-written ordinal pronunciation exists for most languages in the support table above. A handful (`en`, `az`, `es`, `fr`, `it`, among others) route through the unicode-rbnf fallback instead.

**Example Usage:**

```python
from ovos_number_parser import pronounce_ordinal

# Example
result = pronounce_ordinal(5, "en")
print(result)  # "fifth"

```

### Extract a Number

Extract a number from a given text string.

```python
def extract_number(text: str, lang: str, short_scale: Optional[bool] = None, ordinals: bool = False,
                    scale: Optional[Scale] = None) -> Union[int, float, bool]:
    """
    Extract a number from text.

    Args:
        text (str): The string to extract a number from.
        lang (str): A BCP-47 language code.
        short_scale (bool): DEPRECATED, use the `scale` enum instead. Short scale if True, long scale if False.
        ordinals (bool): Consider ordinal numbers.

    Returns:
        int, float, or False: The extracted number, or False if no number found.
    """

```

**Example Usage:**

```python
from ovos_number_parser import extract_number

# Example
result = extract_number("I have twenty apples", "en")
print(result)  # 20

```

### Check for Fractional Numbers

Identify if the text contains a fractional number.

```python
def is_fractional(input_str: str, lang: str, short_scale: Optional[bool] = None,
                   scale: Optional[Scale] = None) -> Union[bool, float]:
    """
    Check if the text is a fraction.

    Args:
        input_str (str): The string to check if fractional.
        lang (str): A BCP-47 language code.
        short_scale (bool): DEPRECATED, use the `scale` enum instead. Short scale if True, long scale if False.

    Returns:
        bool or float: False if not a fraction, otherwise the fraction as a float.
    """

```

**Example Usage:**

```python
from ovos_number_parser import is_fractional

# Example
result = is_fractional("half", "en")
print(result)  # 0.5

```

### Check for Ordinals

Determine if the text contains an ordinal number.

```python
def is_ordinal(input_str: str, lang: str) -> Union[bool, float]:
    """
    Check if the text is an ordinal number.

    Args:
        input_str (str): The string to check if ordinal.
        lang (str): A BCP-47 language code.

    Returns:
        bool or float: False if not an ordinal, otherwise the ordinal as a float.
    """

```

**Example Usage:**

```python
from ovos_number_parser import is_ordinal

# Example
result = is_ordinal("third", "en")
print(result)  # 3

```

> `is_ordinal` has hand-written detection for most languages in the support table above and a generic fallback for the rest, so it rarely raises `NotImplementedError` in practice.

### Words to Digits

Rewrite spelled-out numbers inside a sentence as digits, leaving the rest of the text intact.

```python
from ovos_number_parser import numbers_to_digits

numbers_to_digits("set a timer for twenty five minutes", "en")
# "set a timer for 25 minutes"
```

```python
def numbers_to_digits(utterance: str, lang: str, scale: Optional[Scale] = None) -> str: ...
```

`scale` (`Scale.LONG` / `Scale.SHORT`, from `ovos_number_parser.util`) only matters for languages that distinguish short/long scale (e.g. `pt`/`mwl`). Hand-written rewriting is dispatched for `en`, `kab`, `ast`, `oc`, `an`, `fy`, `gl`, `de`, `pt`, `mwl`, `ro`, `bg`, `hr`, `ru`, `sk`, `id`, `ms`, `tr`, and `uk`. Every other language gets a generic word-span replacement instead. It works but is less precise about compound numerals than a hand-written implementation. No language ever raises here. One that has no parser at all is simply left unchanged.

!!! note
    Kabyle (`kab`) has two coexisting numeral systems: everyday loan-word counting (Arabic-derived above ten, e.g. `waḥed u ɛecrin` = 21) used for pronunciation, and a formalized pan-Amazigh proposal (invariable tens, descending magnitudes, no connectors) that extraction also recognizes. `kab` counts only up to 9999 and has no scale or fraction vocabulary.

### Pronounce a Fraction

Speak a fraction string such as `"3/2"`. Hand-written pronunciation exists for `pt`, `ast`, `ca`, `oc`, `an`, `mwl`, `gl`, and `ro`. Every other language routes through a generic fallback rather than raising.

```python
from ovos_number_parser import pronounce_fraction

pronounce_fraction("3/2", "pt")   # "três meios"
```

```python
def pronounce_fraction(fraction_word: str, lang: str, scale: Optional[Scale] = None) -> str: ...
```

## License

This project is licensed under the Apache License 2.0.

---
**Read next:** [Dates & Time](date-parser.md)
**Related:** [Language Names](lang-parser.md) · [Colors](color-parser.md) · [Quebra Frases](quebra-frases.md)
