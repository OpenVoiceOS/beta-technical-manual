# Skill Metadata File

!!! abstract "In a nutshell"
    `skill.json` is a small "info card" for your skill: its name, a short description, an icon, and a few example phrases. OVOS and skill stores read this card to install your skill and show it in menus and on screens, much like the listing page for an app in an app store. It does not change what the skill does. It just describes it. For the saved-preferences side of things, see [Skill Settings](skill-settings.md). For term definitions, see the [Glossary](glossary.md).

The `skill.json` file is an optional way to describe your Open Voice OS (OVOS) skill. It provides metadata used for installation, discovery, and display in GUIs or app stores.

## Purpose

- Helps OVOS identify and install your skill.


- Enhances GUI experiences with visuals and usage examples.


- Lays the foundation for future help dialogs and skill documentation features.

---

## Usage Guide

1. Create a `skill.json` file inside your skill's `locale/<language-code>` folder.


2. Fill in the metadata fields as needed (see below).


3. If your skill supports multiple languages, include a separate `skill.json` in each corresponding `locale` subfolder.

> **Warning:** Avoid using old `skill.json` formats found in some legacy skills where the file exists at the root level. These are deprecated.

---

## Example `skill.json`

```json
{
  "skill_id": "skill-xxx.exampleauthor",
  "source": "https://github.com/ExampleAuthor/skill-xxx",
  "package_name": "ovos-skill-xxx",
  "pip_spec": "git+https://github.com/ExampleAuthor/skill-xxx@main",
  "license": "Apache-2.0",
  "author": "ExampleAuthor",
  "extra_plugins": {
    "core": ["ovos-utterance-transformer-xxx"],
    "PHAL": ["ovos-PHAL-xxx"],
    "listener": ["ovos-audio-transformer-xxx", "ovos-ww-plugin-xxx", "ovos-vad-plugin-xxx", "ovos-stt-plugin-xxx"],
    "audio": ["ovos-dialog-transformer-xxx", "ovos-tts-transformer-xxx", "ovos-tts-plugin-xxx"],
    "media": ["ovos-ocp-xxx", "ovos-media-xxx"],
    "gui": ["ovos-gui-extension-xxx"]
  },
  "icon": "http://example.com/icon.svg",
  "images": ["http://example.com/logo.png", "http://example.com/screenshot.png"],
  "name": "My Skill",
  "description": "Does awesome skill stuff!",
  "examples": [
    "do the thing",
    "say this to use the skill"
  ],
  "tags": ["productivity", "entertainment", "aliens"]
}
```

---

## Field Reference

None of these fields are enforced by `ovos-workshop` at runtime. Only `examples` is actually read (it is registered with the homescreen so it can show sample phrases for the skill). Everything else is a convention followed by skill-store and CI tooling.

Ecosystem lint tooling (the `check_skill.py` compliance check used in CI) treats `skill_id`, `name`, `description`, `examples`, and `tags` as the fields it expects to be present. Treat the rest as recommended, not mandatory.

