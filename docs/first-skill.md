# Your First Skill

!!! abstract "In a nutshell"
    A **skill** is an add-on that teaches OVOS a new ability. This page is a hands-on
    walkthrough. You'll create a tiny skill from scratch, install it, and talk to it, in about
    ten minutes. You only need to be comfortable creating a few text files. New to the words
    here? Keep the [Glossary](glossary.md) open.

By the end you'll have a skill that answers when you say *"hello"*. Once you've done it once,
every other skill is just more of the same idea.

!!! note "Before you start: OVOS needs to already be installed"
    This walkthrough assumes OVOS is already installed and its Python environment is available
    to work in. See [ovos-installer](ovos-installer.md) or [RaspOVOS](install-raspovos.md) if
    you haven't done that yet. The ten minutes below covers writing and installing the skill
    itself, once that environment is in place.

    The flow runs from creating the folder layout to a working skill, checks the "hello" reply,
    and loops back to the pip install step on failure:

    ```mermaid
    flowchart TD
        A["Step 1: create folder layout"] --> B["Step 2: write skill code"]
        B --> C["Step 3: write .intent file"]
        C --> D["Step 4: write .dialog file"]
        D --> E["Step 5: pyproject.toml + entry point"]
        E --> F["Step 6: pip install -e ."]
        F --> G["Restart ovos-core"]
        G --> H{"Say 'hello'"}
        H -->|OVOS replies| I["Done"]
        H -->|no reply| J["Check ovos-logs show -l skills"]
        J --> F
    ```

## What a skill is made of

A skill is a small folder with three kinds of files:

| File | What it holds | Example |
|---|---|---|
| **the skill code** (`__init__.py`) | the Python that runs when an intent matches | "when the user says hello, speak a greeting" |
| **intent files** (`*.intent`) | example sentences **the user might say** | `hello`, `hi there` |
| **dialog files** (`*.dialog`) | lines **OVOS can speak back** (it picks one at random) | `Hello! Nice to meet you.` |

The intent and dialog files live in a `locale/<language>/` folder, so the same skill can be
translated. That's the whole model. [Anatomy of a Skill](skill-structure.md) covers it in depth.

## Step 1 — Create the folder layout

Make this structure (replace `youruser` with your name/handle later):

```text
ovos-skill-my-first/
├── pyproject.toml
└── ovos_skill_my_first/
    ├── __init__.py
    └── locale/
        └── en-us/
            ├── intents/
            │   └── Hello.intent
            └── dialog/
                └── hello.dialog
```

!!! note "Both layouts work"
    OVOS walks the *entire* `locale/<lang>/` folder looking for a file by name. So grouping
    files into `intents/`/`dialog/` subfolders (as above) or dropping them flat directly in
    `locale/en-us/` both work equally well. Pick whichever keeps your skill readable. The
    language folder name itself is also case-insensitive (`en-us` and `en-US` are the same
    folder to OVOS). See [Anatomy of a Skill](skill-structure.md) and
    [Intent Design](intents.md) for more on this layout.

## Step 2 — Write the skill code

Every skill is a Python class that subclasses [`OVOSSkill`](ovos-skill.md). A **decorator** (a
line starting with `@` placed just above a function) tells OVOS what that function is for. Here
`@intent_handler("Hello.intent")` means *"run this function when the user says something matching
`Hello.intent`"* (see [Decorators](decorators.md) for the full list). `self.speak_dialog("hello")`
then speaks a random line from `hello.dialog`.

`ovos_skill_my_first/__init__.py`:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class MyFirstSkill(OVOSSkill):

    def initialize(self):
        # runs once, after the skill is fully loaded and connected to the bus —
        # this is the place for setup that needs self.settings, self.bus, etc.
        # (a plain __init__ still runs too early for that; see Skill Settings)
        self.log.info("MyFirstSkill is ready")

    @intent_handler("Hello.intent")
    def handle_hello(self, message):
        self.speak_dialog("hello")
```

That's the entire skill. `initialize()` is optional. You only need it once you have setup work
that depends on the skill being fully wired up (reading [settings](skill-settings.md), registering
extra event handlers, and so on).

## Step 3 — Tell OVOS what the user might say

`ovos_skill_my_first/locale/en-us/intents/Hello.intent`: one example phrase per line. OVOS
learns the *pattern* from these, so you don't have to list every wording:

```text
hello
hi there
say hello
greet me
```

## Step 4 — Write what OVOS says back

`ovos_skill_my_first/locale/en-us/dialog/hello.dialog`: one option per line. OVOS picks one at
random so the assistant doesn't sound robotic:

```text
Hello! Nice to meet you.
Hi there!
Hey — how can I help?
```

## Step 5 — Make it installable

A skill is just a Python package that advertises itself to OVOS through an **entry point**.
`pyproject.toml`:

!!! note "You don't need to understand this file yet"
    Replace the two `name` placeholders and your username, and copy the rest as-is.

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ovos-skill-my-first"
version = "0.0.1"
description = "My first OVOS skill"
requires-python = ">=3.9"
license = {text = "Apache-2.0"}
dependencies = ["ovos-workshop>=0.0.1"]

# "<skill-name>.<author>" becomes the skill_id; the right-hand side is package:ClassName
[project.entry-points."opm.skill"]
"my-first.youruser" = "ovos_skill_my_first:MyFirstSkill"

[tool.setuptools]
packages = ["ovos_skill_my_first"]

[tool.setuptools.package-data]
# match whichever locale layout you picked: the first glob covers files placed flat
# directly in locale/<lang>/, the second covers files grouped in locale/<lang>/intents/
# and locale/<lang>/dialog/ subfolders — list both if you're not sure which you'll use
ovos_skill_my_first = ["locale/*/*", "locale/*/*/*"]
```

