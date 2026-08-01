# OCP Plugins Reference

!!! abstract "In a nutshell"
    OCP (the OpenVoiceOS Common Play system) is the part of OVOS that plays media: music, podcasts, news, radio and the like. Each plugin on this page teaches it to handle one kind of source, such as YouTube links, Bandcamp pages, RSS feeds, or local files. So if you ask to play something, the right plugin knows how to find the actual audio stream and start it. See the [Glossary](glossary.md) for unfamiliar terms.

This page covers stream extractors: plugins that turn a URL or search request into a playable
stream. The playback engine that plays that stream is [OCP Audio Plugin](ocp-audio-plugin.md).
The playback backends it can use are [Media Playback Plugins](media-plugins.md).

--8<-- "snippets/what-ocp-means.md"

---

## Writing an OCP Stream Extractor Plugin

A stream extractor takes a URI a skill (or another extractor) produced and turns it into
the real, directly-playable URI OCP hands to a media backend. Subclass
`ovos_plugin_manager.templates.ocp.OCPStreamExtractor` and register it under the
`opm.ocp.extractor` entry-point group (`.config` group: `opm.ocp.extractor.config`).

### Abstract methods

```python
from typing import List, Optional

from ovos_utils import classproperty
from ovos_plugin_manager.templates.ocp import OCPStreamExtractor


class MyExtractor(OCPStreamExtractor):

    def __init__(self, ocp_settings: Optional[dict] = None):
        super().__init__(ocp_settings)

    @classproperty
    def supported_seis(cls) -> List[str]:
        """Stream Extractor Ids (SEIs) this plugin handles.

        A result URI of the form "{sei}//{uri}" is routed to this extractor
        regardless of what the rest of the URI looks like.
        """
        return ["myservice"]

    def extract_stream(self, uri: str, video: bool = True) -> Optional[str]:
        """Resolve uri to the real, playable stream URI.

        Called with the full raw uri, "{sei}//{id}" prefix included when routed
        via supported_seis. Return None if uri cannot be resolved.
        """
```

