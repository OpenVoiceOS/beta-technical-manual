# Locations

!!! abstract "In a nutshell"
    Like any program, OVOS keeps its settings files in specific folders on your computer. This
    developer reference lists where those folders are and the rules OVOS follows to find them.
    You need it only when you troubleshoot where a setting lives, or write code that reads
    configuration. See the [Glossary](glossary.md).

**Module:** `ovos_config.locations`

Path constants and XDG path helpers used by the rest of `ovos-config` to locate configuration files.

---

## Path Constants

All paths respect the `OVOS_CONFIG_BASE_FOLDER` environment variable (default: `"mycroft"`).

| Constant | Default Path | Description |
|---|---|---|
| `DEFAULT_CONFIG` | `<package>/mycroft.conf` | Bundled default config (read-only) |
| `DISTRIBUTION_CONFIG` | `/usr/share/mycroft/mycroft.conf` | Distribution-level override (env: `OVOS_DISTRIBUTION_CONFIG`) |
| `SYSTEM_CONFIG` | `/etc/mycroft/mycroft.conf` | System-level config (env: `MYCROFT_SYSTEM_CONFIG`) |
| `USER_CONFIG` | `~/.config/mycroft/mycroft.conf` | XDG user config (primary editable) |
| `ASSISTANT_CONFIG` | `~/.config/mycroft/runtime.conf` | OVOS's own runtime-write layer, merged below the user layer (the user config overrides it) |
| `WEB_CONFIG_CACHE` | `~/.config/mycroft/web_cache.json` | **Deprecated, not merged.** Leftover path for the removed remote-config layer (env: `MYCROFT_WEB_CACHE`); only `RemoteConf`, itself a warn-only stub, still reads it |

In addition to `USER_CONFIG`, every XDG config dir is scanned, so a system-wide
`/etc/xdg/mycroft/mycroft.conf` is also merged at the user layer, below your `~/.config`
file. See [Configuration: Config Layer Stack](config.md#config-layer-stack). File formats are JSON (`.json` or `.conf`, with C-style `//` comments supported) or
YAML (`.yml` or `.yaml`).

---

## XDG Path Helpers

These return the canonical XDG-compliant paths for config, data, and cache directories.

### `get_xdg_config_save_path()`

```python
from ovos_config.locations import get_xdg_config_save_path

path = get_xdg_config_save_path()

# e.g. "/home/user/.config/mycroft"

```

Returns the XDG config save directory for the current base folder. At import time the module
creates the user-config and web-cache directories. These helpers only build the path string.

### `get_xdg_data_save_path()`

```python
from ovos_config.locations import get_xdg_data_save_path

path = get_xdg_data_save_path()

# e.g. "/home/user/.local/share/mycroft"

```

Returns the XDG data save directory (path string only).

### `get_xdg_cache_save_path()`

```python
from ovos_config.locations import get_xdg_cache_save_path

path = get_xdg_cache_save_path()

# e.g. "/home/user/.cache/mycroft"

```

Returns the XDG cache save directory (path string only).

### `find_user_config()`

```python
from ovos_config.locations import find_user_config

path = find_user_config()

```

Returns the path to the user config file. It checks `USER_CONFIG` (XDG) first. If that file does
not exist on disk, it falls back to the legacy pre-XDG location `~/.mycroft/mycroft.conf`.

### `get_config_locations()`

```python
from ovos_config.locations import get_config_locations

paths = get_config_locations()

# returns list of all config paths in stack order

```

Returns a list of well-known config paths. Treat it as a rough guide, not as the load list:

- `~/.mycroft/mycroft.conf` is in the list but is never loaded. Only `find_user_config()`
  looks at it.
- `/etc/xdg/mycroft/mycroft.conf` is **not** in the list, but it is loaded — merged just
  before the user config, so the user's own file wins over it.
- The deprecated web-cache path sits fourth in this list, after default, distribution, and
  system. `load_all_configs()` does not merge it at all. `ovos-config` 3.0.0a1 dropped the
  remote-config layer as a breaking change.
- The path environment variables below are ignored — the function rebuilds
  `/usr/share/<base>/<file>` and `/etc/<base>/<file>` literally.

To see what is actually in play, print `get_xdg_config_locations()` together with the layer
paths on `Configuration`.

---

## Environment Variable Influence

| Environment Variable | Effect |
|---|---|
| `OVOS_CONFIG_BASE_FOLDER` | Replaces `"mycroft"` as the XDG subdirectory name |
| `OVOS_CONFIG_FILENAME` | Replaces `"mycroft.conf"` as the config filename |
| `OVOS_DEFAULT_CONFIG` | Absolute path to the bundled default config |
| `OVOS_DISTRIBUTION_CONFIG` | Absolute path to the distribution config |
| `MYCROFT_SYSTEM_CONFIG` | Absolute path to the system config |
| `MYCROFT_WEB_CACHE` | Absolute path to the remote-config cache |

The four absolute-path variables replace a whole path, so they are not affected by
`OVOS_CONFIG_BASE_FOLDER` or `OVOS_CONFIG_FILENAME`. The bundled default config does not use
the base folder at all: it resolves from `OVOS_DEFAULT_CONFIG` or the installed package
directory.

See [Configuration Management](config.md) for the full env var API.

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).*

---
**Read next:** [ovos-core Overview](core.md) · [Concepts Overview](concepts-overview.md)
**Related:** [Configuration Overview](config.md) · [Configuration Reference](config-reference.md) · [Composable Deployments](composable-deployments.md)
