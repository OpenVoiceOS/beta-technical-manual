# Production Overview

!!! abstract "In a nutshell"
    This tab is for anyone running OVOS beyond a single test device: fleets of devices, self-hosted servers, and deployments that must stay current across upgrades. It is not for a first install on one device; see the Get Started tab for that.

This tab is for anyone running OVOS beyond a single test device: fleets, servers, and long-lived deployments.

## Start here

1. [Production Operations](production-operations.md): decide whether you need a single hardened device or a fleet of them, and how the two setups differ.
2. [Privacy & Security](privacy-security.md): what data OVOS handles and how to lock a deployment down.
3. [Self-hosting Servers](stt-server.md): run your own STT, TTS, or translation backend instead of a third party's.
4. [Remote Agents with HiveMind](hivemind-agents.md): connect and manage devices remotely.

## The upgrade trio

Keeping a production deployment current means reading these together:

- [Updating from Older OVOS](updating-from-older-ovos.md): a hub with four audience pages.
  Deployers go straight to [For Device & Fleet Operators](updating-deployers.md). The others:
  [Skill Maintainers](updating-skills.md), [Plugin Maintainers](updating-plugins.md),
  [Remote Bus Clients](updating-remote-clients.md).
- [Upcoming Changes](upcoming-changes.md): what's changing next, so upgrades don't surprise you.
- [Server Compatibility Layers](server-compat-layers.md): keeping self-hosted servers working across versions.

## Self-hosting Servers

Run your own STT, TTS, or translation backend instead of depending on a third party. Each protocol has its own page; Server Compatibility Layers covers keeping them working as OVOS versions change.

- [STT Server](stt-server.md), [TTS Server](tts-server.md), [Translate Server](translate-server.md).

## Home Assistant

Connecting OVOS to an existing Home Assistant install, either as a client or by exposing OVOS engines as Wyoming-protocol services HA can call.

- [Overview](home-assistant.md): connecting OVOS to a Home Assistant install.
- [Wyoming Bridges](wyoming-bridges.md): using OVOS engines as Wyoming-protocol services for HA.

New to OVOS and just want it working on one device? That's the Get Started tab. Building the agent that runs on your fleet? That's the Agents tab.

---
**Read next:** [Production Operations](production-operations.md)
**Related:** [Get Started](start-here.md) · [Agents Overview](agents-overview.md) · [Reference Overview](reference-overview.md)
