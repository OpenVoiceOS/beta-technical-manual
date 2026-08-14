# Migrating Off ovos-utils 0.1.0

!!! abstract "In a nutshell"
    Any code that imports from `ovos_utils` written before late 2024 is
    affected. `ovos-utils` `0.1.0` deleted almost every helper the package
    had carried since the Mycroft era. Fix it by moving each import to its
    new home using the table below.

### The ovos-utils 0.1.0 gutting (2024-09)

A decade of accumulated helpers, inherited all the way back from the
Mycroft era, disappeared in a single release: `ovos-utils` 0.1.0 cut the
bulk of the package under the stated goal of removing "ALL dead code." From the
outside this meant imports breaking across the ecosystem the moment a
project bumped past the alpha stream, with no single traceback pointing at
the cause since the deleted symbols were scattered across messagebus,
configuration, intents, skills, and sound helpers alike. A cycle of
`@deprecated`/`log_deprecation` shims had named each symbol's new home
before the cut landed, and a couple of straggler shims survived the mass
deletion only to be swept away later.

`ovos-utils` 0.1.0 deleted almost everything that had accumulated in the
package since the Mycroft era (10,709 deleted lines, PR body: "remove ALL
dead code"). If you have any code importing from `ovos_utils` written
before late 2024, check it against this table.

| Old symbol (`ovos_utils.*`) | New home |
|---|---|
| `messagebus.get_message_lang`, `.get_websocket`, `.get_mycroft_bus`, `.send_message`, `.wait_for_reply`, `.decode_binary_message` | `ovos_bus_client.util.*` |
| `messagebus.dig_for_message`, `.FakeMessage`, `.Message`, `.FakeBus` | `ovos_utils.fakebus` |
| `messagebus.EventContainer` | `ovos_utils.events.EventContainer` |
| `messagebus.BusService`, `.BusFeedProvider`, `.BusQuery`, `.BusFeedConsumer` | removed, no replacement |
| `enclosure.api.EnclosureApi` | `ovos_bus_client.apis.enclosure.EnclosureApi` |
| `enclosure.mark1.*` (Mark1 eyes/faceplate/animations) | removed, no replacement in this repo. `ovos-PHAL-plugin-mk1` carries the eyes/faceplate/mouth handling instead |
| `configuration.*` (`get_default_lang`, `find_user_config`, `read_mycroft_config`, ...) | `ovos_config.config.*` / `ovos_config.locations` / `ovos_config.locale` |
| `fingerprinting.*` (`detect_platform`, `is_mycroft_core`, ...) | removed, no direct successor |
| `intents.IntentServiceInterface` | `ovos_workshop.intents` |
| `intents.IntentQueryApi` | removed, no replacement |
| `intents.converse.ConverseTracker` | removed, no replacement |
| `intents.layers.IntentLayers` | `ovos_workshop.decorators.layers.IntentLayers` |
| `ovos_service_api.OVOSApiService` | `ovos_backend_client.api.BaseApi` |
| `skills.blacklist_skill`, `.whitelist_skill` | `ovos_workshop.permissions.*` |
| `skills.get_skills_folder` | `ovos_plugin_manager.skills.get_default_skills_directory` |
| `skills.get_installed_skills` | `ovos_plugin_manager.skills.get_installed_skill_ids` |
| `skills.api.SkillApi` | `ovos_workshop.skills.api.SkillApi` |
| `skills.audioservice.AudioServiceInterface` | OCP (`OCPInterface`) |
| `skills.locations.*` | `ovos_plugin_manager.skills` |
| `skills.settings.*` (backend upload, folder-local settings) | removed, no replacement |
| `sound.play_acknowledge_sound` and friends | emit the bus message `mycroft.audio.play_sound` instead |
| `sound.record` | use `ovos-dinkum-listener` in recording mode |
| `sound.alsa.AlsaControl` | `ovos_phal_plugin_alsa.AlsaVolumeControlPlugin` |
| `gui.GUITracker`, `.GUIPlaybackStatus` | removed without replacement (`ovos-utils` `3a77617`, 2023-12-29) |

Migration action:

Old, before `0.1.0` — none of these import paths exist any more:

<!-- docs-check: skip-next -->
```python
from ovos_utils.messagebus import get_mycroft_bus, wait_for_reply
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.skills import blacklist_skill
```

New, `0.1.0` and later:

```python
from ovos_bus_client.util import get_mycroft_bus, wait_for_reply
from ovos_config.config import read_mycroft_config
from ovos_workshop.permissions import blacklist_skill
```

Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | any tag before `V0.1.0` | mycroft-core-derived helpers, no shims |
| Deprecated but functional | `80a2f7c` (2023-12-29) through the `0.1.0` alpha stream (`0.1.0a1`..`0.1.0a16`) | `@deprecated`/`log_deprecation` shims naming the replacement |
| Dropped | `V0.1.0` (2024-09-10; the mass deletion landed earlier in `3a77617`, 2023-12-29) | (ovos-utils `3a77617`) |

A follow-up removed the last messagebus shim module entirely: `ovos_utils.messagebus`
(a 1-line re-export left behind after 0.1.0) was deleted in `9c1fd55` (#304,
2024-11-21, between `0.5.0` and `0.6.0`), along with `mycroft_bus_client`
isinstance/constructor compatibility inside `ovos_utils.fakebus`
(ovos-utils `9c1fd55`).

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Skill Maintainers](updating-skills.md) · [For Plugin Maintainers](updating-plugins.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
