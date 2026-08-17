# Music & Radio Skills

!!! abstract "In a nutshell"
    These skills play internet radio, streamed news, and local audio/video files.

## Music & Radio

### PyRadios

**Installer optional** (`extra-skills` feature)

A client for the Radio Browser API, a large, community-maintained directory of internet radio
stations.

**Usage examples:**

- play tsf jazz on pyradios
- play tsf jazz radio

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-pyradios](https://github.com/OpenVoiceOS/ovos-skill-pyradios) · `pip install ovos-skill-pyradios` · Maturity: Stable

### SomaFM

**Installer optional** (`extra-skills` feature)

Listen to a variety of commercial-free internet radio stations from SomaFM.

**Usage examples:**

- play soma fm radio
- play metal detector
- play secret agent

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-somafm](https://github.com/OpenVoiceOS/ovos-skill-somafm) · `pip install ovos-skill-somafm` · Maturity: Stable

### News

**Installer optional** (`extra-skills` feature)

News streams from around the globe.

**Usage examples:**

- play npr news
- play news in spanish
- play the news
- play portuguese news

Naming a specific feed by station name ("play euronews") or asking for Catalan news does not
reliably surface the right feed: the skill's language matcher does not cover Catalan and its
default-feed bonus can outrank a literal station-name match. Stick to the default feed or the
language phrasings above until that is fixed upstream.

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-news](https://github.com/OpenVoiceOS/ovos-skill-news) · `pip install ovos-skill-news` · Maturity: Stable

### Local Media

**Installer optional** (`extra-skills` feature)

Local media file browser for OpenVoiceOS. Browse and play audio/video files from a USB drive or
local folder.

**Usage examples:**

- open my file browser
- show my file browser
- show my usb drive
- start usb browser app
- show my usb

- show file browser app
- show file browser
- open usb
- start usb browser
- open my usb

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-local-media](https://github.com/OpenVoiceOS/ovos-skill-local-media) · `pip install ovos-skill-local-media` · Maturity: Mature

!!! note "Playing your own music or a streaming service"
    Out of the box, OVOS plays internet radio (PyRadios, SomaFM) and local files. It does not
    include Spotify or another streaming-service player by default. See
    [Cool Things You Can Do](showcase.md) and [Media Plugins](media-plugins.md) for what's
    available to add.

---

**Read next:** [Skill Examples](skill-examples.md)
**Related:** [OCP media skills](ocp-skills.md) · [Media Plugins](media-plugins.md) · [Cool Things You Can Do](showcase.md)
