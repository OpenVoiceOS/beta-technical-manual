# ovos-media

!!! warning "Maturity — Proof-of-concept ⬤◯◯◯◯"
    The `ovos-media` daemon is **unfinished**. It is the **upcoming** media-playback service for OVOS, still being refactored, and **not enabled by default**. Today, stock installs play media through the **legacy audio backend**, the [`ovos-ocp-audio-plugin`](media-plugins.md#ovos-ocp-audio-plugin) ("old audio service") inside [`ovos-audio`](audio-service.md), which is **deprecated but still shipped**. Switching to `ovos-media` is opt-in and the player-as-skill coupling remains (the in-process GUI surface was dropped in 2.0.0a1; any GUI is an external bus client). Treat this page as the *target architecture*, for exploration only. Rated by [repository health](maturity.md), not version.

    OVOS has **two media-playback backends** sharing the same [OCP](ocp-pipeline.md) search framework (pipeline + skills + extractors):

    | | Legacy (current default) | ovos-media (upcoming) |
    |---|---|---|
    | **Package** | `ovos-ocp-audio-plugin` in [`ovos-audio`](audio-service.md) | `ovos-media` (standalone daemon) |
    | **Status** | deprecated, still shipped & on by default | opt-in refactor, not default |
    | **Playback** | one bundled audio backend | per-request audio/video/web [media plugins](media-plugins.md) (`opm.media.*`) |
    | **Extras** | none | MPRIS, per-session state, multiple players |
    | **Config** | `enable_old_audioservice: true` (default) | `enable_old_audioservice: false` + run `ovos-media` |

    The OCP **pipeline** and **stream extractors** are unaffected by which backend you use. Only the *playback* layer differs. (OCP **skills** are a separate, longer-term change.)

!!! abstract "In a nutshell"
    `ovos-media` is the planned future replacement for how OVOS plays music, podcasts and videos. Today, stock installs still use the older audio backend. `ovos-media` is an opt-in, work-in-progress rewrite meant to handle audio, video and web playback more cleanly and to support several players at once. If you are not deliberately trying it out, you are not using it yet. This page describes where things are heading. See the [OCP Pipeline](ocp-pipeline.md) for how playback requests are recognized, or the [Glossary](glossary.md) for terms.

`ovos-media` is the standalone audio/video daemon for OpenVoiceOS. It is the **upcoming
replacement** for the legacy audio service, and it provides a more capable and modular media player
built on the OpenVoiceOS [Common Play](ocp-pipeline.md) ([OCP](ocp-pipeline.md)) framework.

**In plain terms:** the old audio service could only play one kind of stream through a thin wrapper. `ovos-media` is a proper media daemon. It has separate audio/video/web players you pick per request. It supports MPRIS, so your phone's media controls work, and it keeps per-session state so multiple devices can each play their own thing.

??? info "📐 Formal specification"
    Media playback is specified by two architecture documents:
    **[OVOS-OCP-1 — OVOS Common Playback](https://github.com/OpenVoiceOS/architecture/blob/dev/ocp-1.md)**
    defines the per-session **virtual media player**, the single logical
    player every "play / pause / next / louder / stop" command targets, plus
    the MPRIS bridge to and from the host OS. Meanwhile,
    **[OVOS-AUDIO-1 — Audio Output Service](https://github.com/OpenVoiceOS/architecture/blob/dev/audio-out.md)**
    defines the **output service** that actually renders queued audio. OCP-1
    fixes the *observable control surface*. How a URI becomes bytes on a
    speaker is a backend concern. `ovos-media` is the implementation moving
    toward that contract. For the full set see the
    **[spec index](architecture-specs.md)**.

To use `ovos-media` you need to disable the old audio service and enable the OCP pipeline in `ovos-core`:

```json
{
  "enable_old_audioservice": false
}

```

```json
{
  "intents": {
    "pipeline": [
      "ovos-converse-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-high",
      "...",
      "ovos-common-query-pipeline-plugin",
      "ovos-ocp-pipeline-plugin-medium",
      "...",
      "ovos-ocp-pipeline-plugin-low",
      "ovos-fallback-pipeline-plugin-low"
    ]
  }
}

```

---

## Architecture

OCP (OVOS Common Play) splits into a **search/match layer** and a **playback layer**. The search
layer, made up of the [`ocp-pipeline`](ocp-pipeline.md), OCP skills (media catalogs), and stream extractors,
is shared regardless of which playback layer you run. The playback layer has two implementations
that currently run in parallel: the legacy ["old audio service"](media-plugins.md#ovos-ocp-audio-plugin)
(`ovos-ocp-audio-plugin` inside [`ovos-audio`](audio-service.md)) and the standalone `ovos-media`
daemon described here, which is the target:

```mermaid
flowchart TD
    Core["ovos-core intent pipeline"] --> Pipeline["ocp-pipeline-plugin"]
    Pipeline -->|"enable_old_audioservice: true (default)"| Legacy["ovos-ocp-audio-plugin (in ovos-audio)"]
    Pipeline -->|"enable_old_audioservice: false"| Media["ovos-media (standalone daemon)"]
    Media --> PSM["Player state machine (OCPMediaPlayer)"]
    Media --> MPRIS
    Media --> Backends["Media backend plugins"]
    Media --> GUI["GUI (external bus clients since 2.0.0a1)"]
```

*Diagram: the intent pipeline routes to either the legacy `ovos-ocp-audio-plugin` or the standalone `ovos-media` daemon, which drives the player state machine, MPRIS, backend plugins, and the GUI.*

---

## OCP Pipeline Plugin

The OCP pipeline plugin (`OCPPipelineMatcher`, import name `ocp_pipeline`) is the search/match
layer: it classifies a media request, dispatches search to OCP skills over the bus, picks the
best-scoring result, and routes it to the active player. It does NOT handle playback. Full
detail (classification, per-session player state, pipeline configuration, OCP skills, bus
messages) has moved to its own page: **[ovos-media OCP Pipeline Plugin](ovos-media-pipeline.md)**.

---

## ovos-media Player

**Entry point:** `ovos-media` (runs `ovos_media.__main__:main`). The installed console script
parses `--help` and `--version` and exits before starting the daemon or touching any socket.

Key modules:

- `ovos_media/player/__init__.py`: `OCPMediaPlayer`, the player state machine (playlist, track history, playback/media/loop state)
- `ovos_media/catalog/catalog.py`: `MediaCatalog` (aliased `OCPMediaCatalog` for back-compat, instantiated as the player's `self.media`) — a plain object with no bus subscriptions of its own, holding only the liked-songs store and search-results playlist
- `ovos_media/skill.py`: `OCPVoiceSkill`, an `OVOSCommonPlaybackSkill` subclass constructed separately from the player and given a reference to its catalog — the actual voice front-end, registering the now-playing intents and the liked-songs `@ocp_search`


- `ovos_media/media_backends/`: `AudioService`, `VideoService`, `WebService`. Each manages typed backend plugins


- `ovos_media/player/__init__.py`: pushes player state only through `ovos.common_play.*` bus broadcasts (2.0.0a1 dropped the in-process `GUIInterface` along with the old `ovos_media/gui.py` / `OCPGUIInterface`); any GUI, `ovos-control-panel` (formerly ovos-webui) included, is an outboard bus client


- `ovos_media/mpris.py`: MPRIS integration

### Available Media Backend Plugins

Media backends are typed: audio players register on the `opm.media.audio` entry-point group,
video players on `opm.media.video`, and web players on `opm.media.web`. They are configured under
`media.audio_players` / `media.video_players` / `media.web_players` (see the config example below).

The table below lists the **pip package** to install. Each package registers one entry point per
type it supports, named `ovos-media-<type>-plugin-<name>` (e.g. the `ovos-media-plugin-vlc`
package registers `ovos-media-audio-plugin-vlc` and `ovos-media-video-plugin-vlc`). You configure
the player by its entry-point name.

| Package | Types | Description |
|---|---|---|
| [`ovos-media-plugin-vlc`](https://github.com/OpenVoiceOS/ovos-media-plugin-vlc) | audio, video | VLC instance |
| [`ovos-media-plugin-mplayer`](https://github.com/OpenVoiceOS/ovos-media-plugin-mplayer) | audio, video | mplayer |
| [`ovos-media-plugin-cli`](https://github.com/OpenVoiceOS/ovos-media-plugin-cli) | audio | Generic CLI-command player, minimal/default audio fallback |
| [`ovos-media-plugin-spotify`](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify) | audio | Spotify Connect |
| [`ovos-media-plugin-chromecast`](https://github.com/OpenVoiceOS/ovos-media-plugin-chromecast) | audio, video | Cast to a Chromecast device |
| [`ovos-media-plugin-qt5`](https://github.com/OpenVoiceOS/ovos-media-plugin-qt5) | audio, video, web | Hand off to the [GUI](gui-service.md) player. **Legacy**, depends on the deprecated [ovos-shell](ovos-shell.md) (see [GUI status](gui-status.md)) |
| `ovos-media-plugin-mass` | audio | **Not yet published** (no public repo or PyPI package). Hands playback off to a [Music Assistant](https://music-assistant.io/) server. Does not implement `next()`/`previous()` through the legacy `AudioBackend` interface — only through the Music Assistant queue API (see Known Coupling Issues below) |
| `ovos-media-plugin-mpris` | audio, video | **Not yet published** (no public repo or PyPI package). Drives an external MPRIS player (e.g. an already-running desktop media app) instead of playing the stream itself |

[`music-assistant-plugin-manager`](https://github.com/TigreGotico/music-assistant-plugin-manager)
(`pip install music-assistant-plugin-manager`) loads out-of-tree Music Assistant providers
into a Music Assistant server, via its `music-assistant-community` wrapper command. It is
independent of `ovos-media` and only concerns the Music Assistant server itself, not OCP.

### Stream Extractor Plugins

OCP supports stream extractor plugins (`opm.ocp.extractor` entry-point group. The older
`ovos.ocp.extractor` group is a deprecated alias) that transform non-playable URIs into playable
streams before handing them to the media backend:

- `ovos-ocp-youtube-plugin`: extracts audio stream from YouTube URLs


- `ovos-ocp-m3u-plugin`: parses M3U playlists


- `ovos-ocp-rss-plugin`: parses podcast RSS feeds

---

## Media Intents

These are the utterances the [OCP pipeline plugin](ovos-media-pipeline.md#pipeline-configuration)
described above actually matches, at whichever confidence tier (`-high` / `-medium` / `-low`)
it's configured for. Before the regular intent stage, OCP handles these utterances (taking into
account current player state):

- `"play {query}"`: always available


- `"previous"`: requires media loaded


- `"next"`: requires media loaded


- `"pause"`: requires media loaded


- `"play"` / `"resume"`: requires media loaded


- `"stop"`: requires media loaded


- `"I like that song"`: **not matchable today** — `like_song.intent` and
  `play_favorites.intent` are commented out of the pipeline's intent list, so their files are
  never loaded, on either stack. The `ocp:like_song` / `ocp:play_favorites` handlers exist and
  the bus messages work; only the voice route is disabled.

### Now-Playing Intents

`OCPVoiceSkill` (the built-in `ovos-media` skill described under [ovos-media
Player](#ovos-media-player)) registers five regular padatious intents (en-us) about the
currently playing track: `WhatSong`, `WhatArtist`, `WhatAlbum`, `ShuffleOn`, and `ShuffleOff`.

`WhatSong` and `WhatArtist` answer from the player's global status
(`ovos.common_play.status`), the same read-only state every session gets back from a status
query — so these two intents answer on **any** session, not just the local device. `WhatAlbum`
always reports it has no album information: `MediaEntry` (the player's now-playing model) has
no album field to report, an upstream data-model limitation rather than a missing lookup.

`ShuffleOn` and `ShuffleOff` are different: they act on the player (`shuffle.set` /
`shuffle.unset`), so they follow the same session gating as any other playback-affecting
command — only the local/"default" session may trigger them, unless the owning `ovos-media`
was configured with `media.validate_source: false` (see [HiveMind: multi-session
gating](#hivemind-multi-session-gating)). On a non-default session the intent handler itself
declines before emitting anything, and speaks a dialog saying the device cannot be controlled
from here, rather than reporting success for a shuffle change that never happened.

---

## MPRIS Integration

`ovos-media` can register itself on D-Bus as an MPRIS player, so tools like `playerctl` and
desktop media widgets can control it, and can optionally reflect and take over other MPRIS
players already running on the machine. This only applies when running `ovos-media`, not the
default `ovos-audio` old-audioservice backend. The full setup, dbus verification steps, and
the Role A / Role B reflection-and-takeover behavior have moved to their own page:
**[ovos-media MPRIS Integration](ovos-media-mpris.md)**.

---

## Configuration

```jsonc
{
  "media": {
    "enable_mpris": false,       // expose OVOS playback on the MPRIS D-Bus interface
    "mpris_poll_interval": 1,    // seconds between MPRIS state polls (when enable_mpris)
    "ignored_players": [],       // MPRIS player names OVOS should not track/adopt
    "dbus_type": "session",      // "session" (per-user, default) or "system" D-Bus

    // when true, the daemon only acts on the local ("default") session.
    // set false for HiveMind/multi-session setups that drive playback remotely
    "validate_source": true,

    "preferred_audio_services": ["vlc", "mplayer", "cli"],
    "preferred_video_services": ["vlc", "mplayer"],
    "preferred_web_services": [],

    // force playback through the audio players even for video/web media, e.g. on headless setups
    // numeric PlaybackMode value from ovos_utils.ocp (30 = FORCE_AUDIO) or, since 2.0.0a1,
    // the enum name as a string ("FORCE_AUDIO")
    "playback_mode": 30,

    "audio_players": {
      "vlc": { "module": "ovos-media-audio-plugin-vlc", "aliases": ["VLC"], "active": true },
      "cli": { "module": "ovos-media-audio-plugin-cli", "aliases": ["Command Line"], "active": true }
    },
    "video_players": {
      "vlc": { "module": "ovos-media-video-plugin-vlc", "aliases": ["VLC"], "active": true }
    },
    "web_players": {
      "mpv": { "module": "ovos-media-web-plugin-mpv", "aliases": ["mpv"], "active": true }
    }
  }
}
```

`dbus_type` picks which D-Bus the MPRIS integration registers and scans on: the per-user
**session** bus (default) or the system-wide **system** bus. `playback_mode` forces media that
would normally need a video or web player through the audio players instead (`PlaybackMode`
values such as `FORCE_AUDIO`) — useful on a headless/speaker-only device that has no screen to
show video on. `web_players` configures `opm.media.web` backends the same way `audio_players`
and `video_players` do, keyed by local name with a `module` entry-point name.

> The `gui` / `browser` module names shown in earlier drafts are not real
> backends. The bundled players are `vlc`, `mplayer`, `cli`, `spotify`,
> `chromecast`, and the legacy `qt5` GUI hand-off (see the
> [backend table](#available-media-backend-plugins)).

!!! tip "Installed backend plugins load automatically"
    `audio_players`/`video_players`/`web_players` are optional. An installed backend plugin
    loads on its own. Use a `{type}_players` entry only to customize a plugin's name/aliases,
    reorder it, or disable it (`"active": false`). Set `"autoload_backends": false` under
    `media` to disable autoloading entirely. `Remote{Audio,Video,Web}PlayerBackend` subclasses
    (a backend driving a remote target) never autoload; they always need an explicit
    `{type}_players` entry, and configured entries always sort before autoloaded ones.

Each entry's key is a local name. `module` is the plugin's **entry-point name**
(e.g. `ovos-media-audio-plugin-vlc`), which can differ from its pip package name
(`ovos-media-plugin-vlc`). `preferred_*_services` are ordered fallback lists. The
audio list is also the generic fallback when a type-specific list is empty.

To hand playback to the legacy GUI player, add the `qt5` entry points
(`ovos-media-audio-plugin-qt5`, `…-video-plugin-qt5`, `…-web-plugin-qt5`). That
backend is legacy and needs the deprecated [ovos-shell](ovos-shell.md).

Other `media.*` keys read by the player (all optional): `autoplay` (default
`true`, play the next queued track automatically) and `merge_search` (fold new
search results into the active playlist vs. replacing it). The old
`force_audioservice` key was removed in 2.0.0a1; use `playback_mode` instead.

### First playback

`ovos-media` listens for `ovos.common_play.play` and expects a `media` dict plus an optional
`playlist` list:

```json
{
  "media": {
    "uri": "https://example.com/song.mp3",
    "title": "Some Jazz",
    "media_type": 2,
    "playback": 2
  },
  "playlist": [{"uri": "https://example.com/song.mp3", "title": "Some Jazz",
                "media_type": 2, "playback": 2}]
}
```

`media` is required — `handle_play_request` logs a warning and ignores the message without it.
If `playlist` is omitted, `ovos-media` builds a single-track playlist containing only `media`.
Either way, playing then **replaces** the player's current playlist outright: an
`ovos.common_play.play` message always overwrites whatever was set by an earlier
`ovos.common_play.playlist.set` message, whether or not it includes a `playlist` key, and
next/previous navigation after a bare `play` (no `playlist` key) only ever has the one track to
work with. To play a track as part of a larger playlist, include the full track list under
`playlist` in the same `ovos.common_play.play` message.

Query-style bus messages follow a `.response` suffix convention: the reply to `<msg_type>` is
emitted as `<msg_type>.response`. For example, `ovos.common_play.status` is answered on
`ovos.common_play.status.response`, and `ovos.common_play.track_info` on
`ovos.common_play.track_info.response`.

### Service-level bus messages

All service-level media control speaks `ovos.common_play.*` (2.0.0a1 dropped the per-player
`ovos.audio.service.*` / `ovos.video.service.*` bus surface). These bus messages
are handled inside the `ovos-media` process. The canonical reference for the full
`ovos.common_play.*` namespace is [Bus Events Reference: OCP / media playback](bus-events.md#ocp-media-playback);
this section covers only the service-level subset with `ovos-media`-specific behavior notes.

Two are on the `MediaService` daemon itself, in `_service_table()`
(`ovos_media/bus/api.py`): `ovos.common_play.ping`, the one to use for a liveness probe, and
`opm.audio.query` (OPM plugin-discovery compatibility with the legacy `PlaybackService`
handler). `ovos.common_play.home`, `.search.start` and `.search.end` are pipeline-side
signals — the OCP pipeline plugin uses them to drive a GUI's own navigation/loading state.
`ovos-media` has no in-process GUI and nothing else that reacts to them, so neither the daemon
nor the player subscribes to any of the three; a bus message with no subscriber here is legal.

The rest are registered by `OCPMediaPlayer`:

| Bus message | Purpose |
|---|---|
| `ovos.common_play.seek` | Seek within the current track |
| `ovos.common_play.playlist.set` / `.queue` / `.clear` | Replace, append to, or empty the playlist |
| `ovos.common_play.shuffle.toggle` / `.set` / `.unset` | Toggle or explicitly set/unset shuffle mode |
| `ovos.common_play.repeat.toggle` / `.set` / `.unset` | Toggle or explicitly set/unset repeat mode |
| `ovos.common_play.duck` / `.unduck` | Duck/restore volume for a competing sound (e.g. TTS) |
| `ovos.common_play.cork` / `.uncork` | Pause/resume playback for a competing sound, without ducking |
| `ovos.common_play.like` / `.unlike` | Mark or unmark the current track as a liked song |
| `ovos.common_play.status` | Report full current player status |
| `ovos.common_play.SEI.get` | Report the stream extractor identifiers `ovos-media` supports |

Ducking binds to ovos-audio's spec topics (`ovos.audio.output.started` / `.ended` trigger
duck/unduck since 1.0.0a1, which dropped the `recognizer_loop:audio_output_*` aliases), while
cork still listens on the legacy-style `recognizer_loop:record_begin` / `record_end`, since no
spec topic covers the mic-recording window. The full handler list, with each topic's `gated` value, is in `_player_table()`
(`ovos_media/bus/api.py`) — see [HiveMind: multi-session gating](#hivemind-multi-session-gating)
above.

`ovos.common_play.playlist.set` validates the payload before touching the playlist. A
non-list `tracks` value is ignored outright and the current playlist is kept. For a list
payload, each entry is checked on its own: invalid entries are skipped with a warning,
and the valid entries are applied.

---

## Stop & Error Semantics

A few guarantees hold for `OCPMediaPlayer` regardless of which backend is active:

- **Stop never advances the queue.** Whether it comes from the bus API, a legacy stop topic, or
  an MPRIS `Stop` command — including while a bad-stream retry is still pending — an explicit
  stop always ends on `PlayerState.STOPPED` with the queue position unchanged. Advancing to the
  next track only ever happens through the normal end-of-track / `next` paths.
- **Unplayable tracks are skipped, not fatal.** A track a backend cannot load emits
  `MediaState.INVALID_MEDIA` and the player schedules a delayed retry that moves on to the next
  track in the queue, rather than failing the whole playback request outright.
- **A queue that is entirely broken stops instead of looping forever.** If every track in the
  current queue has already failed to load since the last successful one, `ovos-media` stops
  playback (`PlayerState.STOPPED`) instead of retrying indefinitely — this applies both to
  `LoopState.REPEAT_TRACK` on a single failed track and to `LoopState.REPEAT` restarting a
  wholly-failed queue.
- **End of queue emits `PlayerState.STOPPED`.** Reaching the end of the queue with repeat off
  updates the player state (and notifies the GUI/MPRIS/bus) rather than leaving it at `PLAYING`
  with nothing left to play.
- **Duplicate URIs in a playlist advance by position, not first match.** A playlist like
  `[a, b, a]` tracks the currently-playing entry by object identity, falling back to playlist
  position and then to URI lookup only if identity is unavailable — so playback moves through
  the queue in order instead of ping-ponging back to the first track sharing a URI.

`ovos-media` also speaks three failure dialogs, each guarded so it does not talk over itself:

- **`no.playback.backend`** speaks once per daemon lifetime, at the first play attempt made
  while zero audio, video, or web backends are loaded. An install with no backend plugin fails
  every play request the same way, so the daemon does not repeat the warning on later attempts.
- **`track.failed`** is rate-limited to once per queue, not once per skipped track, so a run of
  several broken tracks in a row does not talk over itself.
- **`queue.finished`** speaks only when the queue is genuinely exhausted: every track played
  through in order and none remain. It does not fire when autoplay is off mid-queue, and it
  does not fire when an external MPRIS player's track ends.

The `track.failed` guard resets on real evidence of playback starting, not on a track merely
loading, so a track that loads fine but fails to play does not reset the rate limit early. The
`no.playback.backend` guard never resets: it is a once-per-lifetime warning, not a per-queue one.

Shuffle mode honors the same failure bounds (0.4.13a1): a shuffled pick excludes tracks whose
uri already failed this queue, and when nothing playable remains — every track failed, or the
queue is empty and the current track failed — the player stops and speaks `queue.finished`,
the same ending as sequential playback. Repeat mode with at least one good track keeps
playing. A shut-down player also stops reacting to duck/unduck/cork on every spelling it
listens on (`ovos.common_play.*`, the `ovos.audio.output.*` duck triggers, and cork's
`recognizer_loop:record_*`), so a dead daemon no longer adjusts system volume.

---

## Upcoming: MediaProvider plugins replace OCP skills

!!! info "What changes, and when"
    Media catalogs are moving **out of skills and into plugins**. A new **MediaProvider** plugin
    type (`opm.media.provider` / `PluginTypes.MEDIA_PROVIDER`) that the OCP pipeline loads
    **in-process** and calls `search()` on directly, in place of today's
    [OCP skills](ocp-skills.md). This first ships in **`ovos-plugin-manager 2.8.0a1`**
    (Phase 1 of the `ovos-media` migration). OCP skills remain the way to provide media for now.
    Tracked in [ovos-workshop#423](https://github.com/OpenVoiceOS/ovos-workshop/pull/423).

    A first batch of MediaProvider plugins now has **public repositories**, and all eleven
    listed below ship PyPI alpha releases. Installing them does nothing yet —
    the in-process loading is not wired into `ovos-media` (see below). Each one supersedes
    the catalog/search half of an older OCP skill:

    | MediaProvider plugin | Supersedes |
    |---|---|
    | [`ovos-media-provider-bandcamp`](https://github.com/OpenVoiceOS/ovos-media-provider-bandcamp) | [ovos-skill-bandcamp](https://github.com/OpenVoiceOS/ovos-skill-bandcamp) |
    | [`ovos-media-provider-pyradios`](https://github.com/OpenVoiceOS/ovos-media-provider-pyradios) | [ovos-skill-pyradios](https://github.com/OpenVoiceOS/ovos-skill-pyradios) |
    | [`ovos-media-provider-somafm`](https://github.com/OpenVoiceOS/ovos-media-provider-somafm) | [ovos-skill-somafm](https://github.com/OpenVoiceOS/ovos-skill-somafm) |
    | [`ovos-media-provider-soundcloud`](https://github.com/OpenVoiceOS/ovos-media-provider-soundcloud) | [ovos-skill-soundcloud](https://github.com/OpenVoiceOS/ovos-skill-soundcloud) |
    | [`ovos-media-provider-tunein`](https://github.com/OpenVoiceOS/ovos-media-provider-tunein) | [ovos-skill-tunein](https://github.com/OpenVoiceOS/ovos-skill-tunein) |
    | [`ovos-media-provider-youtube`](https://github.com/OpenVoiceOS/ovos-media-provider-youtube) | [ovos-skill-youtube](https://github.com/OpenVoiceOS/ovos-skill-youtube) |
    | [`ovos-media-provider-youtube-music`](https://github.com/OpenVoiceOS/ovos-media-provider-youtube-music) | [ovos-skill-youtube-music](https://github.com/OpenVoiceOS/ovos-skill-youtube-music) |
    | [`ovos-media-provider-mass`](https://github.com/OpenVoiceOS/ovos-media-provider-mass) | `ovos-skill-music-assistant` (playback via the companion `ovos-media-plugin-mass` backend) |
    | [`ovos-media-provider-news`](https://github.com/OpenVoiceOS/ovos-media-provider-news) | [ovos-skill-news](https://github.com/OpenVoiceOS/ovos-skill-news) |
    | [`ovos-media-provider-spotify`](https://github.com/OpenVoiceOS/ovos-media-provider-spotify) | [ovos-skill-spotify](https://github.com/OpenVoiceOS/ovos-skill-spotify) (playback via the companion [ovos-media-plugin-spotify](https://github.com/OpenVoiceOS/ovos-media-plugin-spotify) backend) |
    | [`ovos-media-provider-local`](https://github.com/OpenVoiceOS/ovos-media-provider-local) | Local file playback; uses `tinytag` (MIT) rather than `mutagen` (GPL) for metadata |

    The old OCP skills keep working; a MediaProvider plugin only takes over once the
    `opm.media.provider` plugin type ships on a released `ovos-plugin-manager`.

## Legacy Compatibility & Known Coupling Issues

`ovos-media`'s pipeline plugin falls back to the classic `mycroft.audio.service.*` bus messages
when `ovos-media` is not running, and bridges old pre-OCP `CommonPlaySkill` skills via `play:query`
/ `play:start`. It also carries some architectural coupling from that history, such as
`OCPVoiceSkill` registering itself as a skill and the Music Assistant backend's missing
`next()`/`previous()`. The full detail has moved to its own page:
**[ovos-media Legacy Compatibility](ovos-media-compat.md)**.

---

## HiveMind: multi-session gating

On a server that fans playback out to several [HiveMind](hivemind-agents.md) satellites, not
every bus handler should act on behalf of every session. `ovos_media/bus/api.py`'s single
registration table marks each playback-executing topic `gated`, and applies `is_default_session()`
(`ovos_media/utils.py`) before dispatching it. Every `ovos.common_play.*` topic that changes
player state is gated to the local ("default") session this way — the full playback-control set
(`play`, `pause`, `play_pause`, `resume`, `stop`, `next`, `previous`, `seek`,
`set_track_position`), the whole `playlist.*` group (`set`, `clear`, `queue`), the hardware-bound
`duck`/`unduck`/`cork`/`uncork` (which react to `ovos.audio.output.started`/`.ended` and
`recognizer_loop:record_begin`/`_end`), the whole `shuffle.*` and `repeat.*` groups,
`like`/`unlike`, and `ovos.utterance.handled`. Only the read-only/status topics
(`get_track_length`, `get_track_position`, `track_info`, `list_backends`, `status`,
`media.state`, `playback_time`, `SEI.get`) and a few others stay ungated — check
`_player_table()` in `ovos_media/bus/api.py` for the authoritative, current list rather than
treating this paragraph as exhaustive. Set `media.validate_source: false` on an instance that
must act on non-default/remote HiveMind sessions — see
[Updating: deployers](updating-deployers.md#native_sources-config-key-replaced-by-session-based-routing).

The `media.validate_source` config flag (see [Configuration](#configuration) above) controls how
strict this gating is:

- `true` (default): the daemon only acts on messages carrying the local "default" session.
  Correct for a single-device install where `ovos-media` and the microphone are the same box.
- `false`: needed on a server fronting multiple HiveMind satellites, so a satellite's own session
  can drive playback remotely instead of every command being silently scoped to "default".

Get this wrong on a server/satellite topology and playback commands from a satellite either get
ignored (`validate_source: true` on a multi-satellite server) or, worse, target the wrong
device's player state.

---

## Features

### Liked Songs

Like a currently playing song through the GUI, or over the bus with `ovos.common_play.like`.

The voice route is **disabled today**: `like_song.intent` and `play_favorites.intent` are
commented out of the OCP pipeline's intent list, so "I like that song" and "play my favorite
songs" never match. Use the GUI or the bus messages until they are re-enabled.

A `like` request with nothing playing and no explicit `uri` is refused, with spoken
feedback, instead of silently storing a junk entry with no way to remove it later.

### Skills Browse / Featured Media

Some skills provide `@ocp_featured_media()`. These are accessible from the OCP skills menu in the GUI.

### File Browser Integration

Selected files and folders will be played in OCP. Folders are treated as playlists.

---
**Read next:** [Screens on OVOS Today](gui-status.md) · [Concepts Overview](concepts-overview.md)
**Related:** [Audio Service](audio-service.md) · [ovos-media OCP Pipeline Plugin](ovos-media-pipeline.md) · [OCP Pipeline](ocp-pipeline.md) · [Media Playback Plugins](media-plugins.md) · [OCP Extractors](ocp-plugins.md) · [ovos-media MPRIS Integration](ovos-media-mpris.md) · [ovos-media Legacy Compatibility](ovos-media-compat.md)
