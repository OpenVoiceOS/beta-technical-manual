# ovos-media Legacy Compatibility

!!! abstract "In a nutshell"
    How `ovos-media` and its OCP pipeline plugin stay compatible with the legacy audio backend and with old-style pre-OCP skills, plus the known architectural coupling issues carried over from that history. For the core `ovos-media` service this extends, see [ovos-media](ovos-media.md). For the legacy audio backend itself, see [Audio Service](audio-service.md).

---

## Legacy Compatibility

### ClassicAudioServiceInterface

When `ovos-media` is not running (i.e., the system still uses `ovos-ocp-audio-plugin` inside
`ovos-audio`), the pipeline plugin falls back to emitting `mycroft.audio.service.*` bus messages
to control the classic audio service via `ovos_bus_client.apis.ocp.ClassicAudioServiceInterface`.

### LegacyCommonPlay Bridge

For skills that still use the old Mycroft `CommonPlaySkill` base class (pre-OCP), the pipeline
plugin includes a bridge:

- Emits `play:query` instead of `ovos.common_play.query`


- Collects `play:query.response` from old-style skills


- Emits `play:start` to tell the winning skill to handle playback itself

This bridge is marked for removal in `ovos-core 0.1.0`.

---

## Known Coupling Issues

### OCPVoiceSkill is a skill

`OCPVoiceSkill` in `ovos_media/skill.py` inherits from `OVOSCommonPlaybackSkill`, constructed
separately from the player and given a reference to its `MediaCatalog` (`OCPMediaCatalog` is
now just a back-compat alias for the plain, skill-free catalog object). `OCPVoiceSkill` registers
`ovos-media` as a skill on the bus and loads skill infrastructure (settings, locale, etc.). It
registers `@ocp_search()` to expose liked songs as a search result. There is no
`@ocp_featured_media()` handler.

### Music Assistant next/prev delegate to the queue API

The Music Assistant audio backend's `next()`/`previous()` on the legacy `AudioBackend`
interface work: they delegate internally to Music Assistant's own queue API
(`next_track()`/`previous_track()`) rather than implementing track skipping themselves.

---
**Read next:** [ovos-media HiveMind: multi-session gating](ovos-media.md#hivemind-multi-session-gating)
**Related:** [ovos-media](ovos-media.md) · [ovos-media MPRIS Integration](ovos-media-mpris.md) · [Audio Service](audio-service.md)
