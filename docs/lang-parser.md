
# ovos-lang-parser

!!! abstract "In a nutshell"
    This is a small helper that connects the *name* of a language to the short code computers use for it. When you say "switch to Spanish", it figures out you mean the language tagged `es`; and when the assistant needs to mention a language out loud, it turns that code back into the spoken name "Spanish". That two-way translation is what lets you change languages just by asking. See the [Glossary](glossary.md) for terms, or [Language Selection](lang-selection.md) for how OVOS decides which language to use.

OpenVoiceOS's multilingual language-name parsing and pronouncing library. It converts spoken language names ("Spanish", "Espagnol") to BCP-47 codes (`"es"`) and vice versa, so skills and components can handle language-selection commands in natural speech.

**What you get in 30 seconds:**

```python
from ovos_lang_parser import extract_langcode, pronounce_lang

extract_langcode("switch to Spanish please", "en")   # ("es", 1.0)  -> (code, confidence)
extract_langcode("Brazilian Portuguese", "en")        # ("pt-br", 1.0)  regional codes preserved
pronounce_lang("fr", "en")                            # "French"
```

Because matching is fuzzy, apply a confidence threshold before acting on a result — the OVOS examples treat `conf >= 0.7` as a hit:

```python
code, conf = extract_langcode(utterance, ui_lang)
if conf >= 0.7:
    switch_language(code)
```

When a user says "switch to French", you need the BCP-47 code `"fr"`; when speaking a language back to the user you need its localized name. This library covers both directions.

The first argument that names a language is the *target* language being talked about; the `lang` argument is the *UI language the user is speaking in* (which decides the vocabulary of recognized names). 21 UI languages ship with name vocabularies: `an`, `ar`, `ast`, `bg`, `ca`, `da`, `de`, `en`, `es`, `eu`, `fr`, `fy`, `gl`, `hr`, `it`, `kab`, `nl`, `oc`, `pt`, `ro`, `sk` (the live list is always `ovos_lang_parser.LANGS`). A UI `lang` outside this set is matched to the closest one (and raises `ValueError` if nothing is close).

---

## Package layout

| File | Responsibility |
|------|---------------|
| `ovos_lang_parser/__init__.py` | Entire public API — 3 functions plus the `LANGS` constant |
| `ovos_lang_parser/res/<lang>/langs.json` | Per-UI-language JSON files mapping BCP-47 codes to their spoken name(s) in that UI language |

The public surface is these three functions plus the `LANGS` constant — the list of UI-language codes that ship a wordlist.

Dependencies: `ovos-spec-tools` (BCP-47 tag resolution: `standardize_lang`, `closest_lang`, `lang_distance` per OVOS-INTENT-2 §2.2), `langcodes` and `language_data` (CLDR display names / fuzzy name lookup), `ovos-utils` (fuzzy `match_one`). Alternative-name template expansion is handled internally by the module's own `_expand()` regex, not by `ovos-utils`.

---

## Architecture

The library is intentionally minimal. `__init__.py` contains three functions and a module-level resource directory scan:

```python
RES_DIR = f"{os.path.dirname(__file__)}/res"
LANGS = sorted(entry for entry in os.listdir(RES_DIR)
               if os.path.isfile(f"{RES_DIR}/{entry}/langs.json"))
```

### `get_lang_data(lang)`

1. Uses `ovos_spec_tools.language.closest_lang(lang, LANGS)` to tolerate BCP-47 variants (e.g. `"en-US"` matches `"en"`, `"pt-br"` matches `"pt"`). Raises `ValueError` when `closest_lang` returns `None` (nothing close enough).
2. Opens `res/<closest_lang>/langs.json`.
3. Expands any alternative-name templates (e.g. `"(Español|Castellano)"` → `["Español", "Castellano"]`) with the module's internal recursive `_expand()` regex.
4. Returns a flat `dict` of `spoken_name → bcp47_code` for all known languages in that UI language.

!!! note
    The template syntax is `(a|b)` for alternatives, not square brackets. Expansion is done by the library's own `_expand()` function — there is no dependency on any external template-expansion helper.

The `langs.json` format maps BCP-47 codes to one or more spoken names, either as a plain string, a JSON list, or a `(alt1|alt2)` template string. For example, `res/de/langs.json` (German UI names) lists Catalan as:

```json
{
  "ca": ["Katalanisch", "Valencianisch"]
}
```

---

## API reference

All three public functions are defined in `ovos_lang_parser/__init__.py`.

### `get_lang_data`

```python
def get_lang_data(lang: str) -> dict
```

Return the full spoken-name-to-code mapping for UI language `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lang` | `str` | BCP-47 code of the UI language (the language the user is speaking in) |

