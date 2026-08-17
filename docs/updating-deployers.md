# Updating a Device or Fleet From Older OVOS (Config Changes)

## In a nutshell

This page is for people who operate an OVOS device or fleet and need to
track config-only changes: renamed keys, changed defaults, and removed
blocks in `mycroft.conf` and `ovos.conf`. Entries are in date order: start
at the version you are currently running and read forward to your target
version. For the Big-ticket migrations (the changes with the widest blast
radius, including the ovos-config 2.0.0 pipeline renames), see
[Updating from Older OVOS](updating-from-older-ovos.md#big-ticket-migrations).

## If you operate a device or fleet (config changes)

### Distribution config layer added, precedence order changed

`get_config_locations()` gained a `distribution=True` parameter and a new
layer, `/usr/share/<base_folder>/<config_filename>`, inserted between
DEFAULT and SYSTEM.

- Migration: [config](config.md) precedence is now DEFAULT < DISTRIBUTION
  (`/usr/share/...`) < SYSTEM (`/etc/...`) < web-cache (remote) < OLD_USER
  < USER. Distro packagers should install an overwrite-safe default to the
  DISTRIBUTION path.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | additive, not a removal | |
| Deprecated but functional | n/a | |
| Dropped | landed pre-`0.1.0` | (ovos-config `3781f01`, #128) |

### `mimic3` no longer the default TTS fallback

The default `tts.fallback_module` value `"ovos-tts-plugin-mimic3-server"`
and its settings block were removed from the shipped `mycroft.conf`.

- Migration: set `tts.fallback_module` and the settings block explicitly
  in your own config if a fallback [TTS](tts-plugins.md) is still wanted (mimic3 itself is
  deprecated upstream).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `bc9be86` | |
| Deprecated but functional | none | |
| Dropped | `bc9be86` (2023-11-05) | (ovos-config `bc9be86`, #81) |

`ovos-audio`'s matching default change (`tts.fallback_module` `"mimic"` →
`""`) landed separately in `c47e596` (2024-01-26).

### `mycroft.conf` no longer probes a mycroft-core install

`ovos_config/locations.py::find_default_config()` stopped checking for a
running mycroft-core installation as a source for the DEFAULT config
layer. Only the bundled `ovos_config/mycroft.conf` is used as DEFAULT.

- Migration: put overrides in SYSTEM/USER [config](config.md) layers
  (`/etc/mycroft/mycroft.conf`, `~/.config/mycroft/mycroft.conf`) instead
  of relying on a legacy mycroft-core file being picked up.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `0b16d46` | |
| Deprecated but functional | none | |
| Dropped | `0.1.0` (2023-12-28) | (ovos-config `0b16d46`, #90) |

### Default TTS fallback and MPRIS/lang-detect defaults changed

Three unrelated default-value changes landed in one `mycroft.conf` update:
`duck_while_listening` removed entirely (documented an unimplemented
feature), the default language-detection plugin switched to a
public-server-based one, and `mpris` under `Audio.backends.OCP` was
disabled by default.

- Migration: set `mpris: true` under `Audio.backends.OCP` (pre-`ovos-media`
  split. See the [OCP](ocp-pipeline.md)→[ovos-media](ovos-media.md) entry in the hub's Big-ticket migrations)
  if MPRIS is wanted. Pin the old [lang-detect plugin](translation-plugins.md) explicitly if
  network-free detection is required.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `bff2d72` | |
| Deprecated but functional | none | |
| Dropped | `bff2d72` (2024-02-26), dropped/changed | (ovos-config `bff2d72`, #112) |

### `native_sources` config key replaced by session-based routing

`ovos-audio`'s `native_sources` allowlist (gating playback-control bus
messages by `message.context["source"]`) was replaced by
`@require_default_session()`, gating on
`message.context["session"]["session_id"] == "default"` instead.

- Migration: remove `native_sources` from config/constructor calls. Ensure
  playback-control messages either omit `context.session` (defaults to
  `"default"`) or explicitly set `session_id: "default"`. See [Session](session.md)
  for how `session_id` scoping works.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `01499ee` | |
| Deprecated but functional | unverified | the gating decorator was introduced in `c5d95a4`, 2024-06-06, then replaced outright |
| Dropped | `01499ee` (2025-03-06) | (ovos-audio `01499ee`, #121) |

`ovos-media` landed the matching change with `require_default_session()`
plus a new `media.validate_source` (bool, default `True`) config key in
`4601792` (#58, 2026-06-26): set `media.validate_source: false` on a
central `ovos-media` instance that must act on non-default/remote
HiveMind sessions.

`ovos-media`'s `require_default_session()` decorator was itself replaced in
`72f6088` (#160, 2026-08-17, `2.0.0a3`): gating moved from a per-handler
decorator to a `gated` flag in `ovos_media/bus/api.py`'s single registration
table, checked with `is_default_session()` (`ovos_media/utils.py`) before
dispatch. `media.validate_source` still gates the same way. See
[ovos-media: HiveMind multi-session gating](ovos-media.md#hivemind-multi-session-gating)
for the current mechanism.

### Listener defaults changed (instant_listen, remove_silence, mic backend)

`listener.instant_listen` and `listener.remove_silence` flipped to enabled
by default (`54a0844`, #133, 2024-06-11). The default microphone module
was reverted from an interim `sounddevice`-family default back to `alsa`
once OPM plugin-fallback support made the missing-ALSA case safe
(`0bbec90`, #155, 2024-09-15).

- Migration: set `listener.instant_listen: false` and
  `listener.remove_silence: false` to restore old timing/silence behavior.
  explicitly pin a different mic backend if ALSA is unavailable on your
  host (OPM now falls back to `sounddevice` automatically on ALSA load
  failure).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | default-value changes, not deprecate-then-drop | |
| Deprecated but functional | n/a | |
| Dropped | `54a0844` (2024-06-11), `0bbec90` (2024-09-15) | |

### `ovos.conf` deprecated in favor of environment variables

The separate `ovos.conf` INI file controlling `base_folder`/
`config_filename`/XDG behavior is deprecated. Those values move
exclusively to environment variables.

- Migration: replace `ovos.conf` `[core] base_folder=...` /
  `config_filename=...` / `default_config_path=...` with the env vars
  `OVOS_CONFIG_BASE_FOLDER`, `OVOS_CONFIG_FILENAME`, and
  `OVOS_DEFAULT_CONFIG` (all introduced in the same commit that
  deprecated `ovos.conf`, `76d9310`, `ovos_config/meta.py`).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `76d9310` | |
| Deprecated but functional | from `76d9310` (2024-08-16) | |
| Dropped | drop version unverified | (ovos-config `76d9310`, #138) |

### `ready` settings block removed

The `"ready"` start-up gating config block (14 lines) was dropped entirely
from shipped `mycroft.conf` defaults.

- Migration: consult `ovos-core`'s listener release notes for the
  replacement readiness mechanism (the skill-based "finished booting"
  signal). `ready_settings`/`ready` keys have no default anymore.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `94f2348` | |
| Deprecated but functional | none | |
| Dropped | `94f2348` (2024-10-15) | (ovos-config `94f2348`, #166) |

On the `ovos-core` side, the matching `SkillManager.is_device_ready()`/
`check_services_ready()`/`handle_check_device_readiness()` methods
(deprecated since `1.0.0`) were removed outright in `62024dbf98` (#690,
2025-06-10, first stable `2.1.0`).

### Backend/microservices config block removed

The single largest config removal in `ovos-config`'s history. Removed
entirely from `mycroft.conf` and `ovos_config/models.py`:

- `opt_in` top-level telemetry key.
- `skills.upload_skill_manifest`, `skills.sync2way`, `skills.autogen_meta`.
- The entire `server` section (`backend_type`, `url`, `version`, `update`,
  `metrics`, `sync_skill_settings`).
- The entire `microservices` section (`wolfram_provider`,
  `weather_provider`, `geolocation_provider`, `wolfram_key`, `owm_key`,
  `email.*`).
- `protected_keys.remote` shrunk to drop the corresponding keys.

- Migration: route weather/Wolfram/geolocation provider config through
  each plugin's own config (for example a weather PHAL plugin's own
  `weather_provider`/API-key settings) instead of the removed centralized
  `microservices` block. `opt_in` telemetry has no replacement key.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `0a7a060` | |
| Deprecated but functional | unverified | |
| Dropped | `0a7a060` (2024-11-19) | (ovos-config `0a7a060`, #183) |

This mirrors `ovos-core`'s own `mycroft.api`/`DeviceApi` deprecation
toward `ovos-backend-client` (`ee9a14cb23`, 2022-10-04) and the full
removal of the `mycroft` compat package including Selene API support
(`2a10fa9c1c`, #439, 2025-03-04, first stable release `1.1.0`).

### `padatious_medium` dropped from default pipeline, later reinstated

- Migration: nothing to do on current installs. The stage returned to the shipped default
  pipeline as `ovos-padatious-pipeline-plugin-medium` in ovos-config `2.3.9a1` (`4d52513`,
  #289), so out-of-list entity-slot matches fire again by default. Only a deployment pinned
  between `1.0.2` and `2.3.9a1` needs to add it back explicitly in USER config (see
  [Pipelines Overview](pipelines-overview.md) and the
  [Padatious pipeline](padatious-pipeline.md) page).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `b08b7b8` | |
| Dropped | `b08b7b8` (2025-02-28, tag `1.0.2`) | (ovos-config `b08b7b8`, #200; maintainers' note at the time: "it is always wrong in benchmarks") |
| Reinstated | `4d52513` (first tag `2.3.9a1`) | (ovos-config `4d52513`, #289) |

### phoonnx becomes the default offline TTS in autoconfigure

Every `offline_male`/`offline_female` TTS recommendation in the
autoconfigure "recommends" registry now resolves to
`ovos-tts-plugin-phoonnx` instead of the prior per-language recommendation.

- Migration: pin the desired [TTS](tts-plugins.md) plugin explicitly under `tts.module` in
  `mycroft.conf` (see [Config Reference](config-reference.md)) if the old default is still wanted. Phoonnx requires its
  own model/voice availability per language.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | n/a | registry default change, not a removal |
| Deprecated but functional | n/a | |
| Dropped | landed `2a5bc3f` (2026-06-23) | (ovos-config `2a5bc3f`, #272) |

### `ovos_config.locale` helpers marked for removal

`get_full_lang_code`, `get_primary_lang_code`, `get_default_lang` in
`ovos_config/locale.py` now emit `DeprecationWarning` and lost their
internal caching. Signatures are unchanged so this is warning-only so far.

- Migration: switch to `ovos_config.Configuration()["lang"]` /
  `Configuration().get("lang")` directly ahead of the eventual hard
  removal.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `087a112` | |
| Deprecated but functional | from `087a112` (2026-07-24) | |
| Dropped | drop version unverified | the decorator's target version string reads a placeholder that does not match the current major line (ovos-config `087a112`, #253) |

---

**Read next:** [Version-Compatible Skills & Plugins](version-compat-guide.md) · [Upcoming Changes](upcoming-changes.md)
**Related:** [Updating from Older OVOS](updating-from-older-ovos.md) · [Production Operations](production-operations.md)
