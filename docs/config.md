# Configuration Management

!!! abstract "In a nutshell"
    This page covers how you change OVOS's settings, such as your language, voice, and microphone. OVOS ships with a complete set of defaults you never touch. You write a small personal file listing only the things you want different. OVOS stacks your file on top of the defaults, so the rest stays as-is, like adding a sticky note over a printed form. The `ovos-config` command-line tool helps you view and edit those settings. For the full list of settings, see the [Configuration Reference](config-reference.md). For term definitions, see the [Glossary](glossary.md).

`ovos-config` is the configuration layer for the entire OVOS ecosystem. It provides a layered, merged `Configuration` singleton that all OVOS components read from, plus XDG-aware path helpers, a CLI tool, and meta-config support for custom distributions.

For a detailed list of every available configuration option, see the **[Configuration Reference](config-reference.md)**.

---

## Where config lives (start here)

OVOS ships a complete default config bundled inside the `ovos-config` package
(`mycroft.conf`). You never edit that file. Instead, you create a small file at
**`~/.config/mycroft/mycroft.conf`** containing only the keys you want to change.
Everything you don't mention keeps its default.

At read time OVOS stacks several files on top of each other and merges them. The
file closest to *you* wins:

```text
bundled default  →  remote cache  →  /usr/share/...  →  /etc/mycroft/...  →  ~/.config/mycroft/mycroft.conf  →  runtime patch
     lowest priority  ───────────────────────────────────────────────────►  highest priority
```

