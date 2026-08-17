# Troubleshooting Media and Playback

!!! abstract "In a nutshell"
    This page is the deep dive for Stage 7 of [Troubleshooting & Debugging](troubleshooting.md):
    what to check when a media request ("play some jazz") matched but nothing plays. It covers
    empty search results, stream extraction failures, and audio-sink problems. For hardware-level
    mic/speaker checks, see [Troubleshooting → Prove the microphone and speaker
    work](troubleshooting.md#prove-the-microphone-and-speaker-work) instead.

**Log:** `audio.log` (service `ovos-audio`, or `ovos-media` if enabled). **Bus filter:**
`ovos.common_play.query` / `ovos.common_play.query.response`, `ovos.common_play.status`

This stage only applies to media requests ("play some jazz", "next song"), not plain spoken
answers. It starts once [Stage 4](troubleshooting.md#stage-4-which-pipeline-stage-matched-or-didnt)
has already matched the utterance to the [OCP pipeline](ocp-pipeline.md)
(`ovos-ocp-pipeline-plugin-high` / `-medium` / `-low`). If OCP never claims the utterance at all,
that is a Stage 4 problem, not a Stage 7 one: check the pipeline miss log described there first.

---

## (a) Search found nothing

Once OCP classifies the utterance as a playback request, it emits `ovos.common_play.query` and
collects `ovos.common_play.query.response` results from every installed [OCP-enabled media
skill](ocp-skills.md). If no skill answers, or every answer is empty, OVOS reports it found
nothing to play.

Checks:

- Is an OCP-enabled media skill actually installed and loaded? Skills act purely as catalogs
  here, so with none installed there is nothing to search. See [Media Skills
  (OCP)](ocp-skills.md).
- Watch the query round-trip live in [`ovos-busmon`](troubleshooting-bus.md):
  filter by `ovos.common_play.query*` to confirm the query went out and see which skills (if any)
  answered, and with what results.
- Reproduce it without speaking: `ovos-say-to "play some jazz"` (see [Troubleshooting Stage
  3](troubleshooting.md#stage-3-did-stt-produce-text)), then check `skills.log` for the matching
  skill's search handler.

---

## (b) A result was found but the stream never starts

A search result is only a candidate URI. Before OCP can play it, a [stream
extractor](ocp-plugins.md) has to resolve that URI to the real, directly-playable stream (this is
what the `ovos-ocp-*-plugin` packages, e.g. `ovos-ocp-youtube-plugin` or
`ovos-ocp-bandcamp-plugin`, do). If the matching extractor is missing, misconfigured, or the
remote service it scrapes changes shape, extraction fails and playback never begins even though a
result was found.

Check `audio.log` (the [audio service](audio-service.md), which hosts the OCP audio plugin by
default, or `ovos-media`'s own log if that daemon is enabled instead) for an extractor exception
around the time of the request. See [OCP Plugins Reference](ocp-plugins.md) for which extractor
handles which source, and confirm the right one is installed for the kind of link the skill
returned.

---

## (c) Audio plays on the wrong output, or not at all

If a stream extracted fine but nothing (or the wrong device) makes sound, this is the same class
of problem as [Troubleshooting Stage 6](troubleshooting.md#stage-6-did-tts-speak)'s audio sink
failure, not a media-specific bug:

- Run the hardware and mixer checks in [Troubleshooting → Prove the microphone and speaker
  work](troubleshooting.md#prove-the-microphone-and-speaker-work) (`aplay -l`, `alsamixer`,
  `wpctl status` / `pactl list short sinks`) to confirm the speaker is present, unmuted, and set
  as the default sink.
- Check the OCP backend's audio configuration: the `preferred_audio_services` order it uses to
  pick a lower-level backend (shipped default `mpv`, `vlc`, `simple`), described in [OCP Audio
  Plugin](ocp-audio-plugin.md#configuration). A missing or misconfigured backend in that list can
  leave OCP with nothing to hand the stream to.

In [`ovos-busmon`](troubleshooting-bus.md), filter by `ovos.common_play.status` to see the
player's own state (playing, paused, stopped) regardless of whether sound is actually audible,
useful for telling apart "OCP thinks it's playing" (an audio sink problem) from "OCP never
started playing" (extractor or search problem, (a)/(b) above).

---
**Read next:** [Troubleshooting & Debugging](troubleshooting.md)
**Related:** [OCP Pipeline](ocp-pipeline.md) · [Media Skills (OCP)](ocp-skills.md) · [OCP Plugins Reference](ocp-plugins.md) · [OCP Audio Plugin](ocp-audio-plugin.md)
