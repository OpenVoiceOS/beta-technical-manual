# ovos-media MPRIS Integration

!!! abstract "In a nutshell"
    `ovos-media` can register on the D-Bus session bus as an MPRIS player (so tools like `playerctl` and desktop media widgets can control it) and, opt-in, can also reflect and take over other MPRIS players already running on the machine. For the core `ovos-media` service this extends, see [ovos-media](ovos-media.md).

!!! note "This is `ovos-media`'s support, not the stock-install default"
    MPRIS integration only exists when you're running `ovos-media` as the playback backend
    (`enable_old_audioservice: false`). The default `ovos-audio` old-audioservice backend does
    not provide it.

---

## MPRIS Integration

OCP integrates with MPRIS, allowing OCP to control and be controlled by external players.
Via MPRIS (and KDEConnect), OCP can display data from external players and control playback
in connected devices.

```json
{
  "media": {
    "enable_mpris": true,
    "dbus_type": "session"
  }
}

```

Confirm OCP is registered with dbus:

```bash
dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames

# Should show: "org.mpris.MediaPlayer2.OCP"

```

---

## External Player Reflection & Takeover

`OcpMprisExporter` (`ovos_media/mpris.py`) has two roles, referred to as **Role A** and
**Role B**. Role A is registering OCP itself on the D-Bus session bus (above), always active
once `enable_mpris` is set, and it is what lets an MPRIS client like `playerctl` control OCP:

```bash
playerctl --player=org.mpris.MediaPlayer2.OCP play-pause
playerctl --player=org.mpris.MediaPlayer2.OCP next
playerctl --player=org.mpris.MediaPlayer2.OCP metadata
```

Role B is the opt-in second role, and lets OCP *reflect and take over* other MPRIS players
already running on the same machine (Spotify, VLC, Firefox, and so on):

```json
{
  "media": {
    "enable_mpris": true,
    "manage_external_players": true
  }
}

```

With `manage_external_players` enabled, OCP periodically scans D-Bus for other
`org.mpris.MediaPlayer2.*` players and mirrors their metadata and playback state onto
its own OCP bus messages, so an external player's now-playing info shows up the same way
native OCP media does. When an external player starts playing, OCP automatically pauses
itself, and vice versa when the external player stops, so only one thing is audibly
playing at a time. OCP's own transport controls (skip/pause/shuffle/repeat) are proxied
through to whichever external player is currently active, letting one set of controls
(voice, GUI, or a remote MPRIS client) drive both native OCP media and third-party
players interchangeably.

---
**Read next:** [ovos-media Configuration](ovos-media.md#configuration)
**Related:** [ovos-media](ovos-media.md) · [ovos-media Legacy Compatibility](ovos-media-compat.md) · [Audio Service](audio-service.md)
