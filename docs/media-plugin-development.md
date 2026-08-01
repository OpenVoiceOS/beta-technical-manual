# Writing a Media Playback Backend Plugin

!!! abstract "In a nutshell"
    This page teaches you how to write an [`ovos-media`](ovos-media.md) playback backend:
    which base class to subclass, what each method contract expects, how to register the
    entry point, and how to test the result. It covers the `opm.media.*` family only. The
    old audio service (`mycroft.plugin.audioservice`) is a separate, deprecated interface.
    See [OCP Audio Plugin](ocp-audio-plugin.md) if you still need to target it. Looking for
    a plugin to use instead of writing one? Go to [Media Plugins](media-plugins.md).

A media backend plays **one track at a time**. OCP owns the playlist. Your plugin only
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
add no new methods. They only change load order.

## Abstract methods

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
alone. `load_track` only records the URI and metadata and emits `LOADED_MEDIA`. It does
**not** start playback. Playback itself is driven by `ocp_start()` / `ocp_pause()` /
`ocp_resume()` / `ocp_stop()`, which the base class also implements: each one emits the
matching `ovos.common_play.player.state` / `.media.state` / `.track.state` bus events and
then calls your `play()` / `pause()` / `resume()` / `stop()`. Implement the plain methods,
not the `ocp_*` wrappers.

Two constructor arguments matter: `config` (your plugin's settings dict) and `bus` (the
`MessageBusClient` OCP passes in). `bus` falls back to a `FakeBus()` when unset, which is
what makes the plugin importable and testable outside a running OVOS stack.

---

## Minimal complete example

**Project layout:**

```
ovos-media-plugin-noop/
├── pyproject.toml
└── ovos_media_plugin_noop/
    └── __init__.py
```

**`ovos_media_plugin_noop/__init__.py`**: an audio backend wrapping a hypothetical
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

---

## Unit-testing without OVOS

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
plain `play()`/`pause()`/`resume()`/`stop()` methods. OCP calls the `ocp_*` wrappers,
and that is also where you can assert on the bus events a `FakeBus` recorded.

## Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.ocp import find_ocp_audio_plugins
print(find_ocp_audio_plugins())
# {'ovos-media-plugin-noop': <class 'ovos_media_plugin_noop.NoopAudioService'>}
```

`find_ocp_video_plugins()` and `find_ocp_web_plugins()` are the matching lookups for the
other two groups (all three live in `ovos_plugin_manager.ocp`).

## Publish checklist

1. The class subclasses `AudioPlayerBackend`, `VideoPlayerBackend`, or
   `WebPlayerBackend` (or their `Remote*` variant) and implements all ten abstract
   methods with the documented signatures and return types: `supported_uris`, `play`,
   `stop`, `pause`, `resume`, `lower_volume`, `restore_volume`, `get_track_length`,
   `get_track_position`, `set_track_position`. `MediaBackend` uses `ABCMeta`, so leaving
   any one of them out is a `TypeError` the first time the plugin is instantiated, not a
   runtime surprise later.
2. The entry-point group in `pyproject.toml` matches that base class
   (`opm.media.audio` / `.video` / `.web`).
3. `__init__` accepts `config=None, bus=None` and works with an empty config and a
   `FakeBus()`.
4. `play()`/`pause()`/`resume()`/`stop()` operate on `self._now_playing`, set by the
   base class's `load_track()`. Do not require callers to pass the URI again.
5. Unit tests exercise the backend directly, with no OVOS services running.
6. `find_ocp_audio_plugins()` (or the `_video`/`_web` equivalent) discovers the
   installed plugin under the expected name.
7. If shipping a dual old-audio-service entry point too, keep the `opm.media.*` class
   and the `mycroft.plugin.audioservice` class separate. They are different contracts,
   not the same class registered twice.

---
**Read next:** [Media Plugins](media-plugins.md)
**Related:** [OCP Audio Plugin](ocp-audio-plugin.md) · [Media Service (ovos-media)](ovos-media.md) · [Plugin Manager](plugin-manager.md)
