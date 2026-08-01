# Media Plugins Reference

!!! abstract "In a nutshell"
    These plugins are the **playback backends** that actually push audio/video to your
    speakers or screen (VLC, MPV, Chromecast, Spotify…). OVOS is mid-migration between the
    legacy audio-service backend and the upcoming [`ovos-media`](ovos-media.md) daemon, and a
    single plugin **package is meant to ship a version for both**. See
    [Media playback: legacy vs. ovos-media](ovos-media.md).

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
| [ovos-audio-plugin-mpv](#ovos-audio-plugin-mpv) | MPV (audio + video) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-ffplay](#ovos-media-plugin-ffplay) | ffplay (audio) | yes: both | Apache-2.0 | Stable |
| [ovos-media-plugin-cli](#ovos-media-plugin-cli) | generic CLI-command player (audio) | yes: both | Apache-2.0 | Alpha |
| [ovos-plugin-vlc](#ovos-plugin-vlc) | VLC | old audio service only (legacy). Use ovos-media-plugin-vlc for ovos-media | Apache-2.0 | Stable |
| ovos-media-plugin-mass | Music Assistant server (audio) | ovos-media only | — | — |
| ovos-media-plugin-mpris | external MPRIS player (audio + video) | ovos-media only | — | — |

Maturity reflects repository health (age, activity, open issues/PRs, in-repo docs), not version. See the [Maturity Scale](maturity.md).

!!! note "License and Maturity are independent axes"
    The **License** column reports what the repository itself declares, or doesn't. "No
    license file" just means no SPDX license was found, not that the code is unmature. The
    **Maturity** column reports repository health (age, activity, issues/PRs, docs). A plugin can
    be **Mature** and still ship no license file, or be **Stable** with a permissive license but
    thin docs. Don't read one column as implying the other.

The [`ovos-ocp-audio-plugin`](#ovos-ocp-audio-plugin) below is not a playback backend. It is the
**old audio service itself** (deprecated, still the shipped default).

---

## Writing a Media Playback Backend Plugin

!!! abstract "In a nutshell"
    This section teaches you how to write an [`ovos-media`](ovos-media.md) playback backend:
    which base class to subclass, what each method contract expects, how to register the
    entry point, and how to test the result. It covers the `opm.media.*` family only. The
    old audio service (`mycroft.plugin.audioservice`) is a separate, deprecated interface;
    see [OCP Audio Plugin](ocp-audio-plugin.md) if you still need to target it.

A media backend plays **one track at a time**. OCP owns the playlist; your plugin only
starts, stops, pauses, resumes, and reports position/length for whatever URI it was just
handed. All three families subclass `ovos_plugin_manager.templates.media.MediaBackend`
through a media-type-specific parent that only differs in which `TrackState` it emits on
`load_track`/`ocp_start`:

| Your plugin plays... | Base class | Group | `.config` group |
|---|---|---|---|
| audio only | `AudioPlayerBackend` | `opm.media.audio` | `opm.media.audio.config` |
| video | `VideoPlayerBackend` | `opm.media.video` | `opm.media.video.config` |
| a webview/webpage | `WebPlayerBackend` | `opm.media.web` | `opm.media.web.config` |

If your backend is a remote service that should only be tried after local backends fail
(a Chromecast, a Mopidy server), subclass the matching `Remote*PlayerBackend` instead
(`RemoteAudioPlayerBackend`, `RemoteVideoPlayerBackend`, `RemoteWebPlayerBackend`). They
add no new methods; they only change load order.

### Abstract methods

```python
from ovos_plugin_manager.templates.media import AudioPlayerBackend

class MyPlayer(AudioPlayerBackend):

    def __init__(self, config=None, bus=None):
        super().__init__(config, bus)
        self.supports_mime_hints = False  # set True if play() can use a mime type hint

    def supported_uris(self) -> list:
        """List of supported uri schemes, e.g. ['file', 'http', 'https']."""

    def play(self):
        """Start playback of the uri passed to load_track()."""

    def stop(self) -> bool:
        """Stop playback. Return True if playback was stopped, else False."""

    def pause(self):
        """Pause playback; resume() must continue from this exact position."""

    def resume(self):
        """Resume playback after pause()."""

    def lower_volume(self):
        """Duck the volume while OVOS is listening or speaking."""

    def restore_volume(self):
        """Restore the volume lower_volume() ducked."""

    def get_track_length(self) -> int:
        """Duration of the current track, in milliseconds."""

    def get_track_position(self) -> int:
        """Current playback position, in milliseconds."""

    def set_track_position(self, milliseconds):
        """Seek to an absolute position, in milliseconds."""
```

`load_track(uri, metadata=None)`, `seek_forward(seconds)`, `seek_backward(seconds)`,
`track_info()`, and `shutdown()` are implemented by the base class and normally left
alone. `load_track` only records the URI and metadata and emits `LOADED_MEDIA`; it does
**not** start playback. Playback itself is driven by `ocp_start()` / `ocp_pause()` /
`ocp_resume()` / `ocp_stop()`, which the base class also implements: each one emits the
matching `ovos.common_play.player.state` / `.media.state` / `.track.state` bus events and
then calls your `play()` / `pause()` / `resume()` / `stop()`. Implement the plain methods,
not the `ocp_*` wrappers.

Two constructor arguments matter: `config` (your plugin's settings dict) and `bus` (the
`MessageBusClient` OCP passes in; falls back to a `FakeBus()` when unset, which is what
makes the plugin importable and testable outside a running OVOS stack).

### Minimal complete example

**Project layout:**

```
ovos-media-plugin-noop/
├── pyproject.toml
└── ovos_media_plugin_noop/
    └── __init__.py
```

**`ovos_media_plugin_noop/__init__.py`** — an audio backend wrapping a hypothetical
`myplayer` library with `play(uri)`, `stop()`, `pause()`, `resume()`, `position_ms()`,
`seek(ms)`, `duration_ms()`, and `set_volume(percent)`:

```python
from ovos_plugin_manager.templates.media import AudioPlayerBackend


class NoopAudioService(AudioPlayerBackend):

    def __init__(self, config=None, bus=None):
        super().__init__(config, bus)
        self._volume = 100
        self._player = None  # lazily created in play()

    def supported_uris(self) -> list:
        return ["file", "http", "https"]

    def play(self):
        import myplayer
        self._player = myplayer.Player()
        self._player.play(self._now_playing)

    def stop(self) -> bool:
        if self._player:
            self._player.stop()
            self._player = None
            return True
        return False

    def pause(self):
        if self._player:
            self._player.pause()

    def resume(self):
        if self._player:
            self._player.resume()

    def lower_volume(self):
        if self._player:
            self._player.set_volume(int(self._volume * 0.3))

    def restore_volume(self):
        if self._player:
            self._player.set_volume(self._volume)

    def get_track_length(self) -> int:
        return self._player.duration_ms() if self._player else 0

    def get_track_position(self) -> int:
        return self._player.position_ms() if self._player else 0

    def set_track_position(self, milliseconds):
        if self._player:
            self._player.seek(milliseconds)
```

**`pyproject.toml`**. The entry-point group must match the base class:

```toml
[project]
name = "ovos-media-plugin-noop"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.media.audio"]
ovos-media-plugin-noop = "ovos_media_plugin_noop:NoopAudioService"
```

`opm.media.audio.config` (or `.video`/`.web`) is the parallel, optional group where a
plugin registers a dict of config metadata for installers and GUIs. Add it once the
plugin has settings worth advertising.

### Unit-testing without OVOS

The base class defaults `bus` to a `FakeBus()`, so a backend is testable with no
messagebus and no running OVOS stack:

```python
from ovos_media_plugin_noop import NoopAudioService

backend = NoopAudioService()
assert "https" in backend.supported_uris()
backend.load_track("https://example.com/track.mp3")
assert backend._now_playing == "https://example.com/track.mp3"
```

Exercise `ocp_start()` / `ocp_pause()` / `ocp_resume()` / `ocp_stop()` too, not just the
plain `play()`/`pause()`/`resume()`/`stop()` methods — OCP calls the `ocp_*` wrappers,
and that is also where you can assert on the bus events a `FakeBus` recorded.

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.ocp import find_ocp_audio_plugins
print(find_ocp_audio_plugins())
# {'ovos-media-plugin-noop': <class 'ovos_media_plugin_noop.NoopAudioService'>}
```

`find_ocp_video_plugins()` and `find_ocp_web_plugins()` are the matching lookups for the
other two groups (all three live in `ovos_plugin_manager.ocp`).

### Publish checklist

1. The class subclasses `AudioPlayerBackend`, `VideoPlayerBackend`, or
   `WebPlayerBackend` (or their `Remote*` variant) and implements all nine abstract
   methods with the documented signatures and return types.
2. The entry-point group in `pyproject.toml` matches that base class
   (`opm.media.audio` / `.video` / `.web`).
3. `__init__` accepts `config=None, bus=None` and works with an empty config and a
   `FakeBus()`.
4. `play()`/`pause()`/`resume()`/`stop()` operate on `self._now_playing`, set by the
   base class's `load_track()` — do not require callers to pass the URI again.
5. Unit tests exercise the backend directly, with no OVOS services running.
6. `find_ocp_audio_plugins()` (or the `_video`/`_web` equivalent) discovers the
   installed plugin under the expected name.
7. If shipping a dual old-audio-service entry point too, keep the `opm.media.*` class
   and the `mycroft.plugin.audioservice` class separate — they are different contracts,
   not the same class registered twice.

---

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
pip install ovos-media-plugin-vlc
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

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
pip install ovos-media-plugin-mplayer
```

Then select it in your audio/media backend config. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-audio-plugin-mpv

- **GitHub**: [ovos-media-plugin-mpv](https://github.com/OpenVoiceOS/ovos-media-plugin-mpv)
  (the repo lives under this name. The PyPI package is still published as `ovos-audio-plugin-mpv`).


- **Description**: MPV audio/video playback. Ships entry points for both
  [ovos-media](https://github.com/OpenVoiceOS/ovos-media) (`opm.media.audio` / `opm.media.video`)
  and the old audio service (`mycroft.plugin.audioservice`, type `ovos_mpv`).

```bash
pip install ovos-audio-plugin-mpv
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
pip install ovos-media-plugin-ffplay
```

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
pip install ovos-media-plugin-cli
```

Then select it in your audio/media backend config, optionally setting the `command` to
a specific CLI player. See [Media playback: legacy vs. ovos-media](ovos-media.md).

---

## ovos-media-plugin-mass

- **Description**: Hands playback off to a [Music Assistant](https://music-assistant.io/) server
  instead of playing the stream directly. `opm.media.audio` only, `ovos-media` only — there is
  no old-audio-service equivalent. Does not implement `next()`/`previous()` through the legacy
  `AudioBackend` interface; skipping/previous only work through the Music Assistant queue API.

Then select it in your `media.audio_players` config. See [Media playback: legacy vs.
ovos-media](ovos-media.md).

---

## ovos-media-plugin-mpris

- **Description**: Drives an already-running external MPRIS player (e.g. a desktop media app)
  rather than playing the stream itself. `opm.media.audio` and `opm.media.video`, `ovos-media`
  only. Complements (but is separate from) `ovos-media`'s own MPRIS exporter/reflector — see
  [MPRIS Integration](ovos-media.md#mpris-integration).

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
pip install ovos-media-classifier          # keyword backend only
pip install ovos-media-classifier[ner]     # adds the Aho-Corasick NER backend
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

The keyword backend self-registers under the `opm.media.classifier` entry-point group this
package defines, so it doubles as the reference plugin exercising both OPM discovery and the
external-plugin path.

---
**Read next:** [GUI Protocol](gui-protocol.md)
**Related:** [OCP Extractors](ocp-plugins.md) · [Media Service (ovos-media)](ovos-media.md) · [Choosing Plugins](choosing-plugins.md)
