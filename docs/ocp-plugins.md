# OCP Plugins Reference

!!! abstract "In a nutshell"
    OCP (the OpenVoiceOS Common Play system) is the part of OVOS that plays media: music, podcasts, news, radio and the like. Each plugin on this page teaches it to handle one kind of source, such as YouTube links, Bandcamp pages, RSS feeds, or local files. So if you ask to play something, the right plugin knows how to find the actual audio stream and start it. See the [Glossary](glossary.md) for unfamiliar terms.

This page covers stream extractors: plugins that turn a URL or search request into a playable
stream. The playback engine that plays that stream is [OCP Audio Plugin](ocp-audio-plugin.md).
The playback backends it can use are [Media Playback Plugins](media-plugins.md).

--8<-- "snippets/what-ocp-means.md"

Writing a plugin instead of choosing one? See [Writing an OCP Stream Extractor Plugin](ocp-plugin-development.md), which covers the `OCPStreamExtractor` base class, its abstract methods, entry point registration, and testing.

---

| Plugin | Description | License | Maturity |
|--------|-------------|---------|----------|
| [ovos-ocp-files-plugin](#ovos-ocp-files-plugin) | Lets OCP play local files (`file://` URIs) and reads their audio tags/metadata so the player can show a title and artist | MIT | not rated |
| [ovos-ocp-news-plugin](#ovos-ocp-news-plugin) | Extracts the real stream for a known set of spoken-news provider URLs at playback time | Apache-2.0 | not rated |
| [ovos-ocp-bandcamp-plugin](#ovos-ocp-bandcamp-plugin) | Scrapes Bandcamp pages via `py-bandcamp` to extract the real audio stream | Apache-2.0 | not rated |
| [ovos-ocp-rss-plugin](#ovos-ocp-rss-plugin) | Parses an RSS/podcast feed and extracts the newest audio enclosure as the playable stream | Apache-2.0 | not rated |
| [ovos-ocp-youtube-plugin](#ovos-ocp-youtube-plugin) | Resolves YouTube/YouTube Music URLs via a selectable `yt-dlp`/pytube/Invidious/webview backend | Apache-2.0 | not rated |
| [ovos-ocp-m3u-plugin](#ovos-ocp-m3u-plugin) | Downloads a `.pls`/`.m3u` playlist and extracts the first playable stream URL inside it | Apache-2.0 | not rated |
| [ovos-media-classifier](#ovos-media-classifier) | ⚠️ experimental: pluggable media-intent classifier that routes a request to the right `MediaProvider`s | Apache-2.0 | not rated |

--8<-- "snippets/maturity-disclaimer.md"

!!! note "Maturity not yet rated for this family"
    These plugins are not yet individually rated in the manual (see the OCP comparison
    table in [Choosing Plugins](choosing-plugins.md#speech-input)). "not rated" means
    unrated, not unmature.

## ovos-ocp-files-plugin

- **GitHub**: [ovos-ocp-files-plugin](https://github.com/OpenVoiceOS/ovos-ocp-files-plugin)


- **Description**: A stream extractor that lets OCP play local files (`file://` URIs, or plain
  paths on disk) and reads their embedded audio tags (title, artist, album) so the player can
  display them. It bundles a fork of the `audio-metadata` tag-reading library.

---

## ovos-ocp-news-plugin

- **GitHub**: [ovos-ocp-news-plugin](https://github.com/OpenVoiceOS/ovos-ocp-news-plugin)


- **Description**: A stream extractor for spoken-news providers. It registers the stream
  extractor id (SEI) `news`, so any result URI of the form `news//<url>` is routed to it. It
  also recognizes a hardcoded table of known news-provider URLs directly (`URL_MAPPINGS`) so
  skills can hand it a raw provider URL without the `news//` prefix. At playback time it looks
  the URL up in that table and calls the matching extractor function to resolve the real,
  playable stream. The TSF (Portugal) source resolves the current bulletin by scraping it from
  TSF's listing page rather than guessing a predictable URL, since TSF now hosts bulletins on a
  CDN with unpredictable per-bulletin filenames. The GR1 (Italy) source resolves Rai's relinker
  URL server-side with a browser-like User-Agent before handing back the final stream, since the
  relinker rejects requests without one.

---

## ovos-ocp-bandcamp-plugin

- **GitHub**: [ovos-ocp-bandcamp-plugin](https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin)


- **Description**: A stream extractor for [Bandcamp](https://bandcamp.com) pages, registering
  the SEI `bandcamp`. It recognizes both `bandcamp//<url>` results and any bare URL containing
  `bandcamp.`, then strips the `bandcamp//` SEI prefix (if present) before delegating the actual
  page scraping to the `py-bandcamp` library (`get_stream_data`) to pull out the real audio
  stream URL and track metadata.

---

## ovos-ocp-rss-plugin

- **GitHub**: [ovos-ocp-rss-plugin](https://github.com/OpenVoiceOS/ovos-ocp-rss-plugin)


- **Description**: A stream extractor for RSS/podcast feeds, registering the SEI `rss`. Given a
  `rss//<feed-url>` (or bare feed URL), it parses the feed with `feedparser`, takes the most
  recent entry, and returns the first enclosure link whose MIME type contains `audio`, along
  with that entry's title, publish timestamp, and duration when the feed provides them. It only
  ever surfaces the newest playable item in the feed, not the whole episode list.

---

## ovos-ocp-youtube-plugin

- **GitHub**: [ovos-ocp-youtube-plugin](https://github.com/OpenVoiceOS/ovos-ocp-youtube-plugin)


- **Description**: A stream extractor for YouTube and YouTube Music links. Unlike the other
  extractors on this page, it is a small router over multiple interchangeable backends:
  `youtube-dl`/`yt-dlp`, `pytube`, an Invidious mirror, or a webview fallback, selectable via
  the `youtube_backend` / `ydl_backend` / `invidious_host` settings, since any single scraping
  approach tends to break whenever YouTube changes its page format. It also has a dedicated path
  for resolving a channel's current live stream. The `pytube` backend depends on
  `tutubo.pytube`, which only exists on `tutubo<3.0.0`; a newer `tutubo` is tolerated (the other
  backends keep working), but selecting the `pytube` backend against `tutubo>=3.0.0` raises a
  clear error telling you to pin `tutubo<3.0.0` or use the default `youtube-dl` backend instead.

---

## ovos-ocp-m3u-plugin

- **GitHub**: [ovos-ocp-m3u-plugin](https://github.com/OpenVoiceOS/ovos-ocp-m3u-plugin)


- **Description**: A stream extractor for `.m3u` and `.pls` playlist URLs, registering the SEIs
  `m3u` and `pls`. These playlist formats aren't understood by the GUI player directly, so the
  plugin downloads the playlist file itself and returns the first line that looks like an
  `http` stream URL as the actual playable URI.

---

## ovos-media-classifier

- **GitHub**: [ovos-media-classifier](https://github.com/OpenVoiceOS/ovos-media-classifier)


- **Description**: ⚠️ **Experimental. Work in progress, not yet deployed in OpenVoiceOS.**
  A self-describing, pluggable media-intent classifier: given a spoken request, it decides
  whether it is a media request at all and, if so, classifies it along several axes at once
  (media type, playback modality, structure, explicitness, tags, qualifiers) so OCP can route
  it to the right `MediaProvider`s and apply content policy. It is a router, not a
  resolver. It does not turn a title into a playable stream. The OCP stream-extractor
  plugins on this page do that.

---
**Read next:** [Media Playback Plugins](media-plugins.md)
**Related:** [OCP Audio Plugin](ocp-audio-plugin.md) · [OCP Pipeline](ocp-pipeline.md) · [Media Skills (OCP)](ocp-skills.md)

