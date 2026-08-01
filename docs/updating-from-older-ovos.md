# Updating From Older OVOS

## In a nutshell

This page is the upgrade companion for people who already run OVOS and need
to move to a newer version. It is not for people new to OVOS
(see [Coming From Mycroft](coming-from-mycroft.md)) and it is not for
porting Mycroft skill code (see [Migrating From Mycroft](migrating-from-mycroft.md)).
It is for a deployer or developer who has an OVOS stack from some past date
and wants to know exactly what changed between then and now.

Use it like this:

1. Find your role below: skill maintainer, plugin maintainer, device or
   fleet operator, or remote bus client (HiveMind and similar).
2. Read that section from the top. Entries are in date order. Start at the
   version you are currently running and read forward to your target
   version.
3. Each entry names the exact symbol, config key, or bus message that
   changed, the fix, and the commit that landed it. Use the commit sha to
   confirm the change against the source repository if you need more detail.
4. Every entry also states the compat lifecycle: when the old behavior was
   active, when it was deprecated but still worked, and when it was
   dropped. If you see "unverified" in a lifecycle column, that phase was
   not confirmed against the commit history. Check the
   [Verification gaps](#verification-gaps) list at the end before relying
   on it.

## How OVOS versions break

OVOS is not one project with one version number. It is about a dozen
independently released repositories (`ovos-core`, `ovos-workshop`,
`ovos-utils`, `ovos-config`, `ovos-bus-client`, `ovos-plugin-manager`,
`ovos-audio`, `ovos-media`, `ovos-messagebus`, the listener services, and
more), each on its own semantic-version line. A device upgrade usually
bumps several of these packages together, so a single "OVOS version" does
not exist. When something breaks after an upgrade, check the changelog of
the specific repository that owns the symbol or config key, not just
`ovos-core`.

The project follows a deprecate-then-drop pattern almost everywhere:

1. **Active**: the old behavior is the only behavior.
2. **Deprecated but functional**: a new replacement exists, the old path
   still works, and calling it logs a deprecation warning (`log_deprecation`
   or `@deprecated(...)`) or is gated behind a compatibility flag (for
   example `legacy_namespace`, `modernize`, `emit_legacy`).
3. **Dropped**: the old path is deleted. Calling it raises `ImportError`,
   `AttributeError`, `TypeError`, or the bus message is simply never sent
   or received again.

Each repository publishes its own changelog and tag history on GitHub
(`OpenVoiceOS/<repo>/releases` and `CHANGELOG.md` where present). When an
entry below says "nearest release," it means the dossier this page is
built from could not tie the change to an exact tag, so the closest
release date after the commit is given instead.

---

## Big-ticket migrations

These changes affect the largest number of installs and are worth their
own walkthrough before the chronological per-audience lists below.

### The ovos-utils 0.1.0 gutting (2024-09)

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
| `intents.*` (`IntentQueryApi`, `IntentServiceInterface`) | `ovos_workshop.intents` |
| `intents.converse.ConverseTracker` | removed, no replacement |
| `intents.layers.IntentLayers` | `ovos_workshop.decorators.layers.IntentLayers` |
| `ovos_service_api.OVOSApiService` | `ovos_backend_client.api.BaseApi` |
| `skills.blacklist_skill`, `.whitelist_skill` | `ovos_workshop.permissions.*` |
| `skills.get_skills_folder` | `ovos_plugin_manager.skills.get_default_skill_dir` |
| `skills.get_installed_skills` | `ovos_plugin_manager.skills.get_installed_skill_ids` |
| `skills.api.SkillApi` | `ovos_workshop.skills.api.SkillApi` |
| `skills.audioservice.AudioServiceInterface` | OCP (`OCPInterface`) |
| `skills.locations.*` | `ovos_plugin_manager.skills` |
| `skills.settings.*` (backend upload, folder-local settings) | removed, no replacement |
| `sound.play_acknowledge_sound` and friends | emit the bus message `mycroft.audio.play_sound` instead |
| `sound.record` | use `ovos-dinkum-listener` in recording mode |
| `sound.alsa.AlsaControl` | `ovos_phal_plugin_alsa.AlsaVolumeControlPlugin` |
| `gui.GUITracker`, `.GUIPlaybackStatus` | removed, no verified successor |

Migration action:

```python
# old (pre-0.1.0)
from ovos_utils.messagebus import get_mycroft_bus, wait_for_reply
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.skills import blacklist_skill

# new (0.1.0+)
from ovos_bus_client.util import get_mycroft_bus, wait_for_reply
from ovos_config.config import read_mycroft_config
from ovos_workshop.permissions import blacklist_skill
```

Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | any tag before `V0.1.0` | mycroft-core-derived helpers, no shims |
| Deprecated but functional | `80a2f7c` (2023-12-29) through the `0.1.0` alpha stream (`0.1.0a1`..`0.1.0a16`) | `@deprecated`/`log_deprecation` shims naming the replacement |
| Dropped | `V0.1.0` (2024-09-10, mass deletion in `3a77617`) | (ovos-utils `3a77617`) |

A follow-up removed the last messagebus shim module entirely: `ovos_utils.messagebus`
(a 1-line re-export left behind after 0.1.0) was deleted in `9c1fd55` (#304,
2024-11-21, between `0.5.0` and `0.6.0`), along with `mycroft_bus_client`
isinstance/constructor compatibility inside `ovos_utils.fakebus`
(ovos-utils `9c1fd55`).

### The ovos-workshop 2025-06 release train (4.0.0 → 7.0.0)

Four major versions of `ovos-workshop` shipped on the same day
(2025-06-07/08). Each is a separate breaking change to the `OVOSSkill`
family. If you are jumping from a pre-2025-06 workshop version to anything
after `7.0.0`, expect all four of these to apply at once.

**v4.0.0: `FallbackSkill.can_answer` becomes abstract.**

```python
# old: default True if any handler registered, no override needed
class MySkill(FallbackSkill):
    def handle_fallback(self, message):
        ...

# new: must implement can_answer explicitly
class MySkill(FallbackSkill):
    def can_answer(self, utterances: list[str], lang: str) -> bool:
        return True  # or real logic
    def handle_fallback(self, message):
        ...
```

`FallbackSkill.make_intent_failure_handler(cls, bus)` (the old mycroft-style
bus-driven fallback dispatcher) is removed with it (ovos-workshop `c066bc3`, #336).

**v5.0.0: converse moves out of `OVOSSkill` into a mixin.**

```python
# old: converse lived directly on OVOSSkill
class MySkill(OVOSSkill):
    def converse(self, message=None):
        ...

# new: subclass the mixin too
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(OVOSSkill, ConversationalSkill):
    def can_converse(self, message) -> bool:
        return True
    def converse(self, message=None):
        ...
```

An `OVOSSkill` subclass that overrides `converse()` without also inheriting
`ConversationalSkill` compiles fine but is silently never called by the
pipeline (ovos-workshop `f725f5e`, #339).

**v6.0.0 / v6.0.1: `can_stop` conditional abstract method.**
`can_stop(self, message)` briefly became a hard `@abc.abstractmethod`
(`10f9781`, #344) then was loosened the same day to only require
overriding if the skill also overrides `stop`/`stop_session`
(`813f7b5`, #346, released as `6.0.1`). If you implement `stop()` or
`stop_session()`, also implement `can_stop()`.

**v7.0.0: `can_answer` on `ConversationalSkill` renamed to `can_converse`.**
The v5.0.0 mixin shipped with the wrong method name for about a day. Rename
`can_answer` → `can_converse` in any `ConversationalSkill` subclass
(ovos-workshop `1fdd532`, #348).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `FallbackSkill.can_answer` concrete/optional | before `4.0.0` (2025-06-07) | unverified | `4.0.0` |
| `converse()` on `OVOSSkill` directly | before `5.0.0` (2025-06-07) | unverified | `5.0.0` |
| `stop_is_implemented` property / concrete `can_stop` | before `6.0.0` | `6.0.1` (conditional requirement) | `6.0.0` (briefly hard), loosened in `6.0.1` |
| `ConversationalSkill.can_answer` | `5.0.0` to `6.0.1` (about one day) | none | `7.0.0` |

### CommonQuerySkill removal

`CommonQuerySkill` had been deprecation-flagged since ovos-workshop
`4.0.0` and was deleted entirely (259 lines, including the `CQSMatchLevel`
enum and `CQS_match_query_phrase`/`CQS_action` abstract methods) in
`6382d0a` (#400, 2026-04-08), ahead of the `8.0.0` release. There is no
direct successor class in `ovos-workshop`. Common-query matching now lives
in whatever pipeline plugin currently owns it (check `ovos-core`'s
common-query pipeline plugin). On `ovos-core` itself, the equivalent
hardcoded common-query wiring was removed from `ovos_core.intent_services`
in `62024dbf98` (#690, 2025-06-10, first stable release `1.3.0`) when the
whole intent-service module became a config-driven OPM pipeline factory.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `ovos_workshop.skills.common_query_skill.CommonQuerySkill` | before `4.0.0` | `4.0.0` to pre-`8.0.0` | `6382d0a` (2026-04-08, pre-`8.0.0`) |
| `ovos-core` hardcoded common-query wiring | before `62024dbf98` | unverified | `62024dbf98` (`1.3.0`, 2025-06-10) |

### ovos-config 2.0.0: pipeline renames and `en-US` casing

`ovos-config` `2.0.0` (`e24e9ce`, #228, 2025-06-16) is the single largest
deployer-facing config break in the ecosystem. If you have a customized
`core.pipeline` list in your `mycroft.conf`, every stage ID in it is now
unregistered and will be silently skipped rather than erroring.

```json
// old core.pipeline (pre-2.0.0)
["stop_high", "converse", "ocp_high", "padatious_high", "adapt_high",
 "ocp_medium", "fallback_high", "stop_medium", "adapt_medium",
 "fallback_medium", "adapt_low", "common_qa", "fallback_low"]

// new core.pipeline (2.0.0+)
["ovos-stop-pipeline-plugin-high", "ovos-converse-pipeline-plugin",
 "ovos-ocp-pipeline-plugin-high", "ovos-padatious-pipeline-plugin-high",
 "ovos-adapt-pipeline-plugin-high", "ovos-ocp-pipeline-plugin-medium",
 "ovos-fallback-pipeline-plugin-high", "ovos-stop-pipeline-plugin-medium",
 "ovos-adapt-pipeline-plugin-medium", "ovos-fallback-pipeline-plugin-medium",
 "ovos-m2v-pipeline-high", "ovos-fallback-pipeline-plugin-low"]
// note: adapt_low and common_qa are dropped from the default list entirely
// (now standalone opt-in plugins); add "ovos-adapt-pipeline-plugin-low" and
// the common-query plugin id back explicitly if you still want them.
```

The same commit changed the default `"lang"` value in `mycroft.conf` from
`"en-us"` to `"en-US"`. Any code doing an exact string comparison against
the lowercase default breaks. Compare case-insensitively or update the
literal.

Also in this commit: `skills.directory` dropped from shipped defaults,
`gui.idle_display_skill` renamed `skill-ovos-homescreen.openvoiceos` →
`ovos-skill-homescreen.openvoiceos`, and the entire NLP-plugin config block
(`tokenization`, `segmentation`, `keyword_extract`, `coref`, `postag`) was
removed from `mycroft.conf` (no longer core-config-driven).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Short pipeline stage IDs (`stop_high`, `converse`, ...) | before `2.0.0` (2025-06-16) | unverified | `2.0.0` |
| `lang` default `"en-us"` | before `2.0.0` | n/a | `2.0.0` (now `"en-US"`) |
| `skills.directory` default key | before `2.0.0` | unverified | `2.0.0` |
| NLP plugin config block | before `2.0.0` | unverified | `2.0.0` |

### The bus-client legacy-topic dual-emit and its removal

This is the change every remote/HiveMind operator needs to plan for.
`ovos-bus-client` `2.x` introduced a transitional bridge so a mixed fleet
(core upgraded, satellites not yet upgraded) keeps working while topics
migrate from legacy `mycroft.*`/`recognizer_loop:*` spellings to the
`ovos.*` spec namespace:

1. `679f120` (#228, 2026-06-25): opt-in (default OFF) dual-emit + dedup bridge.
2. `e25ab12` (#230, 2026-06-25): split into two flags, **both default ON**
   during the migration window: `modernize` (env `OVOS_BUS_MODERNIZE`,
   config `websocket.modernize`) and `emit_legacy` (env
   `OVOS_BUS_EMIT_LEGACY`, config `websocket.emit_legacy`).
3. `4a08946` (#232, 2026-06-25): dedup logic delegated to
   `ovos_spec_tools.NamespaceTranslator` (shared with `FakeBus`).
4. `0f0a241` (#258, 2026-07-03): fixes a bug where the dual-emit doubled
   every message on the raw `on_message` firehose between #230 and this fix.
5. `f1a481d` (2026-08-01): **the bridge is removed entirely.**
   `MessageBusClient` speaks OVOS-MSG-1 spec topics only. The `emit_legacy`,
   `modernize`, and `intent_reemit_blanket` constructor flags are deleted.
   passing any of them now raises `RuntimeError`. A client or satellite
   still emitting or expecting legacy topic spellings stops being received
   with no fallback.

Migration: every producer and consumer must speak `ovos.*` spec topics
directly before upgrading past `f1a481d`. Remove any explicit
`emit_legacy`/`modernize`/`intent_reemit_blanket` arguments from your
`MessageBusClient` construction. The mapping tables
(`ovos_spec_tools.MIGRATION_MAP`, `SPEC_TO_LEGACY`) remain available for
migration tooling only, not for live bus wiring.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Legacy-only `mycroft.*`/`recognizer_loop:*` topics, no bridge | before `679f120` (2026-06-25) | n/a | superseded by dual-emit |
| Dual-emit bridge (`modernize`/`emit_legacy`, both default ON) | `e25ab12` (2026-06-25) | through `2.6.x` line | `f1a481d` (2026-08-01) |

### OCP → ovos-media config split

Audio-service responsibility split out of `ovos-audio` into a dedicated
`ovos-media` daemon starting January 2024. Two config changes to track:

```jsonc
// old (mycroft.conf, read by ovos-media before 89a50c0)
{"OCP": {"disable_mpris": false}}

// new (mycroft.conf, 89a50c0 onward)
{"media": {"enable_mpris": true}}
```

The config root key `OCP` was renamed to `media`: anything still under
`"OCP"` is silently ignored by `ovos-media`. The MPRIS toggle was also
polarity-flipped: `disable_mpris` (default off, meaning MPRIS was **on** by
default) became `enable_mpris` (default `False`, meaning MPRIS is **off**
by default). A deployment that never touched this key gets a behavior
change: MPRIS integration silently turns off after upgrading past
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

### Wake-word plugin `found_wake_word()` signature change (opm 2.0)

`ovos-plugin-manager` 2.0 changed the `HotWordEngine` contract: audio is
fed separately, then detection is polled with no arguments.

```python
# old (pre-opm-2.0)
class MyWakeWordPlugin(HotWordEngine):
    def found_wake_word(self, audio_data) -> bool:
        ...

# new (opm 2.0+)
class MyWakeWordPlugin(HotWordEngine):
    def update(self, chunk: bytes) -> None:
        ...  # feed audio incrementally
    def found_wake_word(self) -> bool:
        ...  # poll with no arguments
```

Both listener services in the org landed the caller-side half of this
change on the same underlying opm bump: `mycroft-classic-listener`
`19d9961` (#12, 2026-01-09) and `ovos-simple-listener` `34e2219` (#20,
2026-01-23, commit message: "opm 2.0.0 introduced breaking change"). If
your wake-word plugin still implements the one-argument form, it will be
called with zero arguments and raise a `TypeError` on any listener service
updated past these commits.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `found_wake_word(audio_data)` one-arg form | before opm `2.0.0` | unverified | opm `2.0.0` · caller-side landed in `19d9961` / `34e2219` |

### Audio-transformer chain-order flip

`ovos-dinkum-listener`'s `AudioTransformersService` sorted plugins by
`priority` **descending** (highest number ran first) with a docstring that
said the opposite of what the OVOS-TRANSFORM-1 spec expects. `1fd909f`
(#236, 2026-06-28) dropped `reverse=True`: the chain now runs in
**ascending** priority order (lowest number first, highest last), matching
`OVOS-TRANSFORM-1 §4` and the ordering `ovos-core` already used for its own
transformer chains.

```python
# old: priority=1 ran LAST (reverse=True)
# new: priority=1 runs FIRST (ascending)
```

If you assigned `priority` values assuming the old descending order,
invert them: old `priority=P` behaved like new `priority=(100-P)` in
relative terms. Any deployment with more than one active
`listener.audio_transformers` plugin where order matters can see a silent
behavior change after upgrading past this commit (ovos-dinkum-listener `1fd909f`, #236).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Descending `priority` sort (`reverse=True`) | before `1fd909f` (2026-06-28) | n/a | `1fd909f` |

---

## If you maintain skills

### mycroft-core `MycroftSkill` compat shim removed

The metaclass hack that let `isinstance(skill, MycroftSkill)` succeed for
both classic Mycroft skills and OVOS skills, and that auto-initialized
classic-style skills, was removed. Skills built for mycroft-core no longer
load.

- Migration: subclass `ovos_workshop.skills.ovos.OVOSSkill` directly.
  Skill lifecycle is now entirely `SkillLoader`-driven: `bus`/`skill_id`
  are passed to `__init__`, not injected via metaclass into a later
  `initialize()` call.
- Lifecycle: active pre-`2d684a1`. Deprecated with warnings through the
  `V0.0.x` era. Dropped in `1.0.0` (ovos-workshop `2d684a1`, #235,
  2024-10-15). The maintainers later bumped `VERSION_MAJOR` to `8` in
  `7c8a1e4` (2025-11-09) purely to acknowledge, after the fact, that this
  should have been versioned as a major bump: treat `2d684a1`/`1.0.0` as
  the real boundary.

### `ovos_workshop.decorators.compat.backwards_compat` removed

The `backwards_compat(classic_core=, pre_008=, no_core=)` decorator, which
branched behavior by detecting `mycroft.version.CORE_VERSION_STR` /
`ovos_core.version`, was deleted along with the mycroft-skill compat shim.

- Migration: remove any use of `backwards_compat`. Branch on your own
  feature-detection logic if you still need version-conditional behavior.
- Lifecycle: active pre-`2d684a1`. Unverified deprecation window. Dropped
  `1.0.0` (ovos-workshop `2d684a1`, #235).

### `ovos_workshop.skills.decorators.*` shim paths removed

The 2022 move of decorators from `skills.decorators.*` to top-level
`decorators.*` (`9ca2018`, 2022-06-02) had kept 4-line re-export shims at
the old paths. Those shims were deleted with no further compat.

- Migration: `from ovos_workshop.skills.decorators.killable import
  killable_intent` → `from ovos_workshop.decorators.killable import
  killable_intent` (same pattern for `ocp`, `layers`, `converse`,
  `fallback_handler`).
- Lifecycle: active before `9ca2018` (2022-06-02). Deprecated but
  functional (shim re-export) `9ca2018` to pre-`1.0.0`. Dropped `1.0.0`
  (ovos-workshop `2d684a1`, #235).

### `OVOSSkill._conditional_activate()` removed

The private helper that auto-re-activated a skill after converse/intent
handling, and the skill class's own emission of `ovos.utterance.handled`,
are both gone: that bookkeeping moved into `ovos-core`'s fallback
pipeline to stop duplicate events.

- Migration: remove any override or call of `_conditional_activate`. Do
  not assume the skill class emits `ovos.utterance.handled` yourself.
- Lifecycle: active before `6649c4f`. Unverified deprecation window.
  dropped `2.0.0` (ovos-workshop `6649c4f`, #262, 2024-10-31).

### Backend settings sync removed from `OVOSSkill`

`enable_settings_manager` kwarg, `self.settings_manager`,
`self._settings_meta`, and `SkillSettingsManager` (Selene/backend
two-way settings sync, `settingsmeta.json` auto-upload) are all removed.

- Migration: remove `enable_settings_manager` from `super().__init__()`
  calls. Use `self.settings` (local `JsonStorage`) only. There is no
  backend settings sync in OVOS.
- Lifecycle: active before `3c026c2`. Unverified deprecation window.
  dropped `3.0.0` (ovos-workshop `3c026c2`, #295, 2024-11-19).

### Skill locale directories renamed to canonical BCP-47

Bundled locale directories under `ovos_workshop/locale/` were renamed from
lowercase/short codes (`en-us`, `da`, `eu`, `fa-fa`) to canonical BCP-47
(`en-US`, `da-DK`, `eu-ES`, `fa-IR`) to fix duplicate zip entries in wheel
builds.

- Migration: ship resource files under canonical BCP-47 folder names. Use
  `ovos_utils.lang.get_language_dir()` / `CoreResources` for resolution
  instead of manual lowercase path construction.
- Lifecycle: active before `e12559e`. Unverified deprecation window.
  dropped `e12559e` (2026-04-03), pre-`8.0.0` (ovos-workshop `e12559e`, #392).

### `_get_dialog()` removed as a public symbol

Module-level `_get_dialog()` on `ovos_workshop.skills.ovos` no longer
exists. Locale lookups (`_get_dialog`, `_get_word`,
`CommonQuerySkill.__init__`, `translated_noise_words`) all route through
`CoreResources`/`self.resources` now.

- Migration: use `self.speak_dialog(key)` or
  `CoreResources(lang).load_dialog_file(...)` instead of importing
  `_get_dialog` directly.
- Lifecycle: active before `acbd438`. Unverified deprecation window.
  dropped `acbd438` (2026-04-08), pre-`8.0.0` (ovos-workshop `acbd438`, #395).

### Legacy non-installable skill loading removed

`skill_launcher.py` dropped the remaining dead code paths for loading
non-pip-installable, classic-mycroft-style skills.

- Migration: package skills as installable Python packages with entry
  points. Loose-file skill loading from a bare folder is unsupported.
- Lifecycle: active before `421899f`. Unverified deprecation window.
  dropped in the `7.0.x` line, `421899f` (2025-06-21), (ovos-workshop `421899f`, #362).
  `ovos-core`'s own equivalent removal of folder-based skill loading
  (`_load_skill`, `_get_skill_directories`, `_unload_removed_skills`)
  landed the same era in `62024dbf98` (#690, 2025-06-10, `1.3.0`).

### Skill-settings file-store rewritten

Skill settings moved to `json_database`-backed XDG-default storage,
replacing the old ad-hoc file kludge, with a one-time auto-migration.

- Migration: rely on the `self.settings` API. Do not read/write the old
  non-XDG settings file path directly.
- Lifecycle: active before `3299173`. Unverified deprecation window (the
  dossier records a one-time auto-migration, not a hard cutover date).
  dropped `3299173734` (2022-02-02), (ovos-core `3299173`, #11).

### Fallback dispatcher no longer bus-driven

`converse` and fallback dispatch became event-based through dedicated
services (`ConverseService`, the fallback pipeline) instead of being
called directly in-process on `MycroftSkill` instances.

- Migration: implement the converse acknowledge handshake if you drive
  converse externally (for example a custom orchestrator). Do not assume
  `converse()` is polled for skills that never override it.
- Lifecycle: active before `4fff98e`. No deprecation window (architecture change, not a
  deprecate-then-drop symbol). Landed `4fff98ecfc` (2022-02-02), (ovos-core `4fff98e`, #32).

---

## If you maintain plugins

### TTS plugin queue tuple shape (ovos-audio)

Direct mutation of `TTS.queue` used a 6-tuple
`(_, data, visemes, ident, listen, tts_id)`. It now expects a 5-tuple
`(data, visemes, listen, tts_id, message)`.

- Migration: push `(data, visemes, listen, tts_id, message)` tuples onto
  `PlaybackThread`'s queue.
- Lifecycle: active before `931784a`. Deprecated but functional (logs via
  `log_deprecation(..., "0.1.0")`) from `931784a` (2023-10-25). Dropped
  target was `0.1.0`: exact drop commit unverified (ovos-audio `931784a`, #37).

### Audio-backend template methods became abstract

`AudioBackend`/`RemoteAudioBackend` templates in `ovos-plugin-manager`
turned previously-optional methods into `@abstractmethod`, and dropped the
dependency on the old `common_play` base class (OCP's predecessor).

- Migration: implement every required method on your `AudioBackend`
  subclass or instantiation raises `TypeError: Can't instantiate abstract
  class`.
- Lifecycle: active before `77c66a3`. Unverified deprecation window.
  dropped `77c66a3` (2024-05-11), (ovos-plugin-manager `77c66a3`, #226).

### STT legacy helper classes deprecated

`StreamingSTT`, `StreamThread`, and related classic-mycroft-derived helper
classes in `ovos_plugin_manager/templates/stt.py` were deprecation-warned,
first via logging (`ff342fe`, #233, 2024-06-03) and later as a real Python
`DeprecationWarning` (`dfbac90`, #291, 2025-01-04): CI suites running
`-W error::DeprecationWarning` will fail the build on continued use.

- Migration: move off `StreamingSTT`/`StreamThread` to the current STT
  template contract.
- Lifecycle: active before `ff342fe`. Deprecated but functional from
  `ff342fe` (2024-06-03), warning strength increased in `dfbac90`
  (2025-01-04). Drop date unverified (ovos-plugin-manager `ff342fe`, #233).

### Dialect matching switched to `tag_distance`

Ad-hoc exact-prefix dialect matching (`en` matches `en-us` via
`.startswith`) was replaced with `langcodes.tag_distance` (threshold
`< 10`) across STT, TTS, wake-word, and tokenization plugin config
resolution.

- Migration: no code change needed for callers of the public
  `get_plugin_config` family. Re-verify locale resolution after upgrading
  if you pinned plugin configs to exact locale strings, since dialect
  fallback selection can differ.
- Lifecycle: behavior-only change, no removal. Landed `08ad348` (2024-10-12),
  (ovos-plugin-manager `08ad348`, #267). Later replaced again by
  `ovos_spec_tools.lang_distance` in `35919b7` (#391, 2026-05-22), same
  `< 10` threshold preserved. Requires the `ovos-spec-tools[langcodes]`
  extra or region codes silently strip (`en-US` → `en`).

### G2P deprecated, moved toward ovos-audio

`opm.g2p` (Grapheme2Phoneme, used only for MK1 mouth animation) is marked
deprecated in `ovos-plugin-manager`. The companion work moves it toward
`ovos-audio`.

- Migration: no functional removal yet in `ovos-plugin-manager`. Expect
  deprecation warnings on every access.
- Lifecycle: active before `c102889`. Deprecated but functional from
  `c102889` (2024-10-23). Drop version unverified (ovos-plugin-manager `c102889`, #277).

### `EmbeddingsDB` gains required collection methods

`create_collection`, `get_collection`, `delete_collection`,
`list_collections` became required `@abstractmethod`s on `EmbeddingsDB`.

- Migration: implement all four on your `EmbeddingsDB` subclass.
  single-collection plugins can wrap a fixed default collection name.
- Lifecycle: active before `15beb84`. No deprecation window (no deprecation window, added
  directly as abstract). Landed `15beb84` (2025-07-22), (ovos-plugin-manager `15beb84`, #333).

### Solver plugin family deprecated in favor of agent engines

The entire `templates/solvers.py` family (`QuestionSolver`, `CorpusSolver`,
`TldrSolver`, `EvidenceSolver`, `MultipleChoiceSolver`, `EntailmentSolver`)
is deprecated with a stated removal target of the next major version.

| Deprecated | Replacement |
|---|---|
| `QuestionSolver` | `ChatEngine` / `RetrievalEngine` |
| `CorpusSolver` | `DocumentIndexerEngine` / `QAIndexerEngine` |
| `TldrSolver` | `SummarizerEngine` |
| `EvidenceSolver` | `ExtractiveQAEngine` |
| `MultipleChoiceSolver` | `ReRankerEngine` |
| `EntailmentSolver` | `NaturalLanguageInferenceEngine` |

- Migration: move to the matching `templates/agents.py` engine class
  before the removal version ships.
- Lifecycle: active before `53564ce`. Deprecated but functional from
  `53564ce` (2026-01-29), `opm.solver.*` entry points still discoverable.
  removal target is the current major version plus one: not yet shipped
  as of this dossier's sweep (ovos-plugin-manager `53564ce`, #365).
  `ovos-bus-client`'s parallel `opm.py` (`neon.plugin.solver`-based chat
  class) was already removed outright in `d526e99` (#207, 2026-05-18,
  `2.0.0`): migrate to `ovos-messagebus-chat-plugin`.

### `opm.*` canonical entry-point rename

Every `PluginTypes`/`PluginConfigTypes` entry-point group string that had
carried a `# TODO rename` comment was flipped to the canonical `opm.*`
form. Old groups keep working through a `DEPRECATED_ENTRYPOINTS` alias
table (with a warning), but comparing `PluginTypes.STT.value` against the
old literal string breaks.

| Old group | New canonical group |
|---|---|
| `mycroft.plugin.stt` | `opm.stt` |
| `mycroft.plugin.tts` | `opm.tts` |
| `mycroft.plugin.wake_word` | `opm.wake_word` |
| `ovos.plugin.gui` | `opm.gui` |
| `ovos.plugin.phal` | `opm.phal` |
| `ovos.plugin.skill` | `opm.skill` |
| `ovos.plugin.microphone` | `opm.microphone` |
| `ovos.plugin.VAD` | `opm.VAD` |
| `ovos.plugin.g2p` | `opm.g2p` |
| `neon.plugin.solver` | `opm.solver.question` |
| `neon.plugin.text` / `.metadata` / `.audio` | `opm.transformer.text` / `.metadata` / `.audio` |
| `neon.plugin.lang.translate` / `.detect` | `opm.lang.translate` / `.detect` |
| `intentbox.coreference` / `.keywords` / `.segmentation` / `.tokenization` / `.postag` | `opm.coreference` / `opm.keywords` / `opm.segmentation` / `opm.tokenization` / `opm.postag` |
| `ovos.ocp.extractor` | `opm.ocp.extractor` |

- Migration: update `entry_points` in your plugin's `setup.py`/
  `pyproject.toml` to the new group at your convenience. Old groups still
  work via the alias table. Code comparing enum values as raw strings
  should compare against `PluginTypes.STT` (the enum member), not the
  literal old string.
- Lifecycle: active before `15beb84`. Deprecated but functional
  (aliased, with a warning) from `15beb84` (2025-07-22). No stated removal
  version as of the sweep, so treat as indefinitely deprecated
  (ovos-plugin-manager `15beb84`, #333). A case-sensitivity bug in the
  alias table (`ovos.plugin.VAD` mapped to lowercase `opm.vad` instead of
  `opm.VAD`) silently broke discovery of un-migrated VAD plugins for about
  eleven months, fixed in `3a7a330` (#401, 2026-06-16).

### PHAL enclosure abstraction dropped

`PHALPlugin` lost its Mark-1/Mark-2 enclosure command handling
(`register_enclosure_namespace`, `on_eyes_*`, `on_mouth_*`, `on_display`,
and so on) in one commit, then lost its lifecycle bus-event auto-wiring
(record/speak/wake/sleep) in a same-day follow-up. `PHALPlugin` is now a
bare background thread with no bus events wired by the base class at all.

- Migration: mix in `EnclosureProtocolListener` from the separate
  `ovos-ui-enclosure-protocol` package for both the enclosure commands and
  `register_core_events()`. The `EnclosureAPI` producer moved to
  `ovos-gui-api-client`.
- Lifecycle: active before `eac52a4`. No deprecation window (no deprecation window, both
  commits landed same day). Dropped `eac52a4` and `f7c613b`
  (2026-06-25), (ovos-plugin-manager `eac52a4`, `f7c613b`).

### `MediaProvider` template collapsed to `search()`

`MediaProvider` lost `is_available`, `matches`, `serves`, `search_context`,
`search_safe`, `featured_media`, and the `media`/`playback_type`/
`genre_filter` ClassVars, all on the same day the `QueryContext` dataclass
parameter was also replaced by plain `**context` kwargs.

```python
# old
class MyProvider(MediaProvider):
    def search(self, signals, context: QueryContext) -> list[Release]:
        if context.allows_playback(...):
            ...

# new
class MyProvider(MediaProvider):
    def search(self, signals, lang='en-us', **context) -> list[Release]:
        if context.get('supported_playback_types'):
            ...
```

- Migration: implement the single `search(signals, lang='en-us',
  **context)` method. Read routing/availability info from `**context`
  instead of the removed `QueryContext` helper methods.
- Lifecycle: active before `8a03351`. No deprecation window (fast in-place redesign of a
  still-fresh API: `opm.media.provider` type was only introduced days
  earlier in `83ade15`, #405). Dropped `8a03351` and `1741181`, both
  2026-06-25 (ovos-plugin-manager `8a03351`, `1741181`).

### GUI adapter plugin handler signature gains `session_id`

All `handle_show_*` template handlers, `on_namespace_activated`,
`on_namespace_deactivated`, `on_status_event`, `on_session_update`, and
`dispatch_template()` gained a new `session_id: str = "default"` parameter
inserted **before** the existing `site_id` parameter.

```python
# old
def handle_show_text(self, skill_id, data, site_id="default"): ...

# new
def handle_show_text(self, skill_id, data, session_id="default", site_id="default"): ...
```

- Migration: switch any positional `site_id` call sites to keyword
  arguments, or insert `session_id="default"` explicitly before the old
  third positional argument.
- Lifecycle: active before `34a0f13`. No deprecation window (explicit `BREAKING CHANGE:` in
  the commit body, no deprecation window). Dropped/landed `34a0f13`
  (2026-03-12), (ovos-plugin-manager `34a0f13`).

---

## If you operate a device or fleet (config changes)

### `mycroft.conf` no longer probes a mycroft-core install

`ovos_config/locations.py::find_default_config()` stopped checking for a
running mycroft-core installation as a source for the DEFAULT config
layer. Only the bundled `ovos_config/mycroft.conf` is used as DEFAULT.

- Migration: put overrides in SYSTEM/USER config layers
  (`/etc/mycroft/mycroft.conf`, `~/.config/mycroft/mycroft.conf`) instead
  of relying on a legacy mycroft-core file being picked up.
- Lifecycle: active before `0b16d46`. No deprecation window. Dropped `0.1.0` (2023-12-28),
  (ovos-config `0b16d46`, #90).

### `ovos.conf` deprecated in favor of environment variables

The separate `ovos.conf` INI file controlling `base_folder`/
`config_filename`/XDG behavior is deprecated. Those values move
exclusively to environment variables.

- Migration: replace `ovos.conf` `[core] base_folder=...` /
  `config_filename=...` / `default_config_path=...` with the env vars
  `OVOS_CONFIG_BASE_FOLDER`, `OVOS_CONFIG_FILENAME`, and
  `OVOS_DEFAULT_CONFIG` (all introduced in the same commit that
  deprecated `ovos.conf`, `76d9310`, `ovos_config/meta.py`).
- Lifecycle: active before `76d9310`. Deprecated but functional from
  `76d9310` (2024-08-16). Drop version unverified (ovos-config `76d9310`, #138).

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
- Lifecycle: active before `0a7a060`. Unverified deprecation window.
  dropped `0a7a060` (2024-11-19), (ovos-config `0a7a060`, #183). This
  mirrors `ovos-core`'s own `mycroft.api`/`DeviceApi` deprecation toward
  `ovos-backend-client` (`ee9a14cb23`, 2022-10-04) and the full removal of
  the `mycroft` compat package including Selene API support
  (`2a10fa9c1c`, #439, 2025-03-04, first stable release `1.1.0`).

### Default TTS fallback and MPRIS/lang-detect defaults changed

Three unrelated default-value changes landed in one `mycroft.conf` update:
`duck_while_listening` removed entirely (documented an unimplemented
feature), the default language-detection plugin switched to a
public-server-based one, and `mpris` under `Audio.backends.OCP` was
disabled by default.

- Migration: set `mpris: true` under `Audio.backends.OCP` (pre-`ovos-media`
  split. See the OCP→ovos-media entry above for the post-split location)
  if MPRIS is wanted. Pin the old lang-detect plugin explicitly if
  network-free detection is required.
- Lifecycle: active before `bff2d72`. No deprecation window. Dropped/changed `bff2d72`
  (2024-02-26), (ovos-config `bff2d72`, #112).

### `mimic3` no longer the default TTS fallback

The default `tts.fallback_module` value `"ovos-tts-plugin-mimic3-server"`
and its settings block were removed from the shipped `mycroft.conf`.

- Migration: set `tts.fallback_module` and the settings block explicitly
  in your own config if a fallback TTS is still wanted (mimic3 itself is
  deprecated upstream).
- Lifecycle: active before `bc9be86`. No deprecation window. Dropped `bc9be86` (2023-11-05),
  (ovos-config `bc9be86`, #81). `ovos-audio`'s matching default change
  (`tts.fallback_module` `"mimic"` → `""`) landed separately in `c47e596`
  (2024-01-26).

### `padatious_medium` dropped from default pipeline

- Migration: add `padatious_medium` back explicitly to `core.pipeline` in
  USER config if you want it (maintainers' note: "it is always wrong in
  benchmarks").
- Lifecycle: active before `b08b7b8`. No deprecation window. Dropped `b08b7b8` (2025-02-28,
  tag `1.0.2`), (ovos-config `b08b7b8`, #200).

### `ready` settings block removed

The `"ready"` start-up gating config block (14 lines) was dropped entirely
from shipped `mycroft.conf` defaults.

- Migration: consult `ovos-core`'s listener release notes for the
  replacement readiness mechanism (the skill-based "finished booting"
  signal). `ready_settings`/`ready` keys have no default anymore.
- Lifecycle: active before `94f2348`. No deprecation window. Dropped `94f2348` (2024-10-15),
  (ovos-config `94f2348`, #166). On the `ovos-core` side, the matching
  `SkillManager.is_device_ready()`/`check_services_ready()`/
  `handle_check_device_readiness()` methods (deprecated since `1.0.0`)
  were removed outright in `62024dbf98` (#690, 2025-06-10, `1.3.0`).

### Distribution config layer added, precedence order changed

`get_config_locations()` gained a `distribution=True` parameter and a new
layer, `/usr/share/<base_folder>/<config_filename>`, inserted between
DEFAULT and SYSTEM.

- Migration: config precedence is now DEFAULT < DISTRIBUTION
  (`/usr/share/...`) < SYSTEM (`/etc/...`) < web-cache (remote) < OLD_USER
  < USER. Distro packagers should install an overwrite-safe default to the
  DISTRIBUTION path.
- Lifecycle: additive, not a removal. Landed pre-`0.1.0`, (ovos-config `3781f01`, #128).

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
- Lifecycle: default-value changes, not deprecate-then-drop. `54a0844`
  (2024-06-11), `0bbec90` (2024-09-15).

### phoonnx becomes the default offline TTS in autoconfigure

Every `offline_male`/`offline_female` TTS recommendation in the
autoconfigure "recommends" registry now resolves to
`ovos-tts-plugin-phoonnx` instead of the prior per-language recommendation.

- Migration: pin the desired TTS plugin explicitly under `tts.module` in
  `mycroft.conf` if the old default is still wanted. Phoonnx requires its
  own model/voice availability per language.
- Lifecycle: n/a (registry default change, not a removal). Landed
  `2a5bc3f` (2026-06-23), (ovos-config `2a5bc3f`, #272).

### `ovos_config.locale` helpers marked for removal

`get_full_lang_code`, `get_primary_lang_code`, `get_default_lang` in
`ovos_config/locale.py` now emit `DeprecationWarning` and lost their
internal caching. Signatures are unchanged so this is warning-only so far.

- Migration: switch to `ovos_config.Configuration()["lang"]` /
  `Configuration().get("lang")` directly ahead of the eventual hard
  removal.
- Lifecycle: active before `087a112`. Deprecated but functional from
  `087a112` (2026-07-24). Drop version unverified: the decorator's target
  version string reads a placeholder that does not match the current
  major line (ovos-config `087a112`, #253).

### `native_sources` config key replaced by session-based routing

`ovos-audio`'s `native_sources` allowlist (gating playback-control bus
messages by `message.context["source"]`) was replaced by
`@require_default_session()`, gating on
`message.context["session"]["session_id"] == "default"` instead.

- Migration: remove `native_sources` from config/constructor calls. Ensure
  playback-control messages either omit `context.session` (defaults to
  `"default"`) or explicitly set `session_id: "default"`.
- Lifecycle: active before `01499ee`. Unverified deprecation window (the
  gating decorator was introduced in `c5d95a4`, 2024-06-06, then replaced
  outright). Dropped `01499ee` (2025-03-06), (ovos-audio `01499ee`, #121).
  `ovos-media` landed the matching change with `require_default_session()`
  plus a new `media.validate_source` (bool, default `True`) config key in
  `4601792` (#58, 2026-06-26): set `media.validate_source: false` on a
  central `ovos-media` instance that must act on non-default/remote
  HiveMind sessions.

---

## If you consume the message bus remotely (HiveMind and other clients)

This section is for anyone connecting to the bus as a separate process:
HiveMind satellites, custom dashboards, external automation, or any code
that parses raw wire messages instead of going through a skill.

### HiveMind agent protocol and messagebus-solver removed from ovos-bus-client

`ovos_bus_client/hpm.py` (`OVOSAgentProtocol`/`OVOSProtocol`) and
`ovos_bus_client/opm.py` (the `neon.plugin.solver`-based chat class) were
deleted, along with the `hivemind.agent.protocol` entry point.

- Migration: `from ovos_bus_client.hpm import OVOSAgentProtocol` → install
  `hivemind-ovos-agent-plugin` and import from there (the entry-point
  *name* is preserved, so HiveMind-core configs need no change, only the
  dependency install). `ovos_bus_client.opm` (QuestionSolver-based chat) →
  `ovos-messagebus-chat-plugin` (implements `ChatEngine`, uses
  `SessionManager` for multi-turn state). See
  JarbasHiveMind/HiveMind-core#85.
- Lifecycle: active before `d526e99`. Unverified deprecation window.
  dropped `2.0.0` (ovos-bus-client `d526e99`, #207, 2026-05-18).

### GUI wire protocol moved to template-based `GUIInterface`

The free-form page/`GUIWidgets` API is replaced by a template wire
protocol: `gui.value.set` + `gui.page.show` (OVOS-GUI-1 §3-4), with a new
`PageTemplates` enum and `show_text`/`show_image`/`show_face` helpers. The
old page/remove primitives became private. `EnclosureAPI` is deprecated in
favor of `GUIInterface` for visual output.

- Migration: declare a `PageTemplates.*` template and call the matching
  `show_*` helper instead of pushing a raw QML/page path. Move visual
  output off `EnclosureAPI` onto `GUIInterface`. Both `GUIInterface` and
  `EnclosureAPI` are themselves deprecated in favor of
  `ovos-gui-api-client`.
- Lifecycle: active before `0d145d3`. Deprecated but functional through a
  series of `refactor!:` commits from `59ee94e` (2026-03-12) through
  `0d145d3` (2026-06-25). Classic API becomes private at `0d145d3`
  (ovos-bus-client `0d145d3`).

### SESSION-1 spec adoption changes session wire semantics

`SessionManager` was rebuilt on the `ovos-spec-tools` session registry
(`b54269c`, 2026-06-29). Three concrete wire/behavior changes to know:

- `get()` no longer reserves the default session id as owner-only: it
  folds like any other session (SESSION-1 §4).
- Session expiry (`Session.expired`/`touch_time`/`expiration_seconds`,
  `prune_sessions`) is not part of SESSION-1 and is deprecation-warned.
  Stop depending on session TTL/pruning behavior.
- `SessionManager` now enforces one live `Session` object per id
  (singleton, `7a2e39f`, #249). Code holding a stale `Session` reference
  expecting it to stay independent from the manager's canonical instance
  will observe shared-state changes it did not make.
- An empty list on a list-valued override field (`pipeline`,
  `blacklisted_skills`, `blacklisted_intents`) is now **omitted** from
  `serialize()` output instead of round-tripped as `[]` (`47b0e4a`,
  2026-07-09). Absence means "use the deployment default." Any bus
  consumer indexing the raw wire dict (`session["pipeline"]`) instead of
  going through `Session.deserialize()` must treat a missing key as
  "deployment default," not as an error.

- Migration: read sessions through `Session.deserialize()`/the `Session`
  class, not by indexing the raw wire dict. Stop relying on
  `prune_sessions`/session TTL expiry. Treat the default session id like
  any other session id.
- Lifecycle: active before `b54269c`. The list-omission wire change is
  deprecated-in-spirit only (no prior wire shape to preserve, this is a
  new spec adoption) landing directly at `47b0e4a` (2026-07-09). Session
  expiry deprecated but functional from `b54269c` (2026-06-29), drop
  version unverified.

### Legacy `mycroft.*`/`recognizer_loop:*` topic bridge removed

See [The bus-client legacy-topic dual-emit and its removal](#the-bus-client-legacy-topic-dual-emit-and-its-removal)
above for the full timeline. The short version for remote clients: as of
`ovos-bus-client` `f1a481d` (2026-08-01), `MessageBusClient` speaks
OVOS-MSG-1 (`ovos.*`) topics only, with no bridge back to legacy topic
spellings. A HiveMind satellite still emitting or expecting legacy topics
silently stops being received.

### Per-service legacy topic migrations (spec-bus adoption, 2026-06)

Every listener/core service in the org migrated its own emit/listen sites
to `ovos_spec_tools.SpecMessage` constants around the same time, mostly
gated behind a `legacy_namespace` config key (default `True`, so
out-of-the-box wire behavior is initially unchanged):

| Legacy topic | Spec topic | Landed in |
|---|---|---|
| `recognizer_loop:utterance` | `ovos.utterance.handle` (`SpecMessage.UTTERANCE`) | ovos-core `1672e35ed0` (#772/#775) · ovos-dinkum-listener `d9dc04e` (#232) · ovos-simple-listener `b8326fa` (#26) · mycroft-classic-listener `4458a3f` (#23, `1.0.0`) |
| `mycroft.awoken` | `SpecMessage.LISTENER_AWOKEN` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `recognizer_loop:record_begin` / `record_end` | `SpecMessage.LISTENER_RECORD_STARTED` / `_ENDED` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `mycroft.mic.listen` | `SpecMessage.MIC_LISTEN` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `recognizer_loop:audio_output_start` / `_end` | `SpecMessage.AUDIO_OUTPUT_STARTED` / `_ENDED` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `recognizer_loop:sleep` | `SpecMessage.LISTENER_SLEEP` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `mycroft.stop`, per-skill stop pings, `complete_intent_failure` | `ovos.stop`, `ovos.stop.ping`, `ovos.intent.unmatched` | ovos-core `f4c00d90b2` (2026-06-05) |
| `stop.openvoiceos.stop.response` | removed, not replaced | ovos-core `2b05201705` (2026-06-29): `StopService` no longer registers itself as a skill, do not count it as a participating skill in custom global-stop aggregation |

- Migration: for any deployment that explicitly sets
  `legacy_namespace: false`, subscribe to the `ovos.*` spec topics instead
  of the legacy ones. Default deployments are unaffected until that flag's
  default flips (not yet flipped as of this dossier's sweep). Prefer
  `ovos_spec_tools.SpecMessage.*` constants over hardcoded topic strings
  going forward, since their literal values are not always the same as
  the legacy strings they replace.
- Lifecycle: active (legacy-only) before mid-2026. Deprecated but
  functional (dual-emit or `legacy_namespace`-gated) from mid-2026
  onward. Hard drop only confirmed for `ovos-bus-client`'s own bridge
  (`f1a481d`, 2026-08-01). `legacy_namespace` gating in `ovos-core`
  itself (`f4c00d90b2`/`f9862a760e`, "gate bus topics by
  legacy_namespace") lives only on unmerged feature branches as of this
  sweep, not on `dev`: the default has not flipped because the flag has
  not shipped to a stable release yet.

### `mycroft-bus-client` package retirement (package-level, not wire-level)

Every repo in the org switched its dependency and imports from the
upstream `mycroft-bus-client` package to `ovos-bus-client`. This is a
Python import change, not a wire change: listed here because it is the
package-level ancestor of the topic-level migration above.

- Migration: `pip install ovos-bus-client`. `from mycroft_bus_client
  import Message` → `from ovos_bus_client.message import Message` (or
  `from ovos_bus_client import MessageBusClient`).
- Lifecycle: active before 2023-04. Dropped (isinstance compat kept
  briefly, `04def5d`) starting `9396c71` (2023-04-05, ovos-bus-client's
  own extraction). The ecosystem-wide dependency swap landed at
  `b1a9d39e16` (2023-04-11) in `ovos-core`, and matching one-line swaps in
  `ovos-audio` (`426a48b`), `ovos-media` (`426a48b`), and
  `ovos-messagebus` (`a1bc1c1`), all within the same week.

---

## Coming next

The following work is visible on unmerged branches only and is **not
released**. It is included so you know it is coming, not because it is
safe to build against yet.

- **AssistantConfig** (`ovos-config`, branches `feat/assistant_config`,
  `pr194`): introduces a new `runtime.conf` config layer for
  OVOS-internal runtime writes, so plugins/components stop corrupting the
  user's `mycroft.conf`. Deprecates `RemoteConfig`. Explicit back-compat
  commits on the branch promise `Configuration().remote` and
  `load_config_stack(...)` keep working once this lands. Do not target
  `AssistantConfig` yet. Watch the `ovos-config` release notes.
- **OVOS-PIPELINE-1 / STOP-1 / INTENT-4 conformance** (`ovos-core`,
  active on `dev` through at least 2026-08-01): the orchestrator is
  taking over emitting `ovos.intent.handler.{start,complete,error}` around
  every skill dispatch, and `ovos.intent.matched` before every dispatch.
  Still landing incrementally under `legacy_namespace` gating. Not yet in
  a numbered stable release.
- Unmerged `ovos-workshop` branches `feat/deprecate-ocp-skills`,
  `feat/remove-skill-homescreens`, `feat/gameskill-and-ocp-deprecation`:
  OCP-skill-base-class and skill-homescreen removal has not landed as of
  this page's sources. Do not treat as shipped.

---

## Verification gaps

The following lifecycle phases could not be confirmed against the commit
history this page is built from. Treat the corresponding table cells as
"unverified" and re-check against the named repository's release history
before relying on them:

- **ovos-utils**: whether `ovos_utils.gui.GUITracker` has a real successor
  anywhere. A search of `ovos-gui`'s current history found no
  `GUITracker`/`GUIPlaybackStatus` symbol anywhere in that repo, so this
  still reads as "no successor," but a positive absence is weaker proof
  than a located replacement. The exact mycroft-core commit that performed
  the original `mycroft.* → ovos_*` rename predates `ovos-utils`'s own
  history: it requires the `mycroft-core` repository's own history, which
  is not cloned in this workspace.
- **ovos-config**: exact key path that STT-embedded language preferences
  moved to in `ede6243`. The commit's own `autoconfigure` CLI command
  writes the standardized language tag to the top-level `lang` config key
  (config root, not nested under `stt`), which is consistent with the PR's
  "split prefs from stt into base config" description, but no dedicated
  migration diff moving an existing nested key was found to confirm this
  covers every prior STT-embedded language setting.
- **ovos-media**: full symbol-level API diff of the `d249e89` `player.py`
  rewrite beyond what the `f1d152c` regression fix incidentally revealed.
  The exact point at which `ovos-media` became production-recommended over
  `ovos-audio`'s classic `AudioService`: that call is a project
  announcement/roadmap decision, not a single commit, so it requires the
  release notes and blog history rather than `git log`.
- **ovos-audio**: the exact mycroft-core commit/version that `047a0a1`
  extracted `ovos_audio` from. `047a0a1` is the first substantive commit
  in `ovos-audio`'s own history (no shared ancestor commit exists in this
  repo), so pinning the mycroft-core side requires the `mycroft-core`
  repository's own history, which is not cloned in this workspace.
- **ovos-bus-client**: no `mycroft.conf` semantics change was found to
  originate in this repo (it does not own config parsing). No explicit
  "MycroftSkill → OVOSSkill" commit exists in this repo either (that
  rename lives in `ovos-core`/`ovos-workshop`).
