# Music & Radio

!!! abstract "In a nutshell"
    OVOS plays internet radio, streamed news, and local audio/video files through
    **MediaProvider plugins**, not skills. Install a provider, and the [OCP pipeline](ocp-pipeline.md)
    picks it up automatically for any "play ..." request. See [MediaProvider plugins](ocp-pipeline.md#mediaprovider-plugins)
    for how the mechanism works.

!!! warning "The old OCP media skills are archived"
    `ovos-skill-pyradios`, `ovos-skill-somafm`, `ovos-skill-news`, and `ovos-skill-local-media`
    are archived. Their MediaProvider plugin replacements below are what to install today.

## PyRadios

A client for the Radio Browser API, a large, community-maintained directory of internet radio
stations.

**Usage examples:**

- play tsf jazz on pyradios
- play tsf jazz radio

```bash
pip install ovos-media-provider-pyradios
```

[:material-github: OpenVoiceOS/ovos-media-provider-pyradios](https://github.com/OpenVoiceOS/ovos-media-provider-pyradios)

## SomaFM

Listen to a variety of commercial-free internet radio stations from SomaFM.

**Usage examples:**

- play soma fm radio
- play metal detector
- play secret agent

```bash
pip install ovos-media-provider-somafm
```

[:material-github: OpenVoiceOS/ovos-media-provider-somafm](https://github.com/OpenVoiceOS/ovos-media-provider-somafm)

## News

News streams from around the globe.

**Usage examples:**

- play npr news
- play news in spanish
- play the news
- play portuguese news

```bash
pip install ovos-media-provider-news
```

[:material-github: OpenVoiceOS/ovos-media-provider-news](https://github.com/OpenVoiceOS/ovos-media-provider-news)

## Local Media

Browse and play audio/video files from a USB drive or local folder. Uses `tinytag` for metadata
rather than the GPL-licensed `mutagen`.

```bash
pip install ovos-media-provider-local
```

[:material-github: OpenVoiceOS/ovos-media-provider-local](https://github.com/OpenVoiceOS/ovos-media-provider-local)

!!! note "Playing your own music or a streaming service"
    Out of the box, OVOS plays internet radio (PyRadios, SomaFM) and local files. It does not
    include Spotify or another streaming-service provider by default. See
    [Cool Things You Can Do](showcase.md) and [Media Plugins](media-plugins.md) for what's
    available to add.

---

**Read next:** [Skill Examples](skill-examples.md)
**Related:** [OCP Pipeline](ocp-pipeline.md) · [Media Plugins](media-plugins.md) · [Cool Things You Can Do](showcase.md)
