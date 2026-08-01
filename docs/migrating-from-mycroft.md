# Migrating from Mycroft

!!! abstract "In a nutshell"
    OVOS grew out of the original Mycroft AI project. A lot of the vocabulary is unchanged on
    purpose: "skills", "intents", "dialog files", even the wake word "Hey Mycroft". This lets
    skills and habits carry over. The underlying Python API was cleaned up along the way. Class
    names moved, one central cloud account went away entirely, and a couple of decorators
    merged into one. This page is a one-stop diff for anyone arriving with old
    `mycroft-core` knowledge (a skill, a config file, a habit) who wants to know exactly what
    changed and why. New to the words here? See the [Glossary](glossary.md).

This page is for skill authors and integrators. If you just used a Mycroft device and
want to know what daily use looks like on OVOS, read
[Coming from Mycroft](coming-from-mycroft.md) instead.

## The short version

OVOS is a **backendless**, community-maintained continuation of the ideas behind Mycroft AI.
There is no cloud account, no pairing step, and no `home.mycroft.ai`. Everything that used to
require the Mycroft backend now runs locally or through swappable, self-hosted plugins. The
skill-writing model (intent files, dialog files, `locale/` folders) is the same model you already
know. Only a handful of import paths and class/decorator names changed.

## Before / after: writing a skill

=== "mycroft-core (historical)"

    ```python
    from mycroft import MycroftSkill, intent_file_handler

    class HelloSkill(MycroftSkill):
        def __init__(self):
            MycroftSkill.__init__(self)

        @intent_file_handler("hello.intent")
        def handle_hello(self, message):
            self.speak_dialog("hello")

    def create_skill():
        return HelloSkill()
    ```

=== "OVOS (current)"

    ```python
    from ovos_workshop.skills import OVOSSkill
    from ovos_workshop.decorators import intent_handler

    class HelloSkill(OVOSSkill):

        @intent_handler("hello.intent")
        def handle_hello(self, message):
            self.speak_dialog("hello")
    ```

What changed, line by line:

- `from mycroft import MycroftSkill` → `from ovos_workshop.skills import OVOSSkill`. The
  `mycroft` package and its `MycroftSkill` class do not exist in the current OVOS stack.
  `OVOSSkill` (in `ovos-workshop`) is the base class every skill subclasses today.
- No `__init__` / `create_skill()` boilerplate is required. A skill is loaded from a Python
  package that declares itself through an `opm.skill` entry point (see
  [Your First Skill](first-skill.md)). OVOS instantiates the class directly.
- `@intent_file_handler(...)` → `@intent_handler(...)`. mycroft-core kept Padatious `.intent`
  files and Adapt intents behind two separate decorators. OVOS merged them into a single
  `@intent_handler` that accepts either an `.intent` filename or an `IntentBuilder`. See
  [Decorators](decorators.md#coming-from-mycroft-core) for the full note.
- `self.speak_dialog(...)` is unchanged. Dialog files and the multilingual `locale/` layout work
  exactly as before (see [Statements](statements.md)).

## Concept map

| mycroft-core concept | OVOS today | Notes |
|---|---|---|
| `MycroftSkill` | [`OVOSSkill`](ovos-skill.md) | Base class every skill subclasses. |
| `@intent_file_handler` | [`@intent_handler`](decorators.md) | Now handles both Padatious `.intent` files and Adapt `IntentBuilder`s. |
| `self.translate()` / `translate_list()` / `translate_namedvalue()` / `translate_template()` | `self.resources.render_dialog()` / `load_list_file()` / `load_named_value_file()` / `load_template_file()` | The old `translate*` helpers were **removed**. See [Statements → Using translatable resources](statements.md#using-translatable-resources). |
| `home.mycroft.ai` (pairing, cloud STT/TTS, remote settings) | *Nothing, removed* | OVOS is [**backendless**](deprecated-repos.md#backend-services-removed-architecture-5). There is no account, no pairing, and no central server. STT/TTS/settings all run through local or self-hosted plugins instead. |
| Mycroft Skills Manager (`msm`, `ovos_skill_manager`) | pip / `opm.skill` entry points | Skills are ordinary Python packages installed with `pip`. Discovery goes through [OPM](plugin-manager.md), not a separate skill manager. |
| `GUITracker` | `can_display()` / `is_gui_installed()` / `is_gui_connected(bus)` in `ovos_utils.gui` | See [Developer FAQ](skill-dev-faq.md). GUI-heavy skills should also read [Mark 1](mark1.md): `self.enclosure` and `self.gui` are being removed from the `OVOSSkill` base class. |
| Mycroft backend skills (`skill-ovos-setup`, `ovos-stt-plugin-selene`, …) | Removed or replaced | See the [Deprecated & Archived Repositories](deprecated-repos.md) list for the full mapping. |
| `~/.config/mycroft/` config/settings folder | Same path, kept for compatibility | `mycroft` is still the **default** base folder name for config and settings, on purpose. See [Skill Settings](skill-settings.md#storage-location). It can be renamed via `ovos.conf` / `OVOS_CONFIG_BASE_FOLDER` if you want a fresh `OpenVoiceOS` folder instead. |
| "Hey Mycroft" wake word | Unchanged | Still the default wake word. Nothing to migrate here. |

## What you don't have to change

- **Intent files, dialog files, and the `locale/` folder layout** are the same format and the
  same lookup rules. A skill's resources port over unmodified.
- **`self.speak()` / `self.speak_dialog()` / `self.get_response()`** and the general shape of an
  intent handler are unchanged.
- **The wake word and general voice interaction model** ("Hey Mycroft, do the thing") are
  unchanged.

## What you must change

- Replace `from mycroft import MycroftSkill` with `from ovos_workshop.skills import OVOSSkill`
  (or one of its subclasses, such as `FallbackSkill` or `OVOSCommonPlaybackSkill`. See
  [Skill Classes](skill-classes.md)). There is no `CommonQuerySkill` base class. A plain
  `OVOSSkill` joins CommonQuery by decorating a method with
  [`@common_query()`](skill-classes.md#commonquery-common_query-on-ovosskill).
- Replace `@intent_file_handler` with `@intent_handler`.
- Drop any code that depends on `home.mycroft.ai` (pairing checks, remote settings sync, cloud
  STT/TTS calls). There is nothing to pair with. Local plugins provide the equivalent
  functionality instead (see [STT Plugins](stt-plugins.md), [TTS Plugins](tts-plugins.md),
  [Skill Settings](skill-settings.md)).
- Replace `self.translate*()` calls with the corresponding `self.resources.*` loader (see the
  concept map above).
- If your skill shipped a `setup.py`/`msm` metadata file for the old Skills Manager, replace it
  with a `pyproject.toml` and an `opm.skill` entry point (see [Your First Skill](first-skill.md)
  and [skill.json](skill-json.md)).

## Where to go from here

- [Deprecated & Archived Repositories](deprecated-repos.md): full list of retired
  mycroft-core-era repositories and their current replacements.
- [Your First Skill](first-skill.md): a from-scratch walkthrough using today's API.
- [Decorators](decorators.md): every decorator available today, including the note on
  `@intent_file_handler`.
- [Glossary](glossary.md): unfamiliar terms, including [`home.mycroft.ai`](glossary.md).

---
**Read next:** [Skill Structure](skill-structure.md) · [Writing Version-Compatible Skills and Plugins](version-compat-guide.md)
**Related:** [Skill Design Best Practices](skill-best-practices.md) · [Voice User Interface Design Guidelines](skill-design-guidelines.md) · [Intent Design](intents.md) · [Coming from Mycroft](coming-from-mycroft.md)
