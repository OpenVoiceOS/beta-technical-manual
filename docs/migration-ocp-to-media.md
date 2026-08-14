# Migrating OCP Config to ovos-media

!!! abstract "In a nutshell"
    Deployers and plugin maintainers with an `OCP` config block are
    affected. Splitting audio-service responsibility into a dedicated
    `ovos-media` daemon renamed the config root key and flipped the MPRIS
    toggle's polarity. Fix it by moving `OCP` to `media` and setting
    `enable_mpris` explicitly if you want MPRIS on.

!!! note "Legacy audioservice and ovos-media are alternatives — pick one"
    Moving to `ovos-media` is an opt-in choice today. It takes two steps.
    Set `enable_old_audioservice: false` (the [switch](audio-service.md) that
    turns the legacy half off). Also install and run the separate
    `ovos-media` daemon. The flag alone leaves you with no media playback at
    all. The legacy audioservice stays installed either way, so the switch
    works in both directions (switching back means `true` + stopping
    `ovos-media`). Don't run both at once. See
    [Audio Service](audio-service.md) for the coexistence model this
    migration guide assumes.

### OCP → ovos-media config split

Splitting audio-service responsibility out of `ovos-audio` into a
dedicated `ovos-media` daemon moved its config with it. The config root
key also changed name in the process. Anything a deployer still
had under the old `"OCP"` key was silently ignored by the new service
rather than flagged as invalid.

The MPRIS toggle was renamed and its
polarity flipped in the same commit. A deployment that had never
touched the key at all still felt the change: MPRIS integration turned
itself off after the upgrade with no explicit setting to blame.

Audio-service responsibility split out of `ovos-audio` into a dedicated
`ovos-media` daemon starting January 2024. Two config changes to track:

Old, `mycroft.conf`, read by `ovos-media` before `89a50c0`:

```json
{"OCP": {"disable_mpris": false}}
```

New, `mycroft.conf`, `89a50c0` onward:

```json
{"media": {"enable_mpris": true}}
```

The config root key `OCP` was renamed to `media`. Anything still under
`"OCP"` is silently ignored by `ovos-media`. The MPRIS toggle was also
polarity-flipped. `disable_mpris` (default off, meaning MPRIS was **on** by
default) became `enable_mpris` (default `False`, meaning MPRIS is **off**
by default). A deployment that never touched this key gets a behavior
change. MPRIS integration silently turns off after upgrading past
`89a50c0` (ovos-media `89a50c0`, #19, 2024-03-29), unless `media.enable_mpris: true`
is set explicitly.

On the `ovos-audio` side, `AudioService.find_ocp()` stopped
auto-discovering OCP from the generic plugin list and instead instantiates
it directly, reading its config from the legacy `Audio.backends.OCP`
location as a documented transitional shim (ovos-audio `3983816`, #80,
2024-07-18).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Config root `OCP` (ovos-media) | before `89a50c0` (2024-03-29) | n/a | `89a50c0` (now `media`) |
| `disable_mpris` (MPRIS on by default) | before `89a50c0` | n/a | `89a50c0` (now `enable_mpris`, off by default) |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Device & Fleet Operators](updating-deployers.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
