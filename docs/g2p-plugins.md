# Grapheme-to-Phoneme (G2P) Plugins

!!! abstract "In a nutshell"
    These plugins work out *how a written word should sound*. A "grapheme" is a letter you see on the page. A "phoneme" is a unit of sound you hear when it's spoken. This is the part that figures out, for example, that "knight" sounds like "nite". The voice that reads text aloud uses this to pronounce words more correctly. On-screen avatars use it to move their lips in time with the speech. For unfamiliar terms, see the [Glossary](glossary.md); to learn about the voices that speak, see [TTS Plugins](tts-plugins.md).

Grapheme-to-Phoneme (G2P) plugins convert written text (graphemes) into phonemes. In practice
this is an **alpha-quality, Mark 1-era capability used for mouth-movement / viseme animation**:
the original consumer was the Mark 1 faceplate, and the [enclosure API](phal-authoring.md) that
carries the mouth frames still exists. Most [TTS](tts-plugins.md) voices don't emit phoneme
timing, so a G2P plugin *estimates* it from the text to drive lip-sync. Only **Mimic 1**
provides phoneme timing natively. For any other voice the G2P plugin simulates the timing with
placeholder durations. **If you don't drive an on-screen mouth or face, you don't need a G2P
plugin.**

## How it works

A G2P plugin takes a word or an utterance and returns a list of phonemes in a specific alphabet, such as **Arpabet** or **IPA**.

At runtime the viseme path lives in `ovos-audio`'s playback thread and has two legs:

1. **TTS-provided timing.** A TTS plugin may return phoneme data alongside the audio. Mimic 1
   returns real `phoneme:duration` pairs, and the TTS base class maps them to viseme codes
   (a phoneme without a duration gets a `0.2`s placeholder). No shipped neural voice returns
   phoneme timing.
2. **G2P fallback.** When the synthesized audio arrives with **no** phoneme timing and a G2P
   plugin is configured, playback calls the plugin's `utterance2visemes(utterance, lang)`
   instead. The base implementation phonemizes word-by-word and assigns every phoneme a flat
   `0.4`s placeholder duration (real per-phoneme duration prediction is unimplemented). A word
   the plugin returns no phonemes for falls back to the phoneme sequence for *"blah blah"*;
   a plugin that raises `OutOfVocabulary` instead aborts viseme generation for that utterance,
   and playback shows no mouth movement. The result is timing that roughly tracks speech, not
   lip-sync you could read.