Returns `dict[spoken_name, bcp47_code]`. Multiple spoken names for the same language produce multiple keys mapping to the same code.

Raises `ValueError` if no resource file is close enough to `lang` (when `ovos_spec_tools.language.closest_lang` returns `None`).

---

### `extract_langcode`

```python
def extract_langcode(text: str, lang: str) -> Tuple[str, float]
```

Identify the language being referred to in `text`, where the user is speaking in `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Utterance containing a language name, e.g. `"set the language to French"` |
| `lang` | `str` | BCP-47 code of the UI language |

Returns `(bcp47_code, confidence_score)` — the best-matching language code and its match confidence (0.0–1.0). Matching proceeds in tiers:

1. **Exact whole-word span match** always wins: a wordlist name appearing verbatim as a run of whole words in the utterance returns confidence `1.0`; the most specific (longest) such span wins, so `"American English"` beats `"English"`.
2. **Fuzzy wordlist match** via `ovos_utils.parse.match_one` with `MatchStrategy.TOKEN_SET_RATIO`.
3. **Guarded CLDR fallback** (`langcodes.find`): consulted only when the fuzzy match is below the `0.9` name floor, covering languages no wordlist bundles. It is guarded so `langcodes.find` cannot greedily resolve ordinary words to obscure codes.

Non-string or blank `text` returns `("", 0.0)` rather than raising; a zero-confidence match also yields `("", 0.0)`.

Example:
```python
extract_langcode("switch to Spanish please", "en")
# ("es", 1.0)
```

---

### `pronounce_lang`

```python
def pronounce_lang(lang_code: str, lang: str) -> str
```

Return the spoken name of a language code in the UI language `lang`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lang_code` | `str` | BCP-47 code of the language to pronounce, e.g. `"fr"` |
| `lang` | `str` | BCP-47 code of the UI language |

Returns a single spoken name string. Resolution is most-specific-first: the full tag's curated name, then the **base-language** curated name (a regioned or private-use tag like `ar-EG` or `pt-BR-x-caipira` resolves to the name of `ar` / `pt`). If the wordlist has no curated name, it falls back to the CLDR display name via `langcodes` (`mwl` → `"Mirandese"`, `lij` → `"Ligurian"`), covering the long tail of ISO-639 codes no wordlist bundles. Only a truly unknown code is returned unchanged.

Example:
```python
pronounce_lang("fr", "en")   # "French"
pronounce_lang("es", "en")   # "Spanish"
pronounce_lang("en", "fr")   # "Anglais"
pronounce_lang("mwl", "en")  # "Mirandese"  (CLDR fallback, no wordlist entry)
```

---

## Dialects & regional subtags

A language code may carry a region (`ar-EG`, `pt-AO`) or a private-use dialect subtag (`an-x-ansotano`, `pt-BR-x-caipira`, `ar-IQ-x-qeltu`). The wordlists name languages and a handful of specific regional varieties — they do not name every dialect. The contract is explicit:

- Tag standardization (`ovos_spec_tools.language.standardize_lang`) **preserves** region and `-x-` private-use subtags; a tag is never silently collapsed to its base language, and a private-use tag never raises.
- `pronounce_lang` returns the most specific spoken name it has: the full tag's name when one exists, otherwise a documented, lossy-but-safe fall back to the **base-language** name (`ar-EG` → the name of `ar`). This is an acceptable answer, not a failure, when no dialect-specific name is bundled.

---

## Language resource files

Resources live in `ovos_lang_parser/res/<lang>/langs.json`. Each file is written in the UI language indicated by the directory name and lists language names as they would be spoken by a user of that UI language.

A code can list multiple valid spoken forms — as a JSON list, or as a `"(Name1|Name2)"` alternation string that gets expanded — allowing for synonyms (e.g. German lists both "Katalanisch" and "Valencianisch" for `"ca"`).

---

## Cross-references

| Package | Relationship |
|---------|-------------|
| `ovos-bus-client` | Uses `ovos-lang-parser` for language normalization in message contexts |
| `ovos-core` | Language selection commands handled via skills that call this library |
| `ovos-workshop` | Skill helpers for language-switching may use this library |
| `ovos-number-parser` | Peer library in the OVOS NLP stack; not a dependency |
| `ovos-date-parser` | Peer library in the OVOS NLP stack; not a dependency |
| `ovos-color-parser` | Peer library in the OVOS NLP stack; not a dependency |

See also:
- [Number Parser](number-parser.md)
- [Date Parser](date-parser.md)
- [Color Parser](color-parser.md)

---

*Source code: [OpenVoiceOS/ovos-lang-parser](https://github.com/OpenVoiceOS/ovos-lang-parser).*
