# Customization

!!! abstract "In a nutshell"
    You don't have to be a programmer to make a skill behave the way you like. This page shows how to change what an existing skill says, to give your assistant its own personality, or to add a language it doesn't yet support, all by dropping a few text files into a folder on your device. The original skill stays untouched. Your changes simply override it. The later sections are a reference for developers. For more on those text files, see [Resource Files](resource-files.md). For term definitions, see the [Glossary](glossary.md).

## Resource Files

Resource files are essential components of OVOS skills. They contain data such as dialogs, intents, vocabularies, regular expressions, and templates.

These files define how a skill interacts with the user and responds to queries.

> **RECAP**: the skill contains a `locale` folder with subfolders for each lang, for example `en-us`. Learn more in the [skill structure docs](skill-structure.md).


### The user resources directory

Both procedures below write into the same place: a per-skill override directory under your
XDG data directory.

```
$XDG_DATA_HOME/mycroft/resources/<skill-id>/
```

`XDG_DATA_HOME` is usually `~/.local/share` on Linux, so for the skill ID
`ovos-skill-date-time.openvoiceos` the directory is
`~/.local/share/mycroft/resources/ovos-skill-date-time.openvoiceos/`.

Inside it, mirror the skill's own directory layout. Create the directory with `mkdir -p` if it
does not exist. You do not need to fork a skill to change what it says or what languages it
speaks.

---

### Customizing Dialogs

`.dialog` user overrides are honored since `ovos-workshop` `9.5.3a1` — the dialog renderer
checks the user override directory first, then falls back to the skill's own `locale/`
directory. The override only takes effect if that directory already exists when the skill
loads; create it before starting/restarting the skill, not after.

Replace one dialog file of an installed [skill](skill-design-guidelines.md) with your own
wording. This example replaces `time.current.dialog` in `ovos-skill-date-time.openvoiceos`.

1. Find the skill ID and the dialog file you want to replace. The file lives in the skill's
   `locale/en-us/dialog` directory.
2. Write a replacement file with the same name, `time.current.dialog`. Change, add, or remove
   lines as you like.
3. Copy it into the matching path under the user resources directory:

    ```bash
    mkdir -p ~/.local/share/mycroft/resources/ovos-skill-date-time.openvoiceos/locale/en-us/dialog
    cp time.current.dialog \
      ~/.local/share/mycroft/resources/ovos-skill-date-time.openvoiceos/locale/en-us/dialog/
    ```

4. Restart OpenVoiceOS so the skill reloads its resources, then ask for the current time.

Once `.dialog` overrides are honored (see the warning above), you will hear your own wording
instead of the skill's built-in text. For the resource types where overrides already work, a
non-effective override usually means the path, the file name, the extension, or the language
folder casing doesn't match exactly.

!!! warning "Your file REPLACES the original, it does not merge with it"
    The user-specific file is used instead of the skill's own `time.current.dialog`, line for
    line. It is not appended to or merged with the original. If the skill is later updated
    upstream and new lines are added to its `time.current.dialog`, your override keeps
    shadowing the whole file, and you will not see those new lines until you copy them into
    your override yourself.

---

### Local Language support

Add a language to a skill that does not ship one yet, without waiting for an upstream release.
This example adds Spanish (`es-es`) to the same skill.

1. Find the skill ID and the language code you want to add.
2. Create the language folder under the user resources directory:

    ```bash
    mkdir -p ~/.local/share/mycroft/resources/ovos-skill-date-time.openvoiceos/locale/es-es
    ```

3. Copy the resource files from an existing language folder, such as `en-us`, into it. This
   covers vocabularies and regex files, depending on what the skill uses (translated
   `.dialog` files placed here are ignored for now — see the warning above). Keep the
   same subdirectory structure.
4. Translate the copied files.
5. Restart OpenVoiceOS, then test the skill in the new language.

If a resource is missing from your new language folder, the skill falls back to its own
language handling. The Language Fallback section below covers the order it uses.

!!! tip "Send it upstream"
    A local language folder only helps you. Opening a pull request against the skill adds the
    language for everyone, and means you stop re-applying it after each update.

---

## Developer: Resource File Reference

The end-user steps above drop files into the same `locale/<lang-code>/` layout described
below. This section is the developer-facing reference for that layout: which resource types
exist, how they are looked up, and how to load them from code.

Skills load localized resources from a structured directory layout. Resources are loaded automatically at startup for every language in `native_langs` (`core_lang` + `secondary_langs`).

### Recommended Layout

```text
my-skill/
├── locale/
│   ├── en-US/
│   │   ├── my.dialog        # spoken responses
│   │   ├── my.intent        # padatious intent examples
│   │   ├── my.voc           # adapt vocabulary keywords
│   │   ├── my.entity        # adapt entity examples
│   │   ├── my.rx            # regex patterns for adapt
│   │   └── skill.json       # skill metadata (examples for homescreen)
│   └── es-ES/
│       ├── my.dialog
│       └── my.intent
└── gui/
    └── my_page.qml

```

Legacy skills may use separate `dialog/`, `vocab/`, `regex/` subdirectories. These are still supported.

### Resource Types

| Extension | Type | Description |
|---|---|---|
| `.dialog` | Dialog | Mustache-templated spoken responses (one per line, random selection) |
| `.intent` | Intent | [Padatious](padatious-pipeline.md) training examples |
| `.voc` | Vocabulary | [Adapt](adapt-pipeline.md) keyword definitions (one keyword per line, first is canonical) |
| `.entity` | Entity | Adapt entity examples |
| `.rx` | Regex | Adapt regex patterns |
| `.list` | List | A flat list resource |
| `.word` | Word | A single word |
| `skill.json` | Metadata | `{"examples": ["...", "..."]}` for homescreen example utterances |

### Dialog Files

Each line in a `.dialog` file is a possible response. One line is chosen randomly when `speak_dialog` is called:

```text

# my.dialog
Hello there!
Hi! How are you?
Greetings, {name}!

```

Mustache template variables are filled from the `data` dict:

```python
self.speak_dialog("my", data={"name": "Alice"})

```

### Language [Fallback](fallback-pipeline.md)

When a resource is not found for the exact `lang`, the skill falls back to dialects of the same language. For example, if `en-AU` is requested but only `en-US` resources exist, `en-US` is used.

### Loading Resources Manually

```python

# Get SkillResources for current lang
resources = self.resources                         # current self.lang
resources = self.load_lang(self.res_dir, "es-ES")  # specific lang

# Find a specific file
path = self.find_resource("my.dialog", "dialog")
path = self.find_resource("hello.mp3", "snd")

# Render a dialog (returns string, does not speak)
text = self.resources.render_dialog("my.dialog", data={"key": "value"})

# Check if a vocab word matches
matches = self.voc_match("hello there", "hello")  # True

```

### `skill.json` Metadata

Optional file for homescreen integration. Placed at `locale/<lang>/skill.json`:

```json
{
  "name": "My Skill",
  "description": "Does something useful",
  "examples": [
    "what is the weather",
    "tell me the weather in Paris"
  ]
}

```

These examples are emitted to the homescreen as `homescreen.register.examples` on skill startup.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Skill Metadata File](skill-json.md)
**Related:** [SSMLBuilder](ssml.md) · [Skill Settings](skill-settings.md) · [Resource Files](resource-files.md) · [Customizing Language Resources](lang-customization.md)
