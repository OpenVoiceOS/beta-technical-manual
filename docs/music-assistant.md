# OVOS & Music Assistant

!!! abstract "In a nutshell"
    OVOS and [Music Assistant](https://music-assistant.io/) (MA) are two different
    open-source projects. OVOS can use an MA server as a media backend, and a HiveMind
    satellite can expose itself as a playback endpoint MA can stream to. There is no
    single combined install; pick the direction that matches what you want.

| Direction | What it does | Status |
|---|---|---|
| **OVOS plays media through MA** | An OVOS assistant searches and plays music/radio/podcasts via a running Music Assistant server | `ovos-media-provider-mass` public on PyPI; `ovos-media-plugin-mass` and `ovos-skill-music-assistant` are public repos, not yet on PyPI (see below) |
| **MA loads out-of-tree providers** | A Music Assistant server loads community-maintained providers not shipped with MA itself | [`music-assistant-plugin-manager`](https://github.com/TigreGotico/music-assistant-plugin-manager), public and on PyPI |
| **MA streams to an OVOS device** | Music Assistant sees an OVOS-powered device as a playback endpoint, browses its library, and streams to it | Via `hivemind-media-player` + Home Assistant's Music Assistant integration; see below |

---

## Direction 1: OVOS plays media through Music Assistant

Three pieces work together, all named after the [OCP media stack](ovos-media.md):

- **[`ovos-media-provider-mass`](https://github.com/OpenVoiceOS/ovos-media-provider-mass)**
  (public, PyPI): the catalog/search half. Registers under `opm.media.provider` as
  `music_assistant`, superseding the search half of `ovos-skill-music-assistant`.
- **[`ovos-media-plugin-mass`](https://github.com/OpenVoiceOS/ovos-media-plugin-mass)**:
  the playback backend for [`ovos-media`](ovos-media.md). Hands playback off to the MA
  server itself. Does not implement `next()`/`previous()` through the legacy
  `AudioBackend` interface, only through the Music Assistant queue API (see
  [Legacy Compatibility](ovos-media-compat.md)).
- **[`ovos-skill-music-assistant`](https://github.com/OpenVoiceOS/ovos-skill-music-assistant)**:
  the legacy OCP skill both of the above supersede.

`ovos-media-plugin-mass` and `ovos-skill-music-assistant` are public repos, not yet on
PyPI. Check PyPI before treating either as installable. `ovos-media-provider-mass` is
public and on PyPI, but installing it does nothing yet. `opm.media.provider` in-process
loading is not wired into `ovos-media` (see
[ovos-media](ovos-media.md#upcoming-mediaprovider-plugins-replace-ocp-skills)).

## Direction 2: Music Assistant loads out-of-tree providers

[`music-assistant-plugin-manager`](https://github.com/TigreGotico/music-assistant-plugin-manager)
(`pip install music-assistant-plugin-manager`) is independent of OVOS: it loads
community-maintained providers into a Music Assistant server via its
`music-assistant-community` wrapper command. Use it to run MA providers that aren't
shipped with MA itself, regardless of whether you also use OVOS.

## Direction 3: Music Assistant streams to an OVOS device

!!! info "Via Home Assistant, not a direct OVOS↔MA link"
    This path goes through Home Assistant: **Home Assistant is the HiveMind client**,
    not the OVOS device. It connects to whatever runs `hivemind-core` on the OVOS side
    and drives it as an admin, so it can trigger playback on the device's real
    `"default"` session rather than an isolated one. Music Assistant then sees the
    resulting HA entity as a playback endpoint. There is no direct
    HiveMind↔Music-Assistant protocol.

The OVOS side runs `hivemind-core` plus whatever agent answers `ovos.common_play.*`,
since it's the same bus messages regardless of what runs behind it. Two options:

- A full **[`hivemind-ovos-agent-plugin`](hivemind-agents.md)** node: a complete
  `ovos-core` install exposed over HiveMind. Heavier, but you get the whole assistant,
  not just playback.
- **[`hivemind-player-protocol`](https://github.com/JarbasHiveMind/hivemind-media-player)**:
  a lighter HiveMind agent plugin for when you only want playback and don't want to run
  full `ovos-core`. It currently embeds the legacy `ovos-audio` service, not
  [`ovos-media`](ovos-media.md); its status query does not yet report real player state.

Home Assistant needs an **admin** client to reach the device's real `"default"` session
instead of an isolated one translated away from it (see
[Session isolation between clients](hivemind-agents.md#session-isolation-between-clients)):

```bash
hivemind-core add-client --name home-assistant --admin
hivemind-core allow-msg "ovos.common_play.play" <NODE_ID>
hivemind-core allow-msg "ovos.common_play.pause" <NODE_ID>
hivemind-core allow-msg "ovos.common_play.resume" <NODE_ID>
hivemind-core allow-msg "ovos.common_play.stop" <NODE_ID>
hivemind-core allow-msg "ovos.common_play.next" <NODE_ID>
hivemind-core allow-msg "ovos.common_play.previous" <NODE_ID>
hivemind-core allow-msg "speak" <NODE_ID>
```

[`hivemind-homeassistant`](https://github.com/JarbasHiveMind/hivemind-homeassistant)
connects to `hivemind-core` with those credentials and, once you pick "Media Player" as
the device type in the HA config flow, exposes it as a `media_player` entity plus a
`notify` entity for TTS. Once that entity exists, Music Assistant (running as its own
Home Assistant integration) treats it like any other media player: it can browse your
library and stream to the device without further OVOS-side configuration.

---
**Related:** [ovos-media](ovos-media.md) · [HiveMind](hivemind-agents.md) · [Home Assistant](home-assistant.md)
