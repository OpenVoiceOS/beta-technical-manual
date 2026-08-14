# Writing an OCP Stream Extractor Plugin

!!! abstract "In a nutshell"
    This page is the tutorial for building your own OCP stream extractor: the
    `OCPStreamExtractor` base class, its abstract methods, the entry point that makes a
    plugin installable, and how to test it. Looking for a plugin to use instead of writing
    one? Go to [OCP Plugins Reference](ocp-plugins.md).

A stream extractor takes a URI a skill (or another extractor) produced and turns it into
the real, directly-playable URI OCP hands to a media backend. Subclass
`ovos_plugin_manager.templates.ocp.OCPStreamExtractor` and register it under the
`opm.ocp.extractor` entry-point group (`.config` group: `opm.ocp.extractor.config`).

## Abstract methods

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

    def extract_stream(self, uri: str, video: bool = True) -> Optional[dict]:
        """Resolve uri to playable-stream metadata.

        Called with the full raw uri, "{sei}//{id}" prefix included when routed
        via supported_seis. Return None if uri cannot be resolved.
        """
```

!!! warning "Return a metadata dict, not a bare string"
    The base class in `ovos-plugin-manager` still type-hints `-> Optional[str]`, but the
    real consumers (`StreamHandler.extract_stream` and the OCP media layer) call `.get()`
    and `.items()` on the return value: return a **dict** with at least a `"uri"` key (plus
    any metadata such as `title` or `image`). Every shipping extractor (bandcamp, youtube)
    returns a dict. A bare string passes a direct unit test and then raises
    `AttributeError` the first time OCP routes a URI through your plugin.

`validate_uri(uri)` is implemented by the base class: it returns `True` when `uri`
starts with `"{sei}//"` for one of `supported_seis`. Override it too if your plugin
should also claim *bare* URLs it recognizes without the `sei//` prefix (the pattern
[ovos-ocp-bandcamp-plugin](ocp-plugins.md#ovos-ocp-bandcamp-plugin) uses for any URL containing
`bandcamp.`). `StreamHandler` falls back to calling `validate_uri` on every extractor
for URIs no SEI claimed.

Override `runtime_requirements` (a `classproperty` returning a `RuntimeRequirements`
from `ovos_utils.process_utils`) if the plugin needs network/internet before it can even
load, or has an offline fallback. The default declares `requires_internet=True,
requires_network=True` with no fallback. This is appropriate for an extractor that scrapes a
web page or calls an API, wrong for one that only reads local files.

---

## Minimal complete example

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

    def extract_stream(self, uri: str, video: bool = True) -> Optional[dict]:
        # uri arrives as "myservice//<id>"; strip the sei prefix ourselves
        track_id = uri.split("//", 1)[-1]
        resp = requests.get(f"https://api.myservice.example/track/{track_id}")
        if resp.ok:
            return {"uri": resp.json()["stream_url"]}
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

## Unit-testing without OVOS

The base class takes no bus and no OVOS services, so a unit test is a direct call:

```python
from ovos_ocp_myservice_plugin import MyServiceExtractor

extractor = MyServiceExtractor()
assert extractor.validate_uri("myservice//abc123")
assert not extractor.validate_uri("https://open.spotify.com/track/xyz")
stream = extractor.extract_stream("myservice//abc123")
assert stream and stream.startswith("http")
```

## Verify discovery

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

## Publish checklist

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
**Read next:** [OCP Plugins Reference](ocp-plugins.md)
**Related:** [OCP Audio Plugin](ocp-audio-plugin.md) · [Media Playback Plugins](media-plugins.md) · [Plugin Manager](plugin-manager.md)
