# Reference Overview

!!! abstract "In a nutshell"
    This tab is for looking up a specific fact: an event name, a CLI command, a repository, a parser library, or a hardware detail, without reading a tutorial. It also holds the pages contributors need: how to submit a change and how the CI workflows work.

This tab is for looking up a specific fact: an event name, a CLI command, a repository, or a hardware detail, without reading a tutorial.

## Start here

1. [OVOS Repository Index](ecosystem-index.md): every repository in the ecosystem and what it does.
2. [Bus Events Reference](bus-events.md): the messagebus events skills and services send and listen for.
3. [Command-line Tools](cli-tools.md): the CLI commands installed with OVOS.
4. [Core Libraries](core-libraries.md): the shared libraries most components depend on.

## NLP Libraries (parsers)

Standalone text-parsing libraries used across OVOS, each usable on its own outside a running assistant.

- [Language Names](lang-parser.md), [Numbers](number-parser.md), [Dates & Time](date-parser.md).
- [Colors](color-parser.md), [Quebra Frases](quebra-frases.md) (sentence splitting).

## Hardware

Building or wiring a physical device: general integration guidance, sound hardware setup, and the two reference Mycroft devices.

- [Hardware Integrators](hardware-integrators.md): building a physical device on OVOS.
- [i2c Sound & Audio Setup](i2c-sound.md): wiring up sound hardware.
- [Mark 1](mark1.md) and [Mark 2](mark2.md): the reference Mycroft hardware.

## Tools

Standalone utilities: a viewer for this documentation, and a web UI for editing skill settings.

- [ovos-docs-viewer](docs-viewer.md): browsing this documentation offline or in-app.
- [ovos-skill-config-tool](skill-settings.md#web-based-settings-ui-community): a web UI for editing skill settings.

## Contributing & Project Infra

For maintainers and contributors: how to get a change merged, and how the gh-automations CI workflows are structured.

- [Contributing](contributing.md): how to get a change merged.
- **gh-automations**: [Overview](gh-automations-overview.md), [Release Flow](gh-automations-release.md), [Workflows](gh-automations-workflows.md), [Release Workflows](gh-automations-release-workflows.md), [PR Check Workflows](gh-automations-pr-workflows.md), [Quality Workflows](gh-automations-quality-workflows.md).

## Project Info

Background on the project itself: its history, repos no longer maintained, and its license.

- [Timeline](timeline.md), [Deprecated & Archived Repos](deprecated-repos.md), [License](license.md).

Looking for how a concept works rather than a lookup table? That's the Concepts tab.

---
**Read next:** [OVOS Repository Index](ecosystem-index.md)
**Related:** [Concepts Overview](concepts-overview.md) · [Skill Development Overview](skills-overview.md) · [Production Overview](production-overview.md)
