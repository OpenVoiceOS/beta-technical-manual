# What Can I Say? Default Skills Overview

!!! abstract "In a nutshell"
    A "skill" is an add-on that teaches your assistant to do one thing: tell the weather, set an
    alarm, play the radio, answer trivia. This page is an index of ready-made skills you can add
    to OVOS, grouped by what they're for, each linking to a subpage with real example phrases and
    install steps. Some come pre-loaded depending on how you set OVOS up, others you add yourself. See
    [Your First Skill](first-skill.md) if you want to build your own, or the
    [Glossary](glossary.md) for terms.

A non-exhaustive list of skills available for OpenVoiceOS. Whether a given skill is already on your
assistant depends on how you installed it. See the legend below.

Each skill shows a **Maturity** rating from its repository health. See the [Maturity Scale](maturity.md).

!!! tip "How to get a skill"
    Many of these ship with the [`ovos-installer`](ovos-installer.md)'s skill selection. To add
    one yourself, install its package (the repo link and install command are in the
    collapsed "Install" block under each skill on its subpage) and restart `ovos-core`. It scans for
    installed skills automatically. On RaspOVOS, prefer `ovos-install <package>`, RaspOVOS's own
    helper, which installs with the correct version constraints. On any other setup, `pip install
    <package>` works the same way. If a skill isn't published to PyPI, install straight from
    git, e.g. `pip install git+https://github.com/OpenVoiceOS/ovos-skill-weather`. To build your
    own, follow [Your First Skill](first-skill.md).

    **Availability legend:**

    - **Installer default**: installed automatically when the `ovos-installer`'s `skills`
      feature is on (the default).
    - **Installer optional**: installed only if you also enable the installer's
      `extra-skills` feature.
    - **Manual install only**: not offered by the installer at all. Add it yourself with
      `ovos-install` (on RaspOVOS) or `pip install` (otherwise).

---

## [Alerts & Time](skill-examples-alerts-time.md)

| Skill | What it does |
| --- | --- |
| [Alerts](skill-examples-alerts-time.md#alerts-timers-reminders-alarms) | Alarms, timers, reminders, events, todos, with optional CalDAV sync. |
| [Date & Time](skill-examples-alerts-time.md#date-time) | Current time, date, and calendar-day facts. |
| [Naptime](skill-examples-alerts-time.md#naptime-snooze-the-assistant) | Puts the assistant to sleep until you say "wake up". |

## Weather

**Installer default**

Get weather conditions, forecasts, expected precipitation and more! You can also ask for other
cities around the world. Current conditions and weather forecasts come from OpenMeteo.

**Usage examples:**

- What's the temperature in Paris tomorrow in Celsius?
- When will it rain next?
- What's the high temperature tomorrow
- Is it going to snow in Baltimore?
- what is the weather like?

- How windy is it?
- What is the weather this weekend?
- What is the weather in Houston?
- Will it be cold on Tuesday
- What's the temperature?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-weather](https://github.com/OpenVoiceOS/ovos-skill-weather) · `pip install ovos-skill-weather` · Maturity: Mature

-------

## Smart Home

Controlling actual smart-home devices (lights, plugs, thermostats, scenes) isn't built into OVOS
itself. It is a separate skill that talks to [Home Assistant](https://www.home-assistant.io/).
See [OVOS & Home Assistant](home-assistant.md) for the full setup story in both directions
(OVOS controlling HA devices, and HA using OVOS's own speech engines), including install steps
and usage examples.

-------

## [Music & Radio](skill-examples-media.md)

| Skill | What it does |
| --- | --- |
| [PyRadios](skill-examples-media.md#pyradios) | Plays stations from the Radio Browser API directory. |
| [SomaFM](skill-examples-media.md#somafm) | Plays commercial-free internet radio from SomaFM. |
| [News](skill-examples-media.md#news) | Plays news streams from around the globe. |
| [Local Media](skill-examples-media.md#local-media) | Browses and plays audio/video files from a USB drive or local folder. |

## [Fun & Trivia](skill-examples-fun.md)

| Skill | What it does |
| --- | --- |
| [Dad Jokes](skill-examples-fun.md#dad-jokes) | Tells dad jokes. |
| [Parrot](skill-examples-fun.md#parrot) | Repeats back whatever you say. |
| [Confucius Quotes](skill-examples-fun.md#confucius-quotes) | Quotes from Confucius. |
| [Today in History](skill-examples-fun.md#today-in-history) | Historical events for any calendar day. |
| [Number Facts](skill-examples-fun.md#number-facts) | Trivia facts about numbers. |
| [Movie Master](skill-examples-fun.md#movie-master) | Movie, actor, and production info. |
| [ISS Location](skill-examples-fun.md#iss-location) | Tracks the International Space Station. |
| [DuckDuckGo](skill-examples-fun.md#duckduckgo) | Answers questions via DuckDuckGo. |
| [Wikipedia](skill-examples-fun.md#wikipedia) | Answers questions via Wikipedia. |
| [WikiHow](skill-examples-fun.md#wikihow) | How-to instructions for nearly everything. |
| [Wolfie (Wolfram Alpha)](skill-examples-fun.md#wolfie-wolfram-alpha) | General-knowledge and math questions. |
| [Wordnet](skill-examples-fun.md#wordnet) | Dictionary-like word lookups. |
| [Spelling](skill-examples-fun.md#spelling) | Spells words and phrases aloud. |
| [Personal](skill-examples-fun.md#personal) | The assistant talks about its own "birth" and community. |
| [Hello World](skill-examples-fun.md#hello-world) | Example skill for skill authors to study. |

## [Utilities](skill-examples-utilities.md)

| Skill | What it does |
| --- | --- |
| [Volume](skill-examples-utilities.md#volume) | Controls OVOS volume by voice. |
| [IP Address](skill-examples-utilities.md#ip-address) | Reports network connection info. |
| [Speedtest](skill-examples-utilities.md#speedtest) | Runs an internet bandwidth test. |
| [Boot Finished](skill-examples-utilities.md#boot-finished) | Announces when OVOS has fully started. |
| [Dictation](skill-examples-utilities.md#dictation) | Transcribes speech to a text file. |
| [Audio Recording](skill-examples-utilities.md#audio-recording) | Records and manages audio clips. |
| [Commands](skill-examples-utilities.md#commands) | Runs shell scripts and system commands by voice. |

---

**Read next:** [Skill Development Overview](skills-overview.md)
**Related:** [Fun stuff to try](showcase.md) · [Your First Skill](first-skill.md) · [It's not behaving](everyday-help.md) · [Skill Dev F.A.Q.](skill-dev-faq.md)