| Field            | Type     | Recommended | Description |
|------------------|----------|----------|-------------|
| `skill_id`       | string   | Yes    | Unique ID, typically `repo.author` style (lowercase). |
| `source`         | string   | Optional | Git URL to install from source. |
| `package_name`   | string   | Optional | Python package name (e.g., for PyPI installs). |
| `pip_spec`       | string   | Optional | [PEP 508](https://peps.python.org/pep-0508/) install spec. |
| `license`        | string   | Optional | License ID (see [SPDX list](https://spdx.org/licenses/)). |
| `author`         | string   | Optional | Display name of the skill author. |
| `extra_plugins`  | object   | Optional | Dependencies to be installed in other OVOS services (not this skill). |
| `icon`           | string   | Optional | URL to a skill icon (SVG recommended). |
| `images`         | list     | Optional | Screenshots or promotional images. |
| `name`           | string   | Yes    | User-facing skill name (some skills use `title` instead or as well). |
| `description`    | string   | Yes    | Short, one-line summary of the skill. |
| `examples`       | list     | Yes    | Example utterances your skill handles: the only field `ovos-workshop` actually reads, to register with the homescreen. |
| `tags`           | list     | Yes    | Keywords for searchability. |

!!! note
    In practice, real-world `skill.json` files vary quite a bit. Some use
    `title` instead of `name`, some carry a `category` string (e.g. `"Daily"`,
    `"Information"`, `"Configuration"`) that the skill store uses to group
    listings, and older, auto-generated `skill.json` files
    (from the legacy skills-manager tooling) carry many more fields
    (`version`, `url`, `requirements`, `platforms`, and more). Stick to the
    fields above for new skills. Anything extra is ignored by `ovos-workshop`.

---

## Language Support

To support multiple languages, place a `skill.json` file in each corresponding `locale/<lang>` folder. Fields like `name`, `description`, `examples`, and `tags` can be translated for that locale.

---

## Installation Behavior

`pip_spec`, `package_name`, and `source` are hints for skill-installer /
skill-store tooling about where to fetch a skill from. `ovos-workshop`
itself does not install skills or read these fields. Provide at least one
so external installers have somewhere to pull the skill from.

---

## Packaging: the `opm.skill` Entry Point

`skill.json` describes a skill for discovery and display, but it is not how OVOS *loads* an installed skill. A pip-installed skill is found through the `opm.skill` entry-point group (singular) declared in its `pyproject.toml` / `setup.py`:

```toml
[project.entry-points."opm.skill"]
"skill-xxx.exampleauthor" = "skill_xxx:MySkill"
```

The entry-point name is the `skill_id` and the value points at the skill class. `find_skill_plugins()` in `ovos-plugin-manager` enumerates this group to load skills.

---

## Tips & Caveats

- This metadata format is a **standard** part of the OVOS skill discovery process and continues to evolve to support new ecosystem features.


- `extra_plugins` allows for declaring companion plugins your skill may require, but that aren't direct Python dependencies.


- The [Skill store](https://openvoiceos.github.io/OVOS-skills-store) and GUI tools like `ovos-shell` use `icon`, `images`, `examples`, and `description` to present the skill visually.

---

## Sharing your skill

Once your skill works, publishing it is the same as publishing any Python package:

1. **Push it to a GitHub repository** under your own account (or the `OpenVoiceOS` org if you're contributing an official skill). The `source` field in `skill.json` should point at it.
2. **Optionally publish it to PyPI** so it can be installed with a plain `pip install`, and set `package_name` in `skill.json` to that PyPI name. Skills without a PyPI release are still installable directly from git via `pip_spec` (see the [PEP 508](https://peps.python.org/pep-0508/) spec syntax used there).
3. **List it on the [OVOS Skill store](https://openvoiceos.github.io/OVOS-skills-store)**. Two submission paths, both feeding the same catalog: fill in the guided **Submit Skill** form on the store site, or open a
   [skill-submission issue](https://github.com/OpenVoiceOS/OVOS-skills-store/issues/new?template=skill_submission.yml)
   on the [OVOS-skills-store](https://github.com/OpenVoiceOS/OVOS-skills-store) repo — the
   issue form's fields mirror `skill.json` and generate the store's catalog entry on merge.
   The store reads the `skill.json` fields above (`name`, `description`, `examples`, `tags`, `icon`, `images`) to build the listing card, and `source`/`pip_spec`/`package_name` to know how to install it.

!!! tip
    A complete, accurate `skill.json` is what makes the difference between a bare repository link
    and a nicely presented store entry. See the [Field Reference](#field-reference) above.

## Maintaining a published skill

Once a skill is out and installed by other people, changing it is a compatibility question
as much as a code change.

### Bumping the version

A skill's version lives in `pyproject.toml` (`version = "0.0.1"` in the [first-skill
tutorial](first-skill.md#step-5-make-it-installable)), the same as any other Python package.
The manual does not document an OVOS-specific version scheme for skills, so follow the
general rule: [semver](https://semver.org). A backward-compatible fix or addition bumps the
patch or minor number. A change that breaks how the skill is used, its settings, or its
intents bumps the major number.

### New release vs. new `skill_id`

`skill_id` is derived from the `opm.skill` entry-point key, in `<skill-name>.<author>` form
(see [Packaging: the `opm.skill` Entry Point](#packaging-the-opmskill-entry-point) and
[first-skill: Step 5](first-skill.md#step-5-make-it-installable)). Because installers, the
skill store, and `SkillManager` all key off `skill_id`, treat it the same way you would treat
a package name:

- A change to intents, dialog, settings, or behavior that stays compatible, or one that
  intentionally breaks compatibility, is still **the same skill**: release a new version
  under the same `skill_id`.
- Renaming the skill in a way that changes the entry-point key is a **breaking rename**. It
  produces a new `skill_id`, which installers and `SkillManager` treat as an entirely
  different skill: old installs won't pick it up automatically, and anyone depending on the
  old `skill_id` (other skills, automation, documentation) needs to switch over. Only do this
  deliberately, and update `skill.json`'s `skill_id` field and the entry-point key together
  so they stay in sync.

### Keeping `pip_spec` floors current

`dependencies` in `pyproject.toml` (for example `ovos-workshop>=0.0.1` in the [first-skill
tutorial](first-skill.md#step-5-make-it-installable)) pin a floor, not an exact version. If a
release relies on behavior only present from a newer `ovos-workshop` (or another dependency)
than what's currently declared, raise that floor in the same release. An outdated floor lets
an installer set up a combination the skill was never tested against, which shows up later as
a hard-to-diagnose bug report rather than a clean install failure. The same applies to the
`pip_spec` field in `skill.json` itself if it carries a version constraint: keep it aligned
with what `pyproject.toml` actually requires. Run the skill's tests (see [Testing Your
Skill](testing-your-skill.md)) against the raised floor before releasing, not just against
whatever happens to already be installed in your dev environment.

---
**Read next:** [ovos-workshop Documentation](workshop-overview.md)
**Related:** [Customization](customization.md) · [Skill Structure](skill-structure.md) · [settingsmeta.json](skill-settings-meta.md) · [For Skill Maintainers](updating-skills.md)
