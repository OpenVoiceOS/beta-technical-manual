# ovos-date-parser

!!! abstract "In a nutshell"
    This is a helper that translates between everyday date and time phrases and the precise dates a computer understands. It works both ways. It can read "next Friday at 3pm" and pin down the exact moment, and it can turn an exact time back into natural words like "three o'clock". It handles many languages, which lets the assistant understand and speak dates the way you do. See the [Number parser](number-parser.md) for the same idea applied to numbers, or the [Glossary](glossary.md) for terms.

`ovos-date-parser` is a multilingual library for turning human date/time phrases into Python objects (`extract_datetime`, `extract_duration`) and for turning `datetime`/`timedelta` objects back into natural spoken or written text (`nice_time`, `nice_date`, `nice_duration`, ...).

**What you get in 30 seconds:**

```python
from ovos_date_parser import extract_datetime, nice_time
from datetime import datetime

extract_datetime("remind me next friday at 3pm", lang="en")
# [datetime(...), 'remind me']    -> parsed datetime + leftover text

nice_time(datetime(2024, 1, 1, 15, 0), lang="en")   # "three o'clock"
```

Every function takes an explicit `lang` (BCP-47 code). The readers `extract_datetime` and `extract_duration` go through the `chronologia` library for every language in the set `CHRONOLOGIA_LOCALES`. For a language outside that set, `extract_datetime` falls back to the [dateparser](https://dateparser.readthedocs.io/en/latest/) library, and `extract_duration` returns `(None, text)`. Only the `nice_*` writers are local to `ovos-date-parser`. They fall back to a generic English-style implementation when a language-specific one is missing.

`ovos-date-parser` also re-exports `extract_timespan` and `explain` from `chronologia`, the reckoning core (astronomical dates, calendars, eras, cycles).

## Features

- **Date and Time Extraction**: extract specific dates and times from natural language phrases in various languages.


- **Duration Parsing**: parse phrases that indicate a span of time, such as "two hours and fifteen minutes."


- **Friendly Time Formatting**: format time for human-friendly output, supporting both 12-hour and 24-hour formats.


- **Relative Time Descriptions**: generate relative descriptions (for example, "tomorrow," "in three days") for given dates.


- **Multilingual Support**: extraction and formatting methods for multiple languages, such as Portuguese, Spanish,
  French, and German.

- **Spans**: `extract_datetime_spans` and `extract_duration_spans` return each expression with its character offsets.

## Installation

```bash
pip install ovos-date-parser

```

### Languages Supported

`ovos-date-parser` supports a wide array of languages, each with its own set of methods for handling natural language
time expressions.

**Parse**

`extract_datetime` and `extract_duration` read every language in `CHRONOLOGIA_LOCALES` through `chronologia`. This command prints the set:

```bash
python -c "from ovos_date_parser import CHRONOLOGIA_LOCALES; print(' '.join(sorted(CHRONOLOGIA_LOCALES)))"
```

For a language outside the set, `extract_datetime` uses [dateparser](https://dateparser.readthedocs.io/en/latest/), and `extract_duration` returns `(None, text)`.

**Format**

In the table, "yes" means a language-specific implementation. "WIP" means an imperfect, usually language-agnostic placeholder. `nice_relative_time` is WIP for every listed language except `eu`, which has a full implementation.

| Language | `nice_date`<br>`nice_date_time`<br>`nice_day` <br>`nice_weekday` <br>`nice_month` <br>`nice_year` <br>`get_date_strings` | `nice_time` | `nice_relative_time` | `nice_duration` |
|----------|--------------------------------------------------------------------------------------------------------------------------|-------------|----------------------|-----------------|
| pt       | yes                                                                                                                        | yes           | WIP                   | yes               |
| es       | yes                                                                                                                        | yes           | WIP                   | yes               |
| fr       | yes                                                                                                                        | yes           | WIP                   | yes               |
| it       | yes                                                                                                                        | yes           | WIP                   | yes               |
| de       | yes                                                                                                                        | yes           | WIP                   | yes               |
| nl       | yes                                                                                                                        | yes           | WIP                   | yes               |
| da       | yes                                                                                                                        | yes           | WIP                   | yes               |
| kab      | yes                                                                                                                        | yes           | WIP                   | yes               |
| an       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ar       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ast      | yes                                                                                                                        | yes           | WIP                   | yes               |
| az       | yes                                                                                                                        | yes           | WIP                   | yes               |
| bg       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ca       | yes                                                                                                                        | yes           | WIP                   | yes               |
| cs       | yes                                                                                                                        | yes           | WIP                   | yes               |
| el       | yes                                                                                                                        | yes           | WIP                   | yes               |
| en       | yes                                                                                                                        | yes           | WIP                   | yes               |
| et       | yes                                                                                                                        | yes           | WIP                   | yes               |
| eu       | yes                                                                                                                        | yes           | yes                    | yes               |
| fa       | yes                                                                                                                        | yes           | WIP                   | yes               |
| fi       | yes                                                                                                                        | yes           | WIP                   | yes               |
| fy       | yes                                                                                                                        | yes           | WIP                   | yes               |
| gl       | yes                                                                                                                        | yes           | WIP                   | yes               |
| he       | yes                                                                                                                        | yes           | WIP                   | yes               |
| hr       | yes                                                                                                                        | yes           | WIP                   | yes               |
| hu       | yes                                                                                                                        | yes           | WIP                   | yes               |
| id       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ms       | yes                                                                                                                        | yes           | WIP                   | yes               |
| nb/no    | yes                                                                                                                        | yes           | WIP                   | yes               |
| nn       | yes                                                                                                                        | yes           | WIP                   | yes               |
| oc       | yes                                                                                                                        | yes           | WIP                   | yes               |
| pl       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ro       | yes                                                                                                                        | yes           | WIP                   | yes               |
| ru       | yes                                                                                                                        | yes           | WIP                   | yes               |
| sk       | yes                                                                                                                        | yes           | WIP                   | yes               |
| sl       | yes                                                                                                                        | yes           | WIP                   | yes               |
| sv       | yes                                                                                                                        | yes           | WIP                   | yes               |
| tr       | yes                                                                                                                        | yes           | WIP                   | yes               |
| uk       | yes                                                                                                                        | yes           | WIP                   | yes               |

### If your language is not listed

`extract_datetime` falls back to the [dateparser](https://dateparser.readthedocs.io/en/latest/)
library for a language outside `CHRONOLOGIA_LOCALES`, so it still returns a result rather
than raising. `extract_duration` returns `(None, text)` for such a language. The `nice_*` formatters (`nice_time`, `nice_date`, `nice_relative_time`, ...) fall
back to a generic, English-style implementation when no language-specific one exists.

## Usage

### Date and Time Extraction

Extract specific dates and times from a phrase. This function identifies date-related terms in natural language and
returns both the datetime object and any remaining text.

```python
from ovos_date_parser import extract_datetime

from datetime import datetime
from zoneinfo import ZoneInfo

anchor = datetime(2024, 1, 1, 9, 0, tzinfo=ZoneInfo("UTC"))
result = extract_datetime("Meet me next Friday at 3pm", lang="en", anchorDate=anchor)
print(result)
# [datetime.datetime(2024, 1, 5, 15, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'Meet me']
```

!!! note
    For a language in `CHRONOLOGIA_LOCALES`, `extract_datetime` returns a 2-item `list`, `[datetime, leftover_text]`. The dateparser fallback returns a 2-item `tuple`. Both unpack the same way. The leftover text keeps the case that the user typed. When no date is found, the return value is `None`.

### Duration Extraction

Identify duration phrases in text and convert them into a `timedelta` object. This can parse common human-friendly
duration expressions like "30 minutes" or "two and a half hours."

```python
from ovos_date_parser import extract_duration

duration, remainder = extract_duration("It will take about 2 hours and 30 minutes", lang="en")
print(repr(duration))  # datetime.timedelta(seconds=9000)
print(remainder)       # It will take about

```

!!! note
    The remainder keeps whatever surrounds the extracted duration phrase verbatim. A
    connective word ("and" in English, "y" in Spanish) or comma left stranded between two
    separately-consumed number groups can end up in the remainder too. Clean up the
    remainder yourself before you display or re-parse it.

`extract_duration` also accepts two keyword-only arguments:

- **`resolution`** (`DurationResolution`, default `TIMEDELTA`): controls the return type. `TIMEDELTA` returns a `timedelta`. `RELATIVEDELTA` returns a `dateutil.relativedelta` that holds the length in days. A month or a year counts as the days it has from the day of the call. A single-unit total such as `TOTAL_SECONDS`/`TOTAL_MINUTES` is returned as a `float`.
- **`replace_token`** (`str`, default `""`): the string each consumed duration phrase is replaced with in the remainder, marking where it was found instead of stripping it out.

```python
from ovos_date_parser import extract_duration
from ovos_date_parser.duration import DurationResolution

extract_duration("wait two weeks", lang="en",
                 resolution=DurationResolution.RELATIVEDELTA)
# (relativedelta(days=+14), 'wait')

extract_duration("wait two weeks", lang="en", replace_token="<d>")
# (datetime.timedelta(days=14), 'wait <d>')
```

### Find every expression with its offsets

`extract_datetime_spans` and `extract_duration_spans` return a list of `DateTimeSpan` or `DurationSpan` objects. Each object has `start`, `end`, `surface` and `value`. An expression with framing words also comes back as its core.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from ovos_date_parser import extract_datetime_spans, extract_duration_spans

anchor = datetime(2024, 1, 1, 9, 0, tzinfo=ZoneInfo("UTC"))
extract_duration_spans("wait two hours and thirty minutes", "en")
# [DurationSpan(start=5, end=33, surface='two hours and thirty minutes', value=datetime.timedelta(seconds=9000))]

extract_datetime_spans("next friday at 5 pm", "en", anchor_date=anchor)
# [DateTimeSpan(start=0, end=19, surface='next friday at 5 pm', value=datetime.datetime(2024, 1, 5, 17, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))),
#  DateTimeSpan(start=5, end=19, surface='friday at 5 pm', value=datetime.datetime(2024, 1, 5, 17, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')))]
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

anchor = datetime(2024, 1, 1, 9, 0)
relative_time = nice_relative_time(anchor + timedelta(days=1), anchor, lang="en")
print(relative_time)  # "twenty four hours"

```

> The generic implementation speaks the rounded difference as words, such as `"two hours"`, `"twenty four hours"`, or `"seven days"`, using `pronounce_number` internally (it does not produce words like "tomorrow"). Basque (`eu`) is the only language with a dedicated `nice_relative_time` implementation. Everything else uses the generic one.

### Format a date for speech

Beyond `nice_time` and `nice_relative_time`, the library exports a family of
formatters that turn a `datetime` into speakable text:

```python
def nice_date(dt, lang, now=None, include_weekday=True): ...
def nice_date_time(dt, lang, now=None, use_24hour=False, ...): ...
def nice_day(dt, lang, date_format='DMY', include_month=True): ...
def nice_weekday(dt, lang): ...
def nice_month(dt, lang, date_format='MDY'): ...
def nice_year(dt, lang, bc=False, ad=False): ...
def nice_duration(duration, lang, ...): ...
def get_date_strings(dt, lang, date_format=None, time_format="full"): ...
```

`nice_date` speaks a full date (relative to `now` when given, e.g. "tomorrow");
`nice_date_time` appends the spoken time; `nice_duration` speaks a
`timedelta`/seconds value; `get_date_strings` returns a dict of display strings
(for GUIs) rather than speakable prose. Per-language support for these is the
`nice_date` family column in the Format table above.

---
**Read next:** [Colors](color-parser.md)
**Related:** [Numbers](number-parser.md) · [Language Names](lang-parser.md) · [Quebra Frases](quebra-frases.md)