Either way the `(viseme, duration)` pairs go out through the enclosure API as an
`enclosure.mouth.viseme_list` bus message (`{"start": <timestamp>, "visemes": [...]}`), which a
faceplate driver or avatar renders. The viseme codes are the Mark 1 mouth shapes: `0` (*y*/*aa*),
`1` (*aw*), `2` (*uh*/*r*), `3` (*th*/*sh*), `4` (neutral / no sound), `5` (*f*/*v*),
`6` (*oy*/*ao*).

## Configuration

G2P is **off by default**: the shipped `mycroft.conf` has `"g2p": {"module": ""}`, and
`ovos-audio` only loads a plugin when a module is set. The reserved module name `dummy` loads
the bare base class (useful only for testing), and an optional `fallback_module` names a second
plugin to try when the first fails to load:

```json
{
  "g2p": {
    "module": "ovos-g2p-plugin-mimic",
    "fallback_module": ""
  }
}
```

**Recommended module: `ovos-g2p-plugin-mimic`** (English only). It is the one plugin that
escapes the placeholder-duration problem: it overrides `utterance2visemes` to run the text
through the Mimic 1 binary and returns Mimic's own per-phoneme durations, so the mouth
tracks real speech timing even when the *voice* you hear is a different TTS engine. Every
other plugin inherits the flat `0.4`s placeholders.

## Available G2P Plugins

| Plugin | Alphabet | Description | Maturity |
|--------|----------|-------------|----------|
| `ovos-g2p-plugin-mimic` | ARPA | Uses the Mimic 1 engine for G2P conversion. Shipped by [ovos-tts-plugin-mimic](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic) (the TTS plugin also registers an `opm.g2p` entry point). | Beta |
| `ovos-scriptconv-g2p-plugin` | IPA | [45 phonemizer backends behind one config switch](https://github.com/TigreGotico/ovos-scriptconv-g2p-plugin), built on [`scriptconv`](https://github.com/TigreGotico/scriptconv). | Alpha |

--8<-- "snippets/maturity-disclaimer.md"

!!! note "Roster completeness"
    This table lists the G2P plugins known to register an `opm.g2p` entry point. It is
    not guaranteed to be exhaustive. If you know of another OVOS-compatible G2P
    plugin missing here, check its `pyproject.toml`/`setup.py` for an `opm.g2p` entry point before
    you assume it belongs on this list.

!!! note "Some TTS engines phonemize internally, without an `opm.g2p` plugin"
    [`ovos-tts-plugin-espeakNG`](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG) embeds
    espeak-ng's own grapheme-to-phoneme conversion. The `phoonnx` TTS backends delegate
    phonemization to [`scriptconv`](https://github.com/TigreGotico/scriptconv), instead of a
    separate `opm.g2p` plugin. Neither is on the table above, because neither is discoverable
    as a standalone G2P plugin. The phonemization happens as an implementation detail of the TTS
    engine itself.

---

## Technical Explanation

All G2P plugins inherit from the `Grapheme2PhonemePlugin` base class in
`ovos_plugin_manager.templates.g2p`.

### The G2P Interface

```python
class Grapheme2PhonemePlugin:
    def __init__(self, config: dict = None):
        self.config = config or {}

    def get_arpa(self, word: str, lang: str, ignore_oov: bool = False):
        """Return phonemes in Arpabet format."""
        # default implementation: converts get_ipa() output via ipa2arpabet,
        # if get_ipa() is implemented. Raises OutOfVocabulary otherwise
        # (or returns None when ignore_oov=True).
        ...

    def get_ipa(self, word: str, lang: str, ignore_oov: bool = False):
        """Return phonemes in IPA format."""
        # default implementation: converts get_arpa() output via arpabet2ipa,
        # if get_arpa() is implemented. Raises OutOfVocabulary otherwise
        # (or returns None when ignore_oov=True).
        ...

    @classproperty
    def available_languages(cls):
        """Return languages supported by this G2P implementation in this state."""
        raise NotImplementedError

```

Neither `get_arpa` nor `get_ipa` is a plain abstract method: each has a default body that
converts the *other* one's output (Arpabet ↔ IPA, via `ovos_utils.lang.phonemes`). A plugin
implements whichever of the two its engine produces natively, and gets the other one for free
through that conversion. Implement neither and both raise `OutOfVocabulary` for every word. The
only member the base class marks with `@abc.abstractmethod` is `available_languages`, a
`classproperty` (from `ovos_utils`) — every plugin must override it.

`OutOfVocabulary` (a `ValueError` subclass, also in `ovos_plugin_manager.templates.g2p`) is the
exception both methods raise for a word the engine cannot phonemize, unless the caller passes
`ignore_oov=True`, in which case they return `None` instead. The `utterance2arpa`,
`utterance2ipa`, and `utterance2visemes` helpers split an utterance on whitespace, call
`get_arpa`/`get_ipa` per word, and join the results with a `"."` separator between words.
`utterance2arpa` and `utterance2ipa` propagate `OutOfVocabulary` the same way, unless
`ignore_oov=True`; `utterance2visemes` has no `ignore_oov` parameter and always propagates.

`PhonemeAlphabet` (a `str` enum with members `ARPA` and `IPA`, same module) is a small
convenience type some plugins use to declare which alphabet they emit — it is not required by
the base class, which never inspects it.

Like every OVOS plugin base class, `Grapheme2PhonemePlugin` also exposes `runtime_requirements`,
a `classproperty` returning a `RuntimeRequirements` instance (from `ovos_utils.process_utils`).
The default declares no network or internet dependency at all. Override it if the plugin needs a
model download or a remote call — see the docstring in the source for the three worked examples
(fully offline, online-with-cache, always-online).

## Creating Your Own Plugin

### Abstract methods

| Method | Signature | Required? |
|---|---|---|
| `available_languages` | `classproperty` → `Set[str]` | Yes, the only true abstract method |
| `get_arpa` | `(self, word: str, lang: str, ignore_oov: bool = False)` | One of `get_arpa`/`get_ipa`, or neither works |
| `get_ipa` | `(self, word: str, lang: str, ignore_oov: bool = False)` | One of `get_arpa`/`get_ipa`, or neither works |

### 1. Minimal complete example

**Project layout:**

```
ovos-g2p-plugin-example/
├── pyproject.toml
└── ovos_g2p_plugin_example/
    └── __init__.py
```

**`ovos_g2p_plugin_example/__init__.py`:**

```python
from typing import Set
from ovos_utils import classproperty
from ovos_plugin_manager.templates.g2p import Grapheme2PhonemePlugin, OutOfVocabulary

# a toy lexicon, replace with a real G2P model or rule set
_LEXICON = {"hello": ["HH", "EH", "L", "OW"]}


class MyG2P(Grapheme2PhonemePlugin):
    def get_arpa(self, word: str, lang: str, ignore_oov: bool = False):
        phones = _LEXICON.get(word.lower())
        if phones is None:
            if ignore_oov:
                return None
            raise OutOfVocabulary(f"unknown word: {word}")
        return phones

    @classproperty
    def available_languages(cls) -> Set[str]:
        return {"en-us"}
```

**`pyproject.toml`**. The entry-point group is `opm.g2p`; the entry-point name (left of `=`) is
the string users put in their config:

```toml
[project]
name = "ovos-g2p-plugin-example"
version = "0.1.0"
dependencies = ["ovos-plugin-manager>=0.5.0,<1.0.0"]

[project.entry-points."opm.g2p"]
ovos-g2p-plugin-example = "ovos_g2p_plugin_example:MyG2P"

[project.entry-points."opm.g2p.config"]
ovos-g2p-plugin-example.config = "ovos_g2p_plugin_example:MY_G2P_CONFIGS"
```

`opm.g2p.config` is the parallel config-metadata group, same convention as every other OPM
plugin family: optional, and only worth adding once the plugin has settings worth advertising to
installers and GUIs.

> **Backward compatibility**: `ovos-plugin-manager` still loads legacy `ovos.plugin.g2p` entry
> points, but new plugins should register under `opm.g2p`.

### 2. Test it without OVOS

`Grapheme2PhonemePlugin` is a plain class with no messagebus connection, so a unit test needs
nothing but the package itself:

```python
from ovos_g2p_plugin_example import MyG2P

def test_get_arpa_known_word():
    g2p = MyG2P()
    assert g2p.get_arpa("hello", lang="en-us") == ["HH", "EH", "L", "OW"]

def test_get_arpa_oov_raises():
    from ovos_plugin_manager.templates.g2p import OutOfVocabulary
    g2p = MyG2P()
    import pytest
    with pytest.raises(OutOfVocabulary):
        g2p.get_arpa("zzznotaword", lang="en-us")
```

### 3. Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.g2p import find_g2p_plugins

plugins = find_g2p_plugins()
print(plugins)
# {'ovos-g2p-plugin-example': <class 'ovos_g2p_plugin_example.MyG2P'>}

g2p_class = plugins["ovos-g2p-plugin-example"]
g2p = g2p_class()
phonemes = g2p.get_arpa("hello", lang="en-us")
print(f"Phonemes: {phonemes}")
```

`ovos_plugin_manager.g2p` also has `load_g2p_plugin(name)` (returns the uninstantiated class)
and config-inspection helpers (`get_g2p_configs`, `get_g2p_lang_configs`,
`get_g2p_supported_langs`) that read whatever a plugin registered under `opm.g2p.config`.

There is no `G2PValidator` in the template, unlike TTS: `OVOSG2PFactory` instantiates the class
directly with no separate validation pass, so a plugin that needs a startup check (a missing
model file, an unreachable service) should raise from `__init__` or fail loudly the first time
`get_arpa`/`get_ipa` is called.

### Streaming

The G2P template has no streaming variant. `get_arpa`/`get_ipa` are synchronous, word-at-a-time
calls; there is nothing analogous to `StreamingTTS`. Do not add one.

### Package and publish

1. **Pin the dependency version.** Put a floor and a ceiling on `ovos-plugin-manager` in
   `pyproject.toml`, for example `ovos-plugin-manager>=0.5.0,<1.0.0`.
2. **Install for local development.** Run `pip install -e .` from the plugin's own repository, then
   confirm `find_g2p_plugins()` sees it, as in [Verify discovery](#3-verify-discovery) above.
3. **Publish to PyPI.** OVOS deployments install plugins from PyPI, not from a git checkout, so a
   plugin needs a PyPI release before it can be installed by `pip install <plugin-name>` on a
   real deployment.
4. **Remember this is alpha, Mark 1-era territory.** As the top of this page explains, G2P only
   matters if something consumes its viseme output for lip-sync. Confirm that use case exists
   before investing in a new plugin; most new TTS voices need no G2P plugin at all.

---
**Read next:** [OCP Audio Plugin](ocp-audio-plugin.md)
**Related:** [TTS Plugins](tts-plugins.md) · [Choosing Plugins](choosing-plugins.md) · [Maturity Scale](maturity.md) · [The First Phonemizer for Barranquenho](https://blog.openvoiceos.org/posts/2025-12-14-barranquenho)
