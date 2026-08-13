# Start Here

!!! abstract "In a nutshell"
    This tab is for anyone new to OpenVoiceOS. It covers picking an install route, getting the assistant running, and fixing the first problems you hit. It is not for developers who want to understand the internals or build a skill; see the Concepts and Skills tabs for that.

This tab is for anyone new to OpenVoiceOS: picking hardware, installing, and getting the assistant talking back.

## Start here

Pick one of the two install routes below, then move on to the three pages that follow. They cover changing the wake word and voice, trying example projects, and finding out what skills already ship by default.

First, pick your install route:

- **[Install with ovos-installer](ovos-installer.md)** (recommended): the guided path for most hardware, including an existing Raspberry Pi OS setup.
- **[RaspOVOS image](install-raspovos.md)** (alternative): a flash-and-boot SD card image for a spare Raspberry Pi. Its **stable** images date from mid-2025 and are not receiving updates (newer DEV builds on the [releases page](https://github.com/OpenVoiceOS/raspOVOS/releases) are untested work toward a refreshed image), so check status first. The installer is the supported route meanwhile.

Once the assistant is installed:

1. [Make it yours](personalize.md): change the wake word, voice, and language once the assistant is running.
2. [Fun stuff to try](showcase.md): a tour of things to build once the basics work.
3. [What can I say? (Skills)](skill-examples.md): a catalog of the default skills you can talk to right away.

## More install options

If neither of the two routes above fits, this page lists the other channels you can pick by hand.

- **Manual & Advanced Install**: [Release channels](release-channels.md): for tinkerers who want to pick a stability track by hand instead of using the installer.

## Coming from somewhere else

If you already used a different assistant, start with the page that matches it. It maps old habits and terms onto their OVOS equivalent.

- [Coming from Mycroft](coming-from-mycroft.md): what carries over if you had a Mycroft device.
- [Coming from Alexa](coming-from-alexa.md): what to expect if you're used to a commercial assistant.
- [Accessibility](accessibility.md): using OVOS without sight, hearing, or a screen.

## Help & Troubleshooting

Something not working? Start with the quick-fix page. Move to the decision tree only if the quick fixes do not solve it.

- [It's not behaving](everyday-help.md): quick fixes for common problems, no terminal needed.
- [Troubleshooting & Debugging](troubleshooting.md): a deeper decision tree for tracking down why a command failed.
- [RaspOVOS Troubleshooting](raspovos-troubleshooting.md): fixes specific to the Raspberry Pi image: power, sound, wake word, STT.

Want to understand how OVOS works internally rather than just use it? That's the Concepts tab. Ready to build a skill of your own? That's the Skills tab.

---
**Read next:** [Install with ovos-installer](ovos-installer.md)
**Related:** [Concepts Overview](concepts-overview.md) · [Skill Development Overview](skills-overview.md) · [Reference Overview](reference-overview.md)
