# Developer FAQ

!!! abstract "In a nutshell"
    Short, direct answers to the questions that come up most often while building an OVOS skill.
    They come from real questions asked in the community and from the sticking points people hit
    while working through this manual. Each answer routes you to the full page for the depth you
    need. Skim this page when you hit one of these, then open the linked page. It assumes you have
    already built a basic skill. Start with [Your First Skill](first-skill.md) if not.

---

## Getting started and the inner dev loop

### My utterance doesn't do anything. Where do I even start looking?

Work through it stage by stage: is the messagebus up, did the mic/wake word fire, did STT produce
text, did a pipeline stage match, did the handler raise, did TTS speak. Each stage has an exact log
line to grep for and a bus message to filter on. Start by injecting the text directly, skipping the
mic entirely:

```bash
ovos-say-to "what time is it"
```

→ full story: [Troubleshooting & Debugging](troubleshooting.md)

### How do I test a skill without talking into a microphone?

Three options, cheapest first: `ovos-say-to "some phrase"` injects a `recognizer_loop:utterance`
message as if STT had already produced it. `ovos-busmon` gives you a browser view of every bus
message live, including a button to inject arbitrary messages yourself. And
[`ovoscope`](ovoscope-overview.md) runs a real in-process assistant (`MiniCroft`) with no audio
hardware at all, so you can write pytest assertions instead of speaking out loud every time.