The **remote cache** is an optional layer holding settings pushed from a paired backend
(the legacy Mycroft-Home / `home.mycroft.ai` model). It sits low in the stack, so anything you
set by hand always wins. You can turn it off entirely with the `disable_remote_config`
system constraint. It is not the file you edit. See the [Config Layer Stack](#config-layer-stack)
below.

To switch to a German voice, you only need:

```json
{
  "lang": "de-de"
}
```

dropped into `~/.config/mycroft/mycroft.conf`. Dicts are deep-merged, so this leaves
every other setting untouched. This alone is enough: STT, TTS, and every other
language-aware plugin follow the global `lang` automatically. A per-plugin `lang`
setting only overrides that default for one plugin (for example, to keep a second voice
speaking another language). `ovos-config autoconfigure` (below) is a convenience
that also swaps in the recommended plugins and voices for a language. It is
not required just to switch languages. See [Language Support](lang-support.md) for
the full picture.

---

## Config Layer Stack

Layers are merged in this order. Later layers override earlier ones:

```text
MycroftDefaultConfig   (bundled mycroft.conf — read-only to OVOS itself; admins edit the file)
RemoteConf             (backend / paired-server cache — optional; disabled by disable_remote_config)
OvosDistributionConfig (/usr/share/mycroft/mycroft.conf — read-only to OVOS itself; admins edit the file)
MycroftSystemConfig    (/etc/mycroft/mycroft.conf — read-only to OVOS itself; admins edit the file)
MycroftUserConfig      (~/.config/mycroft/mycroft.conf — XDG user config)
__patch                (in-memory overlay applied last)

```

The XDG user layer is actually a list of configs (one per XDG config dir, for example
`/etc/xdg/mycroft/mycroft.conf` plus `~/.config/mycroft/mycroft.conf`), all merged
in order. All layers are `LocalConf` dict subclasses backed by a file. Only the user
config (`~/.config/mycroft/mycroft.conf`) should be edited by users. The **`RemoteConf`**
layer is the optional backend or paired-server settings cache (the legacy Mycroft-Home /
`home.mycroft.ai` model). It is merged low in the stack and can be turned off with the
`disable_remote_config` system constraint.

> The merge order in `load_all_configs()` is: default → remote → distribution → system →
> xdg user configs → in-memory patch. The remote layer is skipped when `disable_remote_config`
> is set, and the user/XDG layers when `disable_user_config` is set.

---

## Usage

```python
from ovos_config import Configuration

config = Configuration()
lang = config["lang"]                         # read a value
tts_module = config["tts"]["module"]          # nested access

# Persist a change to the user config file on disk (merges into ~/.config/mycroft/mycroft.conf)
from ovos_config.config import update_mycroft_config
update_mycroft_config({"lang": "de-de"})

# Pass a bus to also emit configuration.patch after writing, so other processes pick it up
update_mycroft_config({"lang": "de-de"}, bus=bus)

```

Because `Configuration` is a singleton, all instances share the same merged view. The framework calls `Configuration.load_all_configs()` automatically on first access.

---

## File Locations

All paths respect the `OVOS_CONFIG_BASE_FOLDER` environment variable (default: `"mycroft"`).

| Constant | Default Path | Description |
|---|---|---|
| `DEFAULT_CONFIG` | `<package>/mycroft.conf` | Bundled default config (read-only) |
| `DISTRIBUTION_CONFIG` | `/usr/share/mycroft/mycroft.conf` | Distribution-level override (env: `OVOS_DISTRIBUTION_CONFIG`) |
| `SYSTEM_CONFIG` | `/etc/mycroft/mycroft.conf` | System-level config (env: `MYCROFT_SYSTEM_CONFIG`) |
| `USER_CONFIG` | `~/.config/mycroft/mycroft.conf` | XDG user config (primary editable) |

In addition to `USER_CONFIG`, every XDG config dir is scanned, so a system-wide
`/etc/xdg/mycroft/mycroft.conf` is also merged at the user layer (below your
`~/.config` file). File formats are JSON (`.json` or `.conf`, with C-style `//`
comments supported) or YAML (`.yml` or `.yaml`).

!!! warning "Secrets and permissions"
    Anything you add here, such as an LLM API key, a Home Assistant token, or a custom
    server credential, is stored as **plaintext**, with no encryption or
    secrets manager. Restrict the file's permissions (`chmod 600`) on shared
    machines, and don't commit it to a public dotfiles repository. See
    [Privacy & Security](privacy-security.md#mycroftconf-can-contain-plaintext-secrets)
    for the full guidance.

---

## Usage Guide

**1. Create or edit your user config:**

```bash
mkdir -p ~/.config/mycroft
nano ~/.config/mycroft/mycroft.conf

```

Add only the keys you want to override. Everything else falls back to defaults.

**2. Override via environment variables (optional):**

```bash
export OVOS_CONFIG_BASE_FOLDER="myfolder"
export OVOS_CONFIG_FILENAME="myconfig.yaml"

```

**3. Use the CLI:**

```bash
ovos-config show                        # full merged config
ovos-config get -k lang                 # find all keys containing "lang"
ovos-config get -k /tts/module          # get exact value at tts.module
ovos-config set -k /tts/module -v ovos-tts-plugin-phoonnx
# if the key is a secret (llm.key, tokens), afterward: chmod 600 ~/.config/mycroft/mycroft.conf

```

See the **Secrets and permissions** warning above. `ovos-config set` does not restrict the file's permissions itself.

**Restart and verify**

`ovos-config set` writes the change to disk. It does not restart the running services. They
keep using the old value until you restart them:

```bash
# raspOVOS
ovos-restart

# any other systemd-managed install
systemctl --user restart ovos.service
```

Then confirm the new value took effect. For an STT or TTS server change, check the
voice/audio logs, or watch live traffic with [`ovos-busmon`](bus-service.md), to see which
server actually receives the request. See [STT server](stt-server.md#companion-plugin) and
[TTS server](tts-server.md#companion-plugin) for the plugin-side config keys.

---

## Protected Keys and System Restrictions

The system config (`/etc/mycroft/mycroft.conf`) can enforce constraints:

| Key in system config | Effect |
|---|---|
| `protected_keys` | Dict of `{"user": [...], "remote": [...]}`: keys stripped from the user / remote layer before merging |
| `disable_user_config` | If `true`, the user XDG config layer is ignored |
| `disable_remote_config` | If `true`, the remote / backend config layer is ignored |

These constraints are read from the `system` section, and **only** from the
distribution or system config. Values set in the default or user layers are
ignored. Nested keys use `:` as the separator (for example, `"listener:sample_rate"`).

Example: stop users from rebinding the messagebus host (must live in the `system` section of `/etc/mycroft/mycroft.conf`):

```json
{
  "system": {
    "protected_keys": {
      "user": ["gui_websocket:host", "websocket:host"]
    }
  }
}

```

> Admin [PHAL](phal.md) is a special service that runs as root. It can **only** access `/etc/mycroft/mycroft.conf`.

---

## Patch Mechanism

The `__patch` overlay is an in-memory dict merged on top of all file-backed layers. It is used for temporary overrides that should not be persisted to disk. Writing a key on the singleton goes into this patch:

```python
config = Configuration()
config["lang"] = "fr-fr"   # stored in the in-memory __patch layer

```

The patch is applied and cleared via `Configuration.patch(message)` and
`Configuration.patch_clear(message)`. Both are `@staticmethod`s that take a bus
`Message` (they read `message.data["config"]`), not a plain dict. In practice they
are driven by the bus handlers below rather than called directly.

---

## Bus Integration

`Configuration.set_config_update_handlers(bus)` registers the following listeners:

| Bus Event | Handler | Action |
|---|---|---|
| `configuration.updated` | `Configuration.updated` | Reload all config layers |
| `configuration.patch` | `Configuration.patch` | Apply `data["config"]` as an in-memory patch |
| `configuration.patch.clear` | `Configuration.patch_clear` | Clear the in-memory patch |
| `configuration.cache.clear` | `Configuration.clear_cache` | Drop the cached merged config |
| `mycroft.paired` | `Configuration.handle_remote_update` | Reload the remote/backend config layer |
| `mycroft.internet.connected` | `Configuration.handle_remote_update` | Reload the remote/backend config layer |

`Configuration.set_config_watcher()` uses `ovos-utils`' `FileWatcher` (watchdog) to monitor config files on disk. It reloads automatically when they change.

---

## Config Models

Each layer is a `LocalConf` instance, a file-backed `dict` subclass.

**Module:** `ovos_config.models`

| Class | Path | Notes |
|---|---|---|
| `LocalConf` | any path | Base class; supports JSON and YAML |
| `ReadOnlyConfig` | any path | Raises `PermissionError` on mutation (unless `allow_overwrite=True`) |
| `MycroftDefaultConfig` | bundled `mycroft.conf` | `ReadOnlyConfig` |
| `OvosDistributionConfig` | `/usr/share/mycroft/mycroft.conf` | `ReadOnlyConfig` |
| `MycroftSystemConfig` | `/etc/mycroft/mycroft.conf` | `ReadOnlyConfig` |
| `RemoteConf` | backend / paired-server cache | Optional remote layer (`LocalConf`) |
| `MycroftUserConfig` | `~/.config/mycroft/mycroft.conf` | Primary user layer (`LocalConf`) |

`MycroftUserConfig` is also exported under the alias `MycroftXDGConfig` for backward
compatibility.

```python
from ovos_config.models import LocalConf, MycroftUserConfig

# Direct access to a layer
user = MycroftUserConfig()
user["tts"] = {"module": "ovos-tts-plugin-phoonnx"}
user.store()   # write to disk

```

### `LocalConf` Key Methods

| Method | Description |
|---|---|
| `load_local(path=None)` | Read from `path` (or `self.path`) and merge into self |
| `store(path=None)` | Write current contents to disk |
| `merge(conf)` | Deep-merge another dict into self |
| `reload()` | Re-read from disk if the file changed since last load |

`LocalConf` uses a single shared class-level `NamedLock("ovos_config")` to coordinate concurrent reads and writes across all instances.

### Merge Semantics

- Scalar values: higher-priority layer wins


- Dict values: recursively merged


- List values: higher-priority layer replaces (no deduplication)

---

## Accessing Individual Layers

The individual layers are class attributes on `Configuration` (not per-instance):

```python
Configuration.default       # MycroftDefaultConfig
Configuration.remote        # RemoteConf — backend / paired-server cache (optional)
Configuration.distribution  # OvosDistributionConfig
Configuration.system        # MycroftSystemConfig
Configuration.xdg_configs   # list[LocalConf] — the user/XDG layer(s)

```

There is no `.user` attribute. The editable user config is the last entry in
`Configuration.xdg_configs`. To write the user file directly, use `MycroftUserConfig()`
(see Config Models above). Or call `update_mycroft_config()` to merge a change and emit the
`configuration.patch` bus notification in one step.

---

## Environment Variable Overrides

**Module:** `ovos_config.meta`

| Variable | Default | Effect |
|---|---|---|
| `OVOS_CONFIG_BASE_FOLDER` | `"mycroft"` | XDG subdirectory name for all config/data/cache paths |
| `OVOS_CONFIG_FILENAME` | `"mycroft.conf"` | Config filename inside the XDG config directory |
| `OVOS_DEFAULT_CONFIG` | package `mycroft.conf` | Path to the bundled default config |

The framework reads these at import time. Override at runtime:

```python
from ovos_config.meta import set_xdg_base, set_config_filename, set_default_config

set_xdg_base("my_distro")                        # changes ~/.config/my_distro/
set_config_filename("mycroft.conf")                  # changes filename
set_default_config("/opt/my_distro/default.conf") # changes bundled defaults

```

### Distribution Overrides

Distributions can change the default XDG base folder or config filename by setting environment variables:

- `OVOS_CONFIG_BASE_FOLDER`: changes `~/.config/mycroft/` to `~/.config/custom/` (default: `mycroft`).


- `OVOS_CONFIG_FILENAME`: changes `mycroft.conf` to `custom.json` (default: `mycroft.conf`).


- `OVOS_DEFAULT_CONFIG`: provides a full path to a custom default configuration file.

---

## XDG Path Helpers

**Module:** `ovos_config.locations`

```python
from ovos_config.locations import (
    get_xdg_config_save_path,   # e.g. ~/.config/mycroft/
    get_xdg_data_save_path,     # e.g. ~/.local/share/mycroft/
    get_xdg_cache_save_path,    # e.g. ~/.cache/mycroft/
    find_user_config,           # finds user config, with XDG→legacy fallback
    get_config_locations,       # ordered list of all active config paths
)

```

`get_config_locations()` returns the full list of active config file paths. It's useful for debugging which files are in use.

---

## CLI Reference

**Entry point:** `ovos-config` | **Module:** `ovos_config.__main__`

### `show`

```bash
ovos-config show                        # full merged config
ovos-config show -u --section tts       # user config, tts section only
ovos-config show -s -l                  # list sections of system config
ovos-config show -u --section base      # user config, top-level scalar keys

```

Merge priority displayed: `user > system > remote > default`

### `get`

```bash
ovos-config get -k lang                 # find all keys containing "lang"
ovos-config get -k /tts/module          # get exact value at tts.module (strict path)

```

### `set`

```bash
ovos-config set -k /tts/module -v ovos-tts-plugin-phoonnx
ovos-config set -k blacklisted_skills -v my-bad-skill   # append to list
ovos-config set -k gui                  # interactive: choose key and enter value

```

Values are type-cast to match the existing value's type. List targets append rather than replace.

### `autoconfigure`

Automatically configure language, [STT](stt-plugins.md), and [TTS](tts-plugins.md) from a language code:

```bash
ovos-config autoconfigure -l en-us --offline --female
ovos-config autoconfigure -l de-de --online --male

```

| Option | Description |
|---|---|
| `-l, --lang LANG` | BCP-47 language code (required) |
| `-hy, --hybrid` | Offline TTS + online STT (default when neither `--online` nor `--offline` is given) |
| `-on, --online` | Online STT and TTS |
| `-off, --offline` | Offline STT and TTS |
| `-p, --platform` | Optimize the config for a device: `rpi3`, `rpi4`, `rpi5`, `linux`, `mac`, or `termux` |
| `-g, --gpu` | Configure plugins for GPU (only valid together with `--offline`) |
| `-m, --male` / `-f, --female` | Default voice gender (if neither is given, TTS configuration is skipped) |

`--online`/`--offline` and `--male`/`--female` are each mutually exclusive pairs.
`--gpu` cannot be combined with `--online`/`--hybrid` or a Raspberry Pi platform.

### `telemetry`

```bash
ovos-config telemetry --enable    # opt in to intent telemetry upload
ovos-config telemetry --disable   # opt out

```

---

## Tips

- Always edit `~/.config/mycroft/mycroft.conf` (user layer). Never edit system or default files.


- JSON files support C-style `//` comments.


- `get_config_locations()` returns the full list of active config file paths for debugging.


- Use `disable_user_config` with caution. It silently skips the user layer.

---

## Related Pages

- [Bus Service](bus-service.md) — `websocket` config section


- [Bus Client](core-libraries.md#ovos-bus-client) — `websocket` and `session` config sections


- [ovos-core](core.md) — `skills`, `intents`, `utterance_transformers` config sections

## Package Layout

```text
ovos_config/
├── config.py       # Configuration singleton
├── models.py       # LocalConf, ReadOnlyConfig, layer classes
├── locations.py    # XDG path helpers and constants
├── meta.py         # Env var overrides (XDG base, filename, default config)
├── locale.py       # Language/timezone helpers
├── utils.py        # init_module_config(), deprecated FileWatcher re-exports
└── __main__.py     # ovos-config CLI (show / get / set / telemetry / autoconfigure)

```

---

## Entry Points

`ovos-config` registers no plugin entry points of its own. Every other OVOS component consumes it as a dependency.

The CLI is registered via `setup.py`:

```python
entry_points={
    "console_scripts": [
        "ovos-config=ovos_config.__main__:config"
    ]
}

```

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config).*
