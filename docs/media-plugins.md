# Media Plugins Reference

!!! abstract "In a nutshell"
    These plugins are the **playback backends** that actually push audio/video to your
    speakers or screen (VLC, MPV, Chromecast, Spotify…). OVOS is mid-migration between the
    legacy audio-service backend and the upcoming [`ovos-media`](ovos-media.md) daemon, and a
    single plugin **package is meant to ship a version for both**. See
    [Media playback: legacy vs. ovos-media](ovos-media.md).

Writing a plugin instead of choosing one? See [Writing a Media Playback Backend Plugin](media-plugin-development.md).

## Two interfaces, one package

A playback plugin can implement **two separate entry-point families**:

- **Old audio service**: `mycroft.plugin.audioservice` (used by the deprecated
  [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) / "old audio service", the shipped default).
- **[`ovos-media`](ovos-media.md)**: `opm.media.{audio,video,web}` (the upcoming daemon).

Media *classifiers* are a separate concern from playback backends: they recognize the
media intent and entities (artist, title, station, …) in an utterance before a stream is
resolved and played. See [ovos-media-classifier](#ovos-media-classifier) below.

These two families are **separate** (different entry-point groups and base classes), **but a
plugin package is meant to ship a version for *both***. This way a single `pip install` gives
you a backend that works whichever playback system you run. Packages are not required to ship
both families. See the table below for what each currently supports.

| Package | Player | Ships for | License | Maturity |
|---|---|---|---|---|
| [ovos-media-plugin-spotify](#ovos-media-plugin-spotify) | Spotify Connect | yes: both (old audio service + ovos-media) | Apache-2.0 | Stable |
| [ovos-media-plugin-chromecast](#ovos-media-plugin-chromecast) | Chromecast (audio + video) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-vlc](#ovos-media-plugin-vlc) | headless VLC (audio + video) | yes: both | Apache-2.0 | Beta |
| [ovos-media-plugin-mplayer](#ovos-media-plugin-mplayer) | MPlayer (audio + video) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-mpv](#ovos-media-plugin-mpv) | MPV (audio + video) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-ffplay](#ovos-media-plugin-ffplay) | ffplay (audio) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-cli](#ovos-media-plugin-cli) | generic CLI-command player (audio) | yes: both | Apache-2.0 | Alpha |
| [ovos-plugin-vlc](#ovos-plugin-vlc) | VLC | old audio service only (legacy). Use ovos-media-plugin-vlc for ovos-media | Apache-2.0 | Stable |
| ovos-media-plugin-mass | Music Assistant server (audio) | ovos-media only | — | Not yet published |
| ovos-media-plugin-mpris | external MPRIS player (audio + video) | ovos-media only | — | Not yet published |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).

!!! note "License and Maturity are independent axes"
    The **License** column reports what the repository itself declares, or doesn't. "No
    license file" just means no SPDX license was found, not that the code is unmature. The
    **Maturity** column reports repository health (age, activity, issues/PRs, docs). A plugin can
    be **Mature** and still ship no license file, or be **Stable** with a permissive license but
    thin docs. Don't read one column as implying the other.

The [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) below is not a playback backend. It is the
**old audio service itself** (deprecated, still the shipped default).


## ovos-media-plugin-spotify

- **GitHub**: [ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify)


- **Description**: Spotify Connect playback. Ships entry points for **both** the old audio service (`mycroft.plugin.audioservice`) and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`).

```bash
pip install ovos-media-plugin-spotify
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-vlc

- **GitHub**: [ovos-media-plugin-vlc](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc)


- **Description**: Headless VLC audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`,
  classes `VLCOCPAudioService` / `VLCOCPVideoService`) and the old audio service
  (`mycroft.plugin.audioservice`, type `ovos_vlc`). The older, old-audio-service-only
  [ovos-plugin-vlc](#ovos-plugin-vlc) still exists as a separate package.

```bash
pip install --pre ovos-media-plugin-vlc
```

!!! warning "Needs the native `libvlc` system library"
    `ovos-media-plugin-vlc` wraps `python-vlc`, which needs the native `libvlc` system library
    to actually load. `pip install` alone will not error if `libvlc` is missing — the plugin
    just silently fails to load, and no audio backend is available. Install the system package
    too, e.g. `apt install vlc` (Debian/Ubuntu) or `libvlc-dev`/`libvlc5` on distros that split
    the runtime from the dev headers. If you want a backend with no native binding to install,
    see [ovos-media-plugin-ffplay](#ovos-media-plugin-ffplay) below.

Then select it in your audio/media backend config, using the **entry-point name**
(`ovos-media-audio-plugin-vlc` for audio, `ovos-media-video-plugin-vlc` for video) as the
`module` value — this differs from the pip package name (`ovos-media-plugin-vlc`). See [Media
playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-chromecast

- **GitHub**: [ovos-media-plugin-chromecast](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast)


- **Description**: Cast audio/video to a Chromecast. Ships entry points for **both** the old audio service and [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`).

```bash
pip install ovos-media-plugin-chromecast
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-ocp-audio-plugin

- **GitHub**: [ovos-ocp-audio-plugin](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin)


- **Description**: The legacy **"old audio service"** OCP backend. It combines OCP search orchestration, the player state machine, MPRIS and the GUI into a single `ovos-audio` `AudioBackend`. Warning: deprecated but still shipped and enabled by default (`enable_old_audioservice: true`). The standalone [ovos-media](ovos-media.md) daemon supersedes it. See the dedicated **[OCP Audio Plugin](ocp-audio-plugin.md)** page for the full background, configuration, and migration path.

---

## ovos-plugin-vlc

- **PyPI**: [ovos-plugin-vlc](https://pypi.org/project/ovos-plugin-vlc) (legacy package, no separate source repository, superseded by [ovos-media-plugin-vlc](#ovos-media-plugin-vlc))


- **Description**: VLC `AudioBackend` for the **old audio service** (`mycroft.plugin.audioservice`). For the [ovos-media](ovos-media.md) backend use [ovos-media-plugin-vlc](#ovos-media-plugin-vlc).

```bash
pip install ovos-plugin-vlc
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-mplayer

- **GitHub**: [ovos-media-plugin-mplayer](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer)


- **Description**: MPlayer audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`)
  and the old audio service (`mycroft.plugin.audioservice`, type `ovos_mplayer`).

```bash
pip install --pre ovos-media-plugin-mplayer
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-mpv

- **GitHub**: [ovos-media-plugin-mpv](https://github.com/OpenVoiceOS/ovos-media-plugin-mpv)
  (PyPI publishes under the same name; the pre-rename `ovos-audio-plugin-mpv` package still
  exists but stopped at 0.2.1 and lacks the dual-target backend).


- **Description**: MPV audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`)
  and the old audio service (`mycroft.plugin.audioservice`, type `ovos_mpv`).

```bash
pip install --pre ovos-media-plugin-mpv
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-ffplay

- **GitHub**: [ovos-media-plugin-ffplay](https://github.com/OpenVoiceOS/ovos-media-plugin-ffplay)


- **Description**: ffplay-based audio playback backend. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio`, class
  `FFPlayOCPAudioService`) and the old audio service (`mycroft.plugin.audioservice`, type
  `ovos_ffplay`). Direct programmatic access is available via `FFPlayAudioPlayer`.

```bash
pip install --pre ovos-media-plugin-ffplay
```

A good default for a headless box: it only needs `ffmpeg`/`ffplay` on the `PATH`, which most
systems already have or can install with a single package (`apt install ffmpeg`), with no
separate native binding to install (unlike [ovos-media-plugin-vlc](#ovos-media-plugin-vlc)
above).

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-cli

- **GitHub**: [ovos-media-plugin-cli](https://github.com/OpenVoiceOS/ovos-media-plugin-cli)


- **Description**: Generic command-line playback backend. Shells out to any CLI media
  player. With an explicit `command` set (e.g. `"mpv --no-terminal"`, `"ffplay -nodisp
  -autoexit"`), it appends the track URI as the final argument. With no `command` set it
  auto-detects the best available player for the platform (`sox`/`play` preferred, then
  `mpg123`/`paplay`/`aplay` on Linux, `afplay` on macOS). Pause/resume use process signals
  (`SIGSTOP`/`SIGCONT`). Ships entry points for both ovos-media (`opm.media.audio`, class
  `CLIAudioService`) and the old audio service (`mycroft.plugin.audioservice`, type
  `ovos_cli`).

```bash
pip install --pre ovos-media-plugin-cli
```

Only alpha releases exist on PyPI so far, matching its Alpha rating above — hence the
`--pre` flag.

Then select it in your audio/media backend config, optionally setting the `command` to
a specific CLI player. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-mass

- **Status**: not yet published — no public repository or PyPI package exists, so it cannot be
  installed today.
- **Description**: Hands playback off to a [Music Assistant](https://music-assistant.io/) server
  instead of playing the stream directly. `opm.media.audio` only, `ovos-media` only — there is
  no old-audio-service equivalent. Does not implement `next()`/`previous()` through the legacy
  `AudioBackend` interface; skipping/previous only work through the Music Assistant queue API.

Then select it in your `media.audio_players` config. See [Media playback: legacy vs.
ovos-media](ovos-media.md).

---

## ovos-media-plugin-mpris

- **Status**: not yet published — no public repository or PyPI package exists, so it cannot be
  installed today.
- **Description**: Drives an already-running external MPRIS player (e.g. a desktop media app)
  rather than playing the stream itself. `opm.media.audio` and `opm.media.video`, `ovos-media`
  only. Complements (but is separate from) `ovos-media`'s own MPRIS exporter/reflector — see
  [MPRIS Integration](ovos-media-mpris.md).

Then select it in your `media.audio_players` / `media.video_players` config. See
[Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-classifier

- **GitHub**: [ovos-media-classifier](https://github.com/OpenVoiceOS/ovos-media-classifier)


- **Description**: Classifies an utterance's media intent and extracts entities (artist,
  title, station, …) ahead of stream resolution. Several backends are available depending on
  installed extras. `KeywordMediaClassifier` (bundled locale keyword lists) is the always-available
  default, with `EmbeddingMediaClassifier`, `HybridMediaClassifier`, `OnnxMediaClassifier`, an
  Aho-Corasick exact-entity-list matcher (`AhocorasickMediaClassifier`, `[ner]` extra), and a
  `metadatarr`-backed classifier (`MetadatarrMediaClassifier`) as optional upgrades. Every backend
  is importable from the top-level package. The optional ones resolve lazily so their extras are
  only touched when actually used.

```bash
pip install --pre ovos-media-classifier          # keyword backend only
pip install --pre ovos-media-classifier[ner]     # adds the Aho-Corasick NER backend
```

```python
from ovos_media_classifier import KeywordMediaClassifier, load_media_classifier
```

The `[ner]` extra adds `AhocorasickMediaClassifier` (in `ovos_media_classifier.ahocorasick`), a gazetteer/entity-list backend built on Aho-Corasick matching.

!!! note
    The `[ner]` extra's "NER" is exact entity-list matching, not statistical named-entity
    recognition: `AhocorasickMediaClassifier` compiles the configured entity lists (your actual
    library: artists, titles, stations) into an Aho-Corasick automaton and matches verbatim. No
    model guesses spans.

The package *defines* the `opm.media.classifier` entry-point group as the contract for
**third-party** classifiers — its own keyword backend is loaded by direct import inside the
package, not through that group, so writing an external classifier means registering your
package under the group per the docstring in `ovos_media_classifier/plugins.py`.

---
**Read next:** [GUI Protocol](gui-protocol.md)
**Related:** [OCP Extractors](ocp-plugins.md) · [Media Service (ovos-media)](ovos-media.md) · [Choosing Plugins](choosing-plugins.md)
