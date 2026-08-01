# Concepts Overview

This tab is for anyone who wants to understand how OpenVoiceOS is built, not just use it: developers, integrators, and curious users.

## Start here

1. [High-level Overview](architecture-overview.md): the whole system as a team of small independent parts talking over a shared channel.
2. [The Life of an Utterance](life-of-an-utterance.md): follow one spoken sentence from microphone to answer.
3. [MessageBus Service](bus-service.md): the shared channel every other part talks over.
4. [Security & Trust Model](security-model.md): what OVOS assumes about the device it runs on.

## Specs and quality

- [Formal Specifications](architecture-specs.md): component contracts written down, not just implemented.
- [Specification Tooling](spec-tooling.md): tools that check code against those contracts.
- [Maturity Scale](maturity.md): how to read the maturity badges used throughout this manual.

## System pieces

- [Plugin Manager](plugin-manager.md): how OVOS finds and loads swappable plugins.
- [Composable Deployments](composable-deployments.md): using OVOS as a library instead of the full assistant.

## Configuration

- [Overview](config.md): how settings are changed and where they live.
- [Reference](config-reference.md): lookup table of settings and defaults.
- [Locations](locations-ref.md): the folders OVOS reads and writes.

## ovos-core Internals

`ovos-core` is the process that owns skills and intent matching. Its parts:

- [Overview](core.md), [Skill Manager](skill-manager.md), [Intent Service](intent-service.md), [Skill Installer](skill-installer.md).

## Sibling Services

These run as their own processes on the bus, separate from `ovos-core`.

- [Speech Service](speech-service.md), [Audio Service](audio-service.md), [Media Service](ovos-media.md).
- [Screens on OVOS Today](gui-status.md), [GUI Service (legacy)](gui-service.md).
- [PHAL](phal.md) for hardware access.

Digging into how intents get matched? That's the Pipeline tab. Building a skill? That's the Skills tab.
