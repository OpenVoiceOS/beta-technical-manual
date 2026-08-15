# The `ovos-installer` Wizard, Screen by Screen

!!! abstract "In a nutshell"
    This page walks through every screen the `ovos-installer` TUI shows you, in order, from
    language selection to the final telemetry prompts. Use it as a reference while the
    installer is running, or to see what a screen means before you get to it. For the
    commands that launch the installer, see [How to Install Open Voice OS](ovos-installer.md).

!!! tip "Scripting this instead?"
    Everything below can be answered up front in a
    [scenario file](ovos-installer.md#non-interactive-scenario-install), so the installer runs
    with no prompts at all. Useful for fleets or CI.

---

## Navigation

- navigation is done via arrow keys


- pressing space selects options in the lists


    - eg. when selecting `virtualenv` or `containers`


- pressing tab will switch between the options and the `<next>`/`<back>` buttons


- pressing enter will execute the highligted `<next>`/`<back>` option

---

## Language Selection

The first screen lets you select your preferred language for the installer's own text, not
the assistant's spoken language. See [Language Support](lang-support.md) for how the
assistant's language is actually chosen.

Setting the global `lang` key is enough on its own. STT, TTS, and plugins follow it
automatically. `ovos-config autoconfigure` can also swap in the recommended plugins and
voices for that language.

Follow the on-screen instructions. Use arrow keys and space to pick.

![Language selection screen listing Dutch, English, French, German, Hindi, Italian, Portuguese, and Spanish as radio-button choices, with English selected](https://gist.github.com/user-attachments/assets/61f9e089-1d54-49e9-8d4a-d5e1f6028ee2)

---

## Environment Summary

An informational screen. No action needed. It reports what the installer auto-detected about the machine, including:

`OS`
:   distribution name and version (e.g. Debian, Ubuntu, macOS)

`Kernel`
:   kernel version string

`Raspberry Pi model`
:   detected board, or `N/A` on non-Pi hardware

`Python`
:   detected Python interpreter version

`CPU capability`
:   whether the CPU supports AVX2/SIMD (affects which speech plugins are offered)

`Sound server`
:   PulseAudio or PipeWire, if detected

`Display server`
:   X11, Wayland, or `EGLFS` (used on Mark II/DevKit), if any

If the board looks like a Mycroft Mark II or DevKit (Raspberry Pi 4 plus the
matching audio/I²C hardware), a confirmation prompt asks you to verify that.
Some generic HATs expose the same signal without being real Mark II hardware.

![Environment summary screen listing the detected OS, kernel, Raspberry Pi model, Python version, AVX/SIMD support, hardware type, virtualenv path, sound server, and display server, with a Next button to continue](https://gist.github.com/user-attachments/assets/1268a703-2007-4bc0-b153-36f33b782b20)

---

## Choose Installation Method

A radio-button list with up to two options:

`virtualenv`
:   Python virtual environment. Recommended for most users. Supported everywhere, including macOS.

`containers`
:   Docker (or Podman) containers. Installed automatically if Docker is missing. **Not offered** on macOS, on 32-bit CPUs, on Raspberry Pi 3, or on Mark II/DevKit hardware. Those are locked to `virtualenv`.

If you're re-running the installer on an existing install, only the method
already in use is offered (you can't switch method in place).

![Installation method screen with a radio-button choice between containers and virtualenv, containers selected](https://gist.github.com/user-attachments/assets/e1b881fc-327d-4e1f-839b-396cffcd354c)

---

## Choose Channel

`testing`
:   Recommended for most users. Generally stable with newer features, but may
    occasionally contain regressions — distinct from the `stable` channel, which
    pins an older snapshot (see [Release Channels](release-channels.md)).

`alpha`
:   Bleeding-edge/pre-release packages. **Required** (and the only option offered) on macOS and on Mark II/DevKit hardware.

![Release channel screen with a single available option, alpha, selected as a radio button](https://gist.github.com/user-attachments/assets/f782cebe-c86b-4474-93d7-894b712e8fe7)

---

## Choose Profile

A radio-button list of installation profiles:

`ovos`
:   The classic, all-in-one experience. Voice pipeline, skills, and (optionally) GUI all run locally. It is the default and the profile the rest of this page assumes.

`satellite`
:   A microphone/speaker endpoint that talks to a separate OVOS core over the network. See [composable deployments](composable-deployments.md). It skips the feature-selection screen (no local skills/GUI/LLM/Home Assistant to configure), but adds four HiveMind connection prompts: host, port, access key, and password.

`listener`
:   A HiveMind Core hub (`hivemind-core listen`) that HiveMind satellites and bots connect
    to. The installer treats `listener` as a desktop profile, so it also runs OVOS's own
    local `ovos-dinkum-listener` service. The `satellite` profile is different: it runs a
    HiveMind satellite client instead and has no local OVOS core or listener at all. See
    [Composable Deployments](composable-deployments.md).

`server`
:   A headless core with no local audio hardware assumptions, meant to serve satellites. It also skips GUI/LLM/Home Assistant options.

![Profile selection screen with four radio-button options — ovos, satellite, listener, server — and ovos selected](https://gist.github.com/user-attachments/assets/0ff4279d-69fa-4ab8-b372-0fef263e6d7c)

---

## Feature Selection

A checklist (only shown for the `ovos`/`listener`/`server` profiles, not `satellite`):

`skills`
:   Install the default OVOS skills. **On** by default.

`extra-skills`
:   Install additional community skills beyond the default set. Off by default.

`gui`
:   Enable the OVOS GUI. Only offered on Mark II/DevKit hardware running Debian Trixie (the check is an exact match on Debian 13, so later Debian releases need an installer update). On those devices it defaults **on**. Not offered on the `server`/`satellite` profiles.

`homeassistant`
:   Enable Home Assistant integration. Prompts for a URL and access token. Only offered for the `ovos`/`listener` profiles with the `virtualenv` or `containers` method.

`llm`
:   Enable an LLM-backed fallback answer via the OVOS Persona pipeline. Prompts for an OpenAI-compatible API URL, key, model, and persona name. Same availability rule as `homeassistant`.

![Feature selection checklist with skills and gui both checked on](https://gist.github.com/user-attachments/assets/bdb65ba6-18d6-42fd-aff6-22fab0826870)

> ⚠️ Note: Some features (like the GUI) may be unavailable on lower-end hardware like the Raspberry Pi 3B+.

---

## Raspberry Pi Tuning *(if applicable)*

On Raspberry Pi boards only, a yes/no prompt offers system performance tweaks
(including an overclock option on supported boards). It's highly recommended
to enable this on a Pi.

![Raspberry Pi tuning prompt with a yes/no choice, yes selected](https://gist.github.com/user-attachments/assets/91bb5f18-9c5a-49ef-a0fe-5b0e52b44ee9)

---

## Summary

Before the installation begins, you'll see a summary of every option you
selected on the previous screens (method, channel, profile, features, tuning).
This is your last chance to cancel the process.

![Summary screen listing the chosen method (virtualenv), version/channel (alpha), profile (ovos), GUI and skills both enabled, and tuning enabled, with a Yes/No confirmation prompt](https://gist.github.com/user-attachments/assets/62a565f3-6871-4dfe-a441-c482199feac0)

---

## Anonymous Telemetry

!!! tip "If you're unsure, decline both"
    Declining both prompts changes nothing about how OVOS works. It only stops these two
    reports from being sent. There is no functional downside to declining.

There are actually **two separate opt-in prompts** here, and they are easy to
mix up. See [Privacy & Security](privacy-security.md#install-time-telemetry-vs-ongoing-usage-telemetry)
for the full explanation. In short, the first ("Telemetry") is a one-time
install report. The second ("Usage Metrics") configures the *installed
assistant* to keep reporting intent-matching data afterwards. It is not
purely a "during setup only" choice.

![Telemetry opt-in prompt explaining what anonymous data collection covers, with a Yes/No choice to accept sharing it](https://gist.github.com/user-attachments/assets/b8015c41-370d-49d3-b783-996887cb421b)

### Install-time telemetry (`share_telemetry`)

This report is generated and sent **once**, right after installation
completes. Nothing else about this specific report is collected afterwards.
Below is the field list. Every one of these is always included in the report
whenever you opt in. None of them is something you type in yourself _(see the
[Ansible task](https://github.com/OpenVoiceOS/ovos-installer/blob/main/ansible/roles/ovos_telemetry/tasks/main.yml) that builds it)_.

In short: system and hardware facts, plus which components you chose during install. No
audio and no personal identifiers are in this report.

| Data                   | Description                                              |
| ---------------------- | -------------------------------------------------------- |
| `architecture`         | CPU architecture where OVOS was installed                |
| `channel`              | `testing` or `alpha` channel of OVOS                     |
| `container`            | OVOS installed into containers                           |
| `country`              | Country the machine appeared to be in, derived from a public-IP geolocation lookup (`ip-api.com`) performed by the installer. Not something you type in |
| `cpu_capable`          | Is the CPU supports AVX2 or SIMD instructions             |
| `display_server`       | Is X or Wayland are used as display server                |
| `extra_skills_feature` | Extra OVOS's skills enabled during the installation        |
| `gui_feature`          | GUI enabled during the installation                        |
| `hardware`             | Is the device a Mark 1, Mark II or DevKit                  |
| `homeassistant_feature`| Home Assistant feature enabled during the installation     |
| `installed_at`         | Date when OVOS has been installed                          |
| `llm_feature`          | LLM feature enabled during the installation                 |
| `os_kernel`            | Kernel version of the host where OVOS is running           |
| `os_name`              | OS name of the host where OVOS is running                  |
| `os_type`              | OS type of the host where OVOS is running                  |
| `os_version`           | OS version of the host where OVOS is running                |
| `profile`              | Which profile has been used during the OVOS installation    |
| `python_version`       | What Python version was running on the host                 |
| `raspberry_pi`         | Does OVOS has been installed on Raspberry Pi                |
| `skills_feature`       | Default OVOS's skills enabled during the installation        |
| `sound_server`         | What PulseAudio or PipeWire used                             |
| `tuning_enabled`       | Whether the Raspberry Pi tuning feature was used              |
| `venv`                 | OVOS installed into a Python virtual environment              |

### Ongoing usage telemetry (`share_usage_telemetry`)

Accepting this prompt adds an `open_data.intent_urls` entry pointing at a
community metrics endpoint to your installed `mycroft.conf`. That makes the
**running assistant** report anonymous intent-matching data on an ongoing
basis. It reports every time it processes a voice command, not just during setup.

If you want data collection to stop once installation is over, decline this
prompt (declining the first, install-time prompt is not enough on its own).
The choice always remains yours, whether made here in the installer or later
by hand editing the `open_data` key in `mycroft.conf`.

---

## Sit Back and Relax

The installation begins. This can take some time. Take a short break while it runs.

Here is a demo of how the process should go if everything works as intended.
The recording shows a full run of the wizard on a fresh machine, from launching
`installer.sh` through the summary screen to the final "installation complete"
message — in order: the language screen, installation method, release channel,
profile, feature selection, Raspberry Pi tuning, the two telemetry prompts, the
summary confirmation, and then the unattended install itself. Each of those screens
is described with a screenshot earlier on this page, so the recording adds pacing,
not information.

[![Terminal recording of the full installer wizard run described above](https://asciinema.org/a/710286.svg)](https://asciinema.org/a/710286)

---
**Read next:** [How to Install Open Voice OS](ovos-installer.md)
**Related:** [Privacy & Security](privacy-security.md) · [Non-interactive scenario install](ovos-installer.md#non-interactive-scenario-install) · [Composable Deployments](composable-deployments.md)
