# ovos-date-parser

!!! abstract "In a nutshell"
    This is a helper that translates between everyday date and time phrases and the precise dates a computer understands. It works both ways. It can read "next Friday at 3pm" and pin down the exact moment, and it can turn an exact time back into natural words like "three o'clock". It handles many languages, which lets the assistant understand and speak dates the way you do. See the [Number parser](number-parser.md) for the same idea applied to numbers, or the [Glossary](glossary.md) for terms.

`ovos-date-parser` is a multilingual library for turning human date/time phrases into Python objects (`extract_datetime`, `extract_duration`) and for turning `datetime`/`timedelta` objects back into natural spoken or written text (`nice_time`, `nice_date`, `nice_duration`, ...).

**What you get in 30 seconds:**

```python
from ovos_date_parser import extract_datetime, nice_time
from datetime import datetime

extract_datetime("remind me next friday at 3pm", lang="en")
# [datetime(...), "remind me"]    -> parsed datetime + leftover text, as a 2-item list

nice_time(datetime(2024, 1, 1, 15, 0), lang="en")   # "three o'clock"
```

Every function takes an explicit `lang` (BCP-47 code). For `extract_datetime`, languages without a dedicated implementation fall back to the [dateparser](https://dateparser.readthedocs.io/en/latest/) library. The `nice_*` formatters fall back to a language-agnostic English-style generic implementation when a language-specific one is missing.

## Features

- **Date and Time Extraction**: extract specific dates and times from natural language phrases in various languages.


- **Duration Parsing**: parse phrases that indicate a span of time, such as "two hours and fifteen minutes."


- **Friendly Time Formatting**: format time for human-friendly output, supporting both 12-hour and 24-hour formats.


- **Relative Time Descriptions**: generate relative descriptions (for example, "tomorrow," "in three days") for given dates.


- **Multilingual Support**: extraction and formatting methods for multiple languages, such as English, Spanish,
  French, and German.

## Installation

```bash
pip install ovos-date-parser

```

### Languages Supported

`ovos-date-parser` supports a wide array of languages, each with its own set of methods for handling natural language
time expressions.

- ✅ - supported


- ❌ - not supported


- 🚧 - imperfect placeholder, usually a language agnostic implementation or external library

**Parse**

| Language | `extract_duration` | `extract_datetime` |
|----------|--------------------|--------------------|
| an       | ✅                  | ✅                  |
| ar       | ✅                  | ✅                  |
| ast      | ✅                  | ✅                  |
| az       | ✅                  | ✅                  |
| bg       | ✅                  | ✅                  |
| ca       | ✅                  | ✅                  |
| cs       | ✅                  | ✅                  |
| da       | ✅                  | ✅                  |
| de       | ✅                  | ✅                  |
| el       | ❌                  | ✅                  |
| en       | ✅                  | ✅                  |
| es       | ✅                  | ✅                  |
| et       | ✅                  | ✅                  |
| eu       | ✅                  | ✅                  |
| fa       | ✅                  | ✅                  |
| fi       | ✅                  | ✅                  |
| fr       | ✅                  | ✅                  |
| fy       | ✅                  | ✅                  |
| gl       | ✅                  | ✅                  |
| he       | ❌                  | ✅                  |
| hr       | ✅                  | ✅                  |
| hu       | ✅                  | ✅                  |
| id       | ❌                  | ✅                  |
| it       | ✅                  | ✅                  |
| kab      | ✅                  | ✅                  |
| ms       | ❌                  | ✅                  |
| nb/no    | ✅                  | ✅                  |
| nl       | ✅                  | ✅                  |
| nn       | ✅                  | ✅                  |
| oc       | ✅                  | ✅                  |
| pl       | ✅                  | ✅                  |
| pt       | ✅                  | ✅                  |
| ro       | ✅                  | ✅                  |
| ru       | ✅                  | ✅                  |
| sk       | ✅                  | ✅                  |
| sl       | ✅                  | ✅                  |
| sv       | ✅                  | ✅                  |
| tr       | ❌                  | ✅                  |
| uk       | ✅                  | ✅                  |


> 💡 If a language is not implemented for `extract_datetime`, [dateparser](https://dateparser.readthedocs.io/en/latest/) is used as a fallback. Most `extract_duration` languages are driven by a shared lexicon engine (`DURATION_LEXICONS` in `ovos_date_parser/duration.py`), so new languages are added declaratively. `ar`, `ast`, `kab`, `fa`, and `sv` have standalone extractors instead.

**Format**

| Language | `nice_date`<br>`nice_date_time`<br>`nice_day` <br>`nice_weekday` <br>`nice_month` <br>`nice_year` <br>`get_date_strings` | `nice_time` | `nice_relative_time` | `nice_duration` |
|----------|--------------------------------------------------------------------------------------------------------------------------|-------------|----------------------|-----------------|
| an       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ar       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ast      | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| az       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| bg       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ca       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| cs       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| da       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| de       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| el       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| en       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| es       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| et       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| eu       | ✅                                                                                                                        | ✅           | ✅                    | ✅               |
| fa       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| fi       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| fr       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| fy       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| gl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| he       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| hr       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| hu       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| id       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| it       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| kab      | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ms       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| nb/no    | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| nl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| nn       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| oc       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| pl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| pt       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ro       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| ru       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| sk       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| sl       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| sv       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| tr       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |
| uk       | ✅                                                                                                                        | ✅           | 🚧                   | ✅               |

## Usage

### Date and Time Extraction

Extract specific dates and times from a phrase. This function identifies date-related terms in natural language and
returns both the datetime object and any remaining text.

```python
from ovos_date_parser import extract_datetime

result = extract_datetime("Meet me next Friday at 3pm", lang="en")
print(result)  # [datetime object, "meet me"]

```

!!! note
    `extract_datetime` returns a 2-item `list`, `[datetime, leftover_text]`, not a tuple. The leftover text is lowercased.

### Duration Extraction

Identify duration phrases in text and convert them into a `timedelta` object. This can parse common human-friendly
duration expressions like "30 minutes" or "two and a half hours."

```python
from ovos_date_parser import extract_duration

duration, remainder = extract_duration("It will take about 2 hours and 30 minutes", lang="en")
print(duration)   # timedelta(hours=2, minutes=30)
print(remainder)  # "It will take about"

```

!!! note
    The remainder keeps whatever surrounds the extracted duration phrase verbatim, but a connective word ("and" in English, "y" in Spanish) or comma left stranded between two consumed number groups is stripped along with them. A connector that still joins unconsumed text on either side is left alone: `extract_duration("two hours and rest and relax", lang="en")` returns remainder `"and rest and relax"`.

`extract_duration` also accepts two keyword-only arguments, but only for languages on the shared lexicon engine (the ✅ `extract_duration` rows above except the standalone `ar`, `ast`, `kab`, `fa`, `sv` extractors). Passing them for any other language raises `NotImplementedError`:

- **`resolution`** (`DurationResolution`, default `TIMEDELTA`): controls the return type. `TIMEDELTA` returns a `timedelta`, `RELATIVEDELTA` returns a calendar-accurate `dateutil.relativedelta` (so "2 months" stays 2 months rather than a fixed number of days), or a single-unit total such as `TOTAL_SECONDS`/`TOTAL_MINUTES` is returned as a `float`.
- **`replace_token`** (`str`, default `""`): the string each consumed duration phrase is replaced with in the remainder, marking where it was found instead of stripping it out.

```python
from ovos_date_parser import extract_duration
from ovos_date_parser.duration import DurationResolution

extract_duration("wait two months", lang="en",
                 resolution=DurationResolution.RELATIVEDELTA)
# (relativedelta(months=+2), "wait")
```

### Formatting Time

Generate a natural-sounding time format suitable for voice or display in different languages, allowing customization for
speech or written text.

```python
from ovos_date_parser import nice_time
from datetime import datetime

dt = datetime(2024, 1, 1, 15, 0)
formatted_time = nice_time(dt, lang="en", speech=True, use_24hour=False)
print(formatted_time)  # "three o'clock"

```

### Relative Time Descriptions

Create relative phrases for describing dates and times in relation to the current moment or a reference datetime.

```python
from ovos_date_parser import nice_relative_time
from datetime import datetime, timedelta

relative_time = nice_relative_time(datetime.now() + timedelta(days=1), datetime.now(), lang="en")
print(relative_time)  # "twenty four hours"

```

> The generic implementation speaks the rounded difference as words, such as `"two hours"`, `"twenty four hours"`, or `"seven days"`, using `pronounce_number` internally (it does not produce words like "tomorrow"). Basque (`eu`) is the only language with a dedicated `nice_relative_time` implementation. Everything else uses the generic one.

!!! note "Upcoming"
    Span extraction (`DateSpan`) and astronomical or era-based dates are in
    development. This work lives on feature branches of
    [OpenVoiceOS/ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)
    and is not part of the released API yet.

## Related Projects

- [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser): for handling numbers


- [ovos-lang-parser](https://github.com/OpenVoiceOS/ovos-lang-parser): for handling language names


- [ovos-color-parser](https://github.com/OpenVoiceOS/ovos-color-parser): for handling colors
