# RaspOVOS Commands Reference

!!! abstract "In a nutshell"
    When you log in to a raspOVOS device, it prints a welcome banner listing its built-in helper commands. These are **raspOVOS-specific shell helpers** (aliases and small scripts baked into the image), not a standard `pip install` of OVOS. This page is the full reference list. Run `ovos-help` on the device at any time to reprint it. See the [Glossary](glossary.md) for unfamiliar terms.

---

## Helpful Commands

**Web interfaces:**

- `ovos-yaml-editor`: web editor for OVOS configuration (port 9210).
- `ovos-skill-config-tool`: web editor for individual skill settings (port 8000).

**Talking to OVOS:**

- `ovos-config`: manage your local OVOS configuration files.
- `ovos-listen`: activate the microphone to listen for a command.
- `ovos-speak <phrase>`: have OVOS speak a phrase to the user.
- `ovos-say-to <phrase>`: send an utterance to OVOS as if you had spoken it.
- `ovos-simple-cli`: chat with your device from the terminal.
- `ovos-docs-viewer`: open the documentation viewer (also `ovos-manual`, `ovos-skills-info`).

**Managing packages:**

- `ovos-install`: install OVOS packages with the correct version constraints.
- `ovos-update`: routine, in-place update of all OVOS and skill packages, scoped to the release
  channel recorded in `/opt/ovos/tag`. It does not change the base image. Moving to a new
  raspOVOS release (a major image update) instead means reflashing a new image and restoring
  your `.config/mycroft` and `.local/share/mycroft` from a backup — see the repo's
  [update how-to](https://github.com/OpenVoiceOS/raspOVOS/blob/dev/docs/how-to/update.md) for the
  backup/restore commands.
- `ovos-force-reinstall`: force a full reinstall of all OVOS packages (last-resort repair).
- `ovos-freeze`: export installed OVOS packages to `requirements.txt`.
- `ovos-outdated`: list outdated OVOS/skill packages.
- `ovos-reset-brain`: reset the "OVOS brain" to a blank state by uninstalling all skills.

**Inspecting plugins:**

- `ls-skills`: list the `skill_id` of every installed skill.
- `ls-stt` / `ls-tts` / `ls-ww` / `ls-tx`: list installed [STT](stt-plugins.md) / [TTS](tts-plugins.md) / wake word / [translation](translation-plugins.md) plugins.

**Sound/audio:**

- `ovos-audio-diagnostics`: print the active sound server, sinks, and default output device.
- `ovos-audio-setup`: interactive audio configuration menu (handy after wiring up a HAT).

**Logs and status:**

- `ologs`: follow the logs in real time — **except `bus.log`**, which the alias excludes
  (`tail -f ~/.local/state/mycroft/!(bus.log)`). For messagebus traffic, tail that file directly:
  `tail -f ~/.local/state/mycroft/bus.log`.
- `ovos-logs [COMMAND] --help`: a small tool to help navigate the logs.
- `ovos-status`: list OVOS-related systemd services.
- `ovos-restart`: restart all OVOS-related systemd services.
- `ovos-server-status`: check the live status of the public OVOS servers.

**Misc:**

- `ovos-commands`: usage examples for the installed skills.
- `ovos-support`: compile logs into a support package to share when asking for help.
- `ovos-help`: reprint this command list.
- `ovos-logo`: print the raspOVOS logo.

!!! note "Audio HAT setup on raspOVOS uses `ovos-i2csound`"
    On raspOVOS, an i2c sound HAT (such as a Respeaker or the Mark 2's SJ201) is detected and
    configured at boot by the **`ovos-i2csound`** service shipped in the image, which writes the
    detected board to `/etc/OpenVoiceOS/i2c_platform`. This is specific to the raspOVOS image.
    The [ovos-installer](ovos-installer.md) does **not** use it (see
    [Mark 2 Hardware](mark2.md) for the installer's kernel-driver approach).

---

## Check Logs in Real-Time

- Use the `ologs` command to monitor logs live on your screen.
- If you're unsure whether the system has finished booting, check logs using this command.

---
**Read next:** [What can I say?](skill-examples.md) · [Fun stuff to try](showcase.md)
**Related:** [RaspOVOS](install-raspovos.md) · [RaspOVOS Troubleshooting](raspovos-troubleshooting.md) · [Command-line Tools](cli-tools.md)
