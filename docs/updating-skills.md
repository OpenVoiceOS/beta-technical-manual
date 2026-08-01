# Updating Skills From Older OVOS

## In a nutshell

This page is for skill maintainers moving a skill forward from an older
OVOS install. Entries are in date order: start at the version you are
currently running and read forward to your target version. For the
Big-ticket migrations (the changes with the widest blast radius, including
the `ovos-workshop` 4.0.0 → 7.0.0 release train), see
[Updating from Older OVOS](updating-from-older-ovos.md#big-ticket-migrations).

## If you maintain skills

### Skill-settings file-store rewritten

Skill settings moved to `json_database`-backed XDG-default storage,
replacing the old ad-hoc file kludge, with a one-time auto-migration.

- Migration: rely on the `self.settings` API. Do not read/write the old
  non-XDG settings file path directly.
- Lifecycle: active before `3299173`. Unverified deprecation window (only
  a one-time auto-migration is recorded, not a hard cutover date).
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

---

**Read next:** [Version-Compatible Skills & Plugins](version-compat-guide.md) · [Upcoming Changes](upcoming-changes.md)
**Related:** [Updating from Older OVOS](updating-from-older-ovos.md) · [Migrating From Mycroft](migrating-from-mycroft.md)