→ full story: [Test Your Skill](testing-your-skill.md), [Troubleshooting](troubleshooting.md#stage-3-did-stt-produce-text)

### How do I restart just my skill while I'm iterating on it, without restarting all of OVOS?

Use `ovos-skill-launcher`, shipped by `ovos-workshop`. It connects to a running bus, loads (or
reloads) one skill by ID, and stays attached so you can edit-and-rerun without touching the rest of
the stack:

```bash
ovos-skill-launcher my-first.youruser /path/to/ovos-skill-my-first
```

Pass just the `skill_id` if the skill is already discoverable on the standard skill directories.
Pass a second argument to point at an arbitrary local path instead.

→ full story: [Command-line Tools](cli-tools.md)

### Why isn't my skill loading at all?

Almost always one of two things: the `opm.skill` entry point in `pyproject.toml` doesn't match what
OVOS is looking for, or the package failed to import. Check `skills.log` for your `skill_id` right
after startup. A traceback there names the exact import problem. If nothing about your skill
appears in the log at all, `pip show <your-package>` to confirm it actually installed, then confirm
the entry point:

```toml
[project.entry-points."opm.skill"]
"my-first.youruser" = "ovos_skill_my_first:MyFirstSkill"
```

The left-hand side (`<skill-name>.<author>`) becomes the `skill_id`. The right-hand side is
`package:ClassName`. `find_skill_plugins()` in `ovos-plugin-manager` enumerates this exact group.
A typo here means the skill is invisible, not broken.

→ full story: [Your First Skill](first-skill.md#step-5-make-it-installable), [Skill Manager](skill-manager.md)

---

## Why isn't it doing what I expect

### Why doesn't my phrase match my intent?

`ovos-core` logs every pipeline stage it tries, in order, and each one logs a miss if it doesn't
claim the utterance:

```text
DEBUG - no match from <bound method ...PadatiousPipeline.match_high ...>
DEBUG - no match from <bound method ...AdaptPipeline.match_high ...>
```

Reproduce it deterministically with `ovos-say-to "the exact phrase"`, then grep `skills.log` for
that text. If every matcher rejects it, it's a training-data problem in your intent files (missing
sample phrase, wrong vocab), not a bug in the pipeline. Add the phrasing to your `.intent`/`.voc`
file and retrain.

→ full story: [Troubleshooting: Stage 4](troubleshooting.md#stage-4-which-pipeline-stage-matched-or-didnt), [Pipelines Overview](pipelines-overview.md)

### Should my skill use Adapt or Padatious for intent matching?

Padatious is the better default for most skills: it's a trained neural matcher that generalizes
across paraphrasing and localizes easily to other languages. Reach for Adapt instead only for a
personal/private skill where you need strict, predictable command-and-control matching in a single
language you fully control.

→ full story: [Adapt Pipeline](adapt-pipeline.md#when-to-use-adapt-in-ovos), [Padatious Pipeline](padatious-pipeline.md#when-to-use)

### My skill needs a follow-up question. How do multi-turn conversations work?

Two different mechanisms depending on the shape of the follow-up. If you're waiting for the answer
to a specific question you just asked, call `self.get_response(...)`. It blocks and returns the
next utterance (or `None` on timeout). If instead you want your skill to keep intercepting *any*
follow-up for a while after it last acted ("yes", "no", "the red one"), implement `converse()`.
That requires subclassing `ConversationalSkill`, not the plain `OVOSSkill`:

```python
from ovos_workshop.skills.converse import ConversationalSkill

class MySkill(ConversationalSkill):
    def converse(self, message):
        if "yes" in message.data["utterances"][0]:
            self.speak("Great!")
            return True
        return False
```

→ full story: [Converse](converse.md)

### I implemented `converse()` but it never fires. Why?

Two common gates sit in front of it, both outside your skill's own code. First, converse
participation is opt-in/opt-out per skill via `ConverseMode` and the converse whitelist/blacklist.
If your skill isn't allowed to converse at all, `converse()` is never called no matter what it
returns. Second, converse only runs for skills the orchestrator considers "active" for the
session (typically the last skill that spoke or handled an intent). An unrelated skill sitting
idle won't get a chance either. Check both before assuming your `converse()` logic itself is
broken.

→ full story: [Permissions & Activation Control](permissions.md), [Converse](converse.md)

---

## Language, settings, and where things live

### How do I make my skill speak in more than one language?

Put per-language `.intent`/`.voc`/dialog files under `locale/<lang>/`, and a translated `skill.json`
in the same folder if you want a localized store listing. Padatious intents localize with the least
friction since they're trained from example phrases rather than hand-written grammar rules.

→ full story: [Skill Structure](skill-structure.md), [Language Support](lang-support.md), [Skill Metadata File](skill-json.md#language-support)

### Where do my skill's settings and files actually live on disk?

Settings live at `$XDG_CONFIG_HOME/<base_folder>/skills/<skill_id>/settings.json`. On most Linux
systems that's `~/.config/mycroft/skills/<skill_id>/settings.json`, since `<base_folder>` defaults
to `mycroft` for backwards-compatibility (a system-wide `ovos.conf`, or the
`OVOS_CONFIG_BASE_FOLDER` environment variable, can rename it, commonly to `OpenVoiceOS`). A
`FileWatcher` on that path fires `ovos.skills.settings_changed` whenever it changes. Persistent
skill data belongs under `self.file_system`, not a path you build yourself. It resolves to
`$XDG_DATA_HOME/mycroft/filesystem/<skill_id>/` and survives skill reinstalls.

```python
self.settings.get("my_key", "default")   # read
self.settings["my_key"] = "value"        # write, auto-saved on shutdown
with self.file_system.open("cache.json", "w") as f:
    ...
```

→ full story: [Skill Settings](skill-settings.md), [Filesystem Access](skill-filesystem.md), [Locations](locations-ref.md)

---

## Dependencies, packaging, and sharing

### Where do my skill's Python dependencies go, `skill.json` or `pyproject.toml`?

`pyproject.toml`'s `dependencies` list is what actually gets installed by `pip`. That's the real
dependency mechanism. `skill.json` only carries `extra_plugins`, for companion OVOS plugins (a TTS
voice, a G2P engine) your skill expects to be present but doesn't import as a Python dependency.
`ovos-workshop` never reads `skill.json` to install anything.

→ full story: [Skill Metadata File](skill-json.md#installation-behavior)

### How do I share or publish my skill?

Push it to a GitHub repository (`source` in `skill.json` should point there). Optionally publish it
to PyPI too and set `package_name` so people can `pip install` it directly. A skill without a PyPI
release is still installable straight from git via `pip_spec`. From there, list it on the
[OVOS Skill store](https://openvoiceos.github.io/OVOS-skills-store). The store reads `name`, `description`,
`examples`, `tags`, `icon`, and `images` from `skill.json` to build the listing card.

→ full story: [Skill Metadata File: Sharing your skill](skill-json.md#sharing-your-skill)

---

### Can I sell my skill, or gate features behind a license key?

There is no monetization, DRM, or licensing mechanism anywhere in the stack: skills are
plain Python packages, `skill.json`'s `license` field is SPDX open-source metadata, and
nothing in skill loading checks entitlements. You can of course implement your own
license-key check inside your skill's code, but the platform gives you no enforcement,
store billing, or copy protection.

---

## Using AI/LLMs from a skill

### Can I use an LLM inside my skill?

Yes, two ways. If you just want conversational fallback behavior for your whole assistant, that's
what a [persona](personas.md) is for, with no skill code needed. If you specifically want your skill's
own handler to call an LLM (to phrase a reply, summarize something, classify an answer), load an
agent engine plugin directly and call it like any other object:

```python
from ovos_plugin_manager.agents import load_chat_plugin
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole

engine_cls = load_chat_plugin("ovos-openai-plugin")  # or ovos-gguf-plugin, etc.
engine = engine_cls(config={})  # see the plugin's own README for its config keys (API URL, key, model)
reply = engine.continue_chat([AgentMessage(role=MessageRole.USER, content="summarize this in one sentence: ...")])
```

`continue_chat(messages: List[AgentMessage], session_id="default", lang=None, units=None, tools=None) -> AgentMessage`
is the same method every `ChatEngine` implements, regardless of backend, so swapping providers
doesn't touch your skill's logic.

→ full story: [Agent Plugins](agent-plugins.md), [Agent Engine Types](agent-plugins.md#agent-engine-types), [Personas](personas.md)

---

## Still stuck?

Ask in the **[skills channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org)**, or
post a longer question on the **[Open Conversational AI forum](https://community.openconversational.ai/)**.
Include a log excerpt or `ovos-busmon` export for the stage where the trail goes cold. See
[Troubleshooting](troubleshooting.md#where-to-ask-for-help).

---

**Read next:** [Skill Development Overview](skills-overview.md) · [Testing Your Skill](testing-your-skill.md)
**Related:** [Your First Skill](first-skill.md) · [Troubleshooting & Debugging](troubleshooting.md) · [Skill Cookbook](skill-cookbook.md) · [Testing Reference (ovoscope)](ovoscope-overview.md)