The entry-point key (`my-first.youruser`) becomes your skill's **`skill_id`**
(`<skill-name>.<author>`). The value points at your skill class. The `opm.skill` group is
how the [Plugin Manager](plugin-manager.md) discovers installed skills.

For the full packaging reference (including GUI assets in package-data), see
[Anatomy of a Skill](skill-structure.md).

## Step 6 — Install it and talk to it

First, activate the same Python environment OVOS runs in, so the skill installs into the
interpreter `ovos-core` actually uses. For example, `source ~/.venvs/ovos/bin/activate` for
a venv install. In plain English: a **[virtual environment](glossary.md)** is an isolated
Python install. "Activating" it just means that **[pip](glossary.md)** will now install
into the one OVOS actually uses, instead of somewhere else. See the
[Glossary](glossary.md) if these terms are new.

That exact path is only an example, not something you can assume. raspOVOS, `ovos-installer`,
and container installs each put it somewhere different.

- Check where your particular install created its environment, for example the installer's
  summary screen (see [ovos-installer](ovos-installer.md#environment-summary)).
- Advanced: if you installed via [systemd](glossary.md), its unit file's
  `Environment=`/`ExecStart=` lines show the path.
- Still stuck? See [Troubleshooting](troubleshooting.md).

If you're running OVOS in
a container instead, there's no host environment to activate. Install into the container
directly: `docker compose exec <service> pip install -e .` (run from the skill folder, with
the skill's path mounted into the container, or copy it in first).

From inside the `ovos-skill-my-first/` folder:

```bash
pip install -e .
```

Restart `ovos-core` (or it will pick the skill up on its next scan). See
[Stage 1 of Troubleshooting](troubleshooting.md#stage-1-is-the-service-even-running-and-is-the-bus-reachable)
for exactly how to start/restart the OVOS services. Then say your configured wake word first
(default **"Hey Mycroft"**), wait for the listening chime, and then say:

> "**hello**"

OVOS replies with one of your dialog lines. You just wrote a skill.

!!! note "If OVOS doesn't reply"
    Check the skills log for your skill_id: `ovos-logs show -l skills`. See
    [Troubleshooting](troubleshooting.md) for how to read what it's telling you. `Hello.intent`
    is a **Padatious** template intent, so the live device also needs
    `ovos-padatious-pipeline-plugin` installed and listed in its `intents.pipeline` config for
    the file to match at all. See [Test Your Skill](testing-your-skill.md) for the same
    requirement in the automated test.

!!! tip "No microphone handy, or want to test without talking?"
    You can send the utterance straight onto the bus as text, skipping the wake word and mic
    entirely: `ovos-say-to "hello"`. See [Troubleshooting](troubleshooting.md#stage-3-did-stt-produce-text)
    for more on this and other text-based ways to test a skill.

## Adding a file later? Know which install you have

If you add a new `.intent` or `.dialog` file after this walkthrough, what you do next depends on
how the skill is installed. With an editable install (`pip install -e .`, as used above), the
files live on disk where you edited them, so a restart of `ovos-core` (or the skills service) is
enough. No reinstall needed. With a normal wheel install, the files were copied into the package
at install time, so you must reinstall the skill (`pip install .` again, or the equivalent for a
built wheel) before OVOS can see the new file.

## Where to go next

- **Pull a value out of what the user said** (a name, a city, a number). See [Intent Design](intents.md).
- **Have a back-and-forth** ("what's your name?" then a reply). See [Continuous Conversation](converse.md).
- **Save settings or files**. See [Skill Settings](skill-settings.md) and [Filesystem](skill-filesystem.md).
- **Make it sound good and behave well**. See [Skill Best Practices](skill-best-practices.md).
- **Test it automatically**. See [Test Your Skill](testing-your-skill.md), which continues this
  exact example. For the broader `ovoscope` reference, see [Testing Skills with ovoscope](ovoscope-overview.md).
- **Publish it** so others can install it. See [Sharing your skill](skill-json.md#sharing-your-skill).
- **See how an utterance actually travels through OVOS**. See [Life of an Utterance](life-of-an-utterance.md).
- Browse real skills for ideas in [Skill Examples](skill-examples.md).
- Questions along the way? Ask in the
  [skills channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org).

---
**Read next:** [Skill Structure](skill-structure.md)
**Related:** [Skill Cookbook](skill-cookbook.md) · [Intent Design](intents.md) · [Test Your Skill](testing-your-skill.md) · [Skill Development Overview](skills-overview.md)
