# Concepts Overview

!!! abstract "In a nutshell"
    This tab explains how OpenVoiceOS is built: the processes, the shared message bus that connects them, and the rules each part must follow. It is for developers, integrators, and curious users who want the architecture, not just the install steps. For hands-on install and setup, see the Get Started tab.

This tab is for anyone who wants to understand how OpenVoiceOS is built, not just use it: developers, integrators, and curious users.

## Start here

1. [High-level Overview](architecture-overview.md): the whole system as a team of small independent parts talking over a shared channel.
2. [The Life of an Utterance](life-of-an-utterance.md): follow one spoken sentence from microphone to answer.
3. [MessageBus Service](bus-service.md): the shared channel every other part talks over.
4. [Security & Trust Model](security-model.md): what OVOS assumes about the device it runs on.

## Specs and quality

OVOS components follow written specs, and this manual has tooling to check code against them. Start with the specs themselves, then the tooling, then the badge scale used to mark how mature each part is.

- [Formal Specifications](architecture-specs.md): component contracts written down, not just implemented.
- [Specification Tooling](spec-tooling.md): tools that check code against those contracts.
- [Maturity Scale](maturity.md): how to read the maturity badges used throughout this manual.

## System pieces

Two cross-cutting pieces don't fit under a single service: how plugins get discovered, and how to run OVOS as a library instead of a full assistant.

- [Plugin Manager](plugin-manager.md): how OVOS finds and loads swappable plugins.
- [Composable Deployments](composable-deployments.md): using OVOS as a library instead of the full assistant.

## Configuration

Start with the overview to learn where config files live and how they layer, then use the reference and locations pages as lookup tables.

- [Overview](config.md): how settings are changed and where they live.
- [Reference](config-reference.md): lookup table of settings and defaults.
- [Locations](locations-ref.md): the folders OVOS reads and writes.

## ovos-core Internals

`ovos-core` is the process that owns skills and intent matching. Its parts:

- [Overview](core.md), [Skill Manager](skill-manager.md), [Intent Service](intent-service.md), [Skill Installer](skill-installer.md).

## Sibling Services

These run as their own processes on the bus, separate from `ovos-core`. Each page covers one service; start with whichever one matches the part of the system you're investigating.

- [Speech Service](speech-service.md), [Audio Service](audio-service.md), [Media Service](ovos-media.md).
- [Screens on OVOS Today](gui-status.md), [GUI Service (legacy)](gui-service.md).
- [PHAL](phal.md) for hardware access.

Digging into how intents get matched? That's the Pipeline tab. Building a skill? That's the Skills tab.

---
**Read next:** [High-level Overview](architecture-overview.md)
**Related:** [Pipeline Overview & Reference](pipelines-overview.md) · [Skill Development Overview](skills-overview.md) · [Reference Overview](reference-overview.md)