`validate_uri(uri)` is implemented by the base class: it returns `True` when `uri`
starts with `"{sei}//"` for one of `supported_seis`. Override it too if your plugin
should also claim *bare* URLs it recognizes without the `sei//` prefix (the pattern
[ovos-ocp-bandcamp-plugin](#ovos-ocp-bandcamp-plugin) uses for any URL containing
`bandcamp.`) — `StreamHandler` falls back to calling `validate_uri` on every extractor
for URIs no SEI claimed.

Override `runtime_requirements` (a `classproperty` returning a `RuntimeRequirements`
from `ovos_utils.process_utils`) if the plugin needs network/internet before it can even
load, or has an offline fallback. The default declares `requires_internet=True,
requires_network=True` with no fallback — appropriate for an extractor that scrapes a
web page or calls an API, wrong for one that only reads local files.

### Minimal complete example

**Project layout:**

```
ovos-ocp-myservice-plugin/
├── pyproject.toml
└── ovos_ocp_myservice_plugin/
    └── __init__.py
```

**`ovos_ocp_myservice_plugin/__init__.py`:**

```python
from typing import List, Optional

import requests

from ovos_utils import classproperty
from ovos_plugin_manager.templates.ocp import OCPStreamExtractor


class MyServiceExtractor(OCPStreamExtractor):

    @classproperty
    def supported_seis(cls) -> List[str]:
        return ["myservice"]

    def extract_stream(self, uri: str, video: bool = True) -> Optional[str]:
        # uri arrives as "myservice//<id>"; strip the sei prefix ourselves
        track_id = uri.split("//", 1)[-1]
        resp = requests.get(f"https://api.myservice.example/track/{track_id}")
        if resp.ok:
            return resp.json()["stream_url"]
        return None
```

**`pyproject.toml`**:

```toml
[project]
name = "ovos-ocp-myservice-plugin"
version = "0.1.0"
dependencies = ["ovos-plugin-manager", "requests"]

[project.entry-points."opm.ocp.extractor"]
ovos-ocp-myservice-plugin = "ovos_ocp_myservice_plugin:MyServiceExtractor"
```

### Unit-testing without OVOS

The base class takes no bus and no OVOS services, so a unit test is a direct call:

```python
from ovos_ocp_myservice_plugin import MyServiceExtractor

extractor = MyServiceExtractor()
assert extractor.validate_uri("myservice//abc123")
assert not extractor.validate_uri("https://open.spotify.com/track/xyz")
stream = extractor.extract_stream("myservice//abc123")
assert stream and stream.startswith("http")
```

### Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.ocp import find_ocp_plugins
print(find_ocp_plugins())
# {'ovos-ocp-myservice-plugin': <class 'ovos_ocp_myservice_plugin.MyServiceExtractor'>}
```

At runtime, `StreamHandler` (`ovos_plugin_manager.ocp.StreamHandler`) instantiates every
discovered extractor and dispatches `extract_stream` by matching `supported_seis` first,
falling back to `validate_uri` for bare URLs. Extractions can chain: if the resolved URI
is itself `"{sei}//..."` for another extractor, `StreamHandler` calls that one next.

### Publish checklist

1. The class subclasses `OCPStreamExtractor` and implements `extract_stream(uri, video)`
   with that exact signature, returning `None` (not raising) when it cannot resolve.
2. `supported_seis` returns a stable, unique SEI list; the entry-point group is
   `opm.ocp.extractor`.
3. `extract_stream` handles both the `"{sei}//<id>"` form and, if `validate_uri` is
   overridden, the bare-URL form it claims.
4. `runtime_requirements` reflects reality (network needed to resolve a URL, offline
   fallback available or not).
5. Unit tests call `extract_stream` directly, with no OVOS services running.
6. `find_ocp_plugins()` discovers the installed plugin under the expected name.

---

| Plugin | Description |
|--------|-------------|
| [ovos-ocp-files-plugin](#ovos-ocp-files-plugin) | Lets OCP play local files (`file://` URIs) and reads their audio tags/metadata so the player can show a title and artist |
| [ovos-ocp-news-plugin](#ovos-ocp-news-plugin) | Extracts the real stream for a known set of spoken-news provider URLs at playback time |
| [ovos-ocp-bandcamp-plugin](#ovos-ocp-bandcamp-plugin) | Scrapes Bandcamp pages via `py-bandcamp` to extract the real audio stream |
| [ovos-ocp-rss-plugin](#ovos-ocp-rss-plugin) | Parses an RSS/podcast feed and extracts the newest audio enclosure as the playable stream |
| [ovos-ocp-youtube-plugin](#ovos-ocp-youtube-plugin) | Resolves YouTube/YouTube Music URLs via a selectable `yt-dlp`/pytube/Invidious/webview backend |
| [ovos-ocp-m3u-plugin](#ovos-ocp-m3u-plugin) | Downloads a `.pls`/`.m3u` playlist and extracts the first playable stream URL inside it |
| [ovos-media-classifier](#ovos-media-classifier) | ⚠️ experimental: pluggable media-intent classifier that routes a request to the right `MediaProvider`s |

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
  playable stream.

---

## ovos-ocp-bandcamp-plugin

- **GitHub**: [ovos-ocp-bandcamp-plugin](https://github.com/OpenVoiceOS/ovos-ocp-bandcamp-plugin)


- **Description**: A stream extractor for [Bandcamp](https://bandcamp.com) pages, registering
  the SEI `bandcamp`. It recognizes both `bandcamp//<url>` results and any bare URL containing
  `bandcamp.`, then delegates the actual page scraping to the `py-bandcamp` library
  (`get_stream_data`) to pull out the real audio stream URL and track metadata.

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
  for resolving a channel's current live stream.

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

