# Utilities Skills

!!! abstract "In a nutshell"
    These skills control system settings and voice-driven maintenance tasks: volume, network
    info, speed tests, boot status, dictation, audio recording, and shell commands.

## Utilities (System & Voice Control)

### Volume

**Installer default**

Control the volume of OVOS with verbal commands.

**Usage examples:**

- unmute volume
- volume low
- mute audio
- volume to high level
- reset volume

- volume to high
- volume level low
- toggle audio
- low volume
- set volume to maximum

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-volume](https://github.com/OpenVoiceOS/ovos-skill-volume) · `pip install ovos-skill-volume` · Maturity: Stable

### IP Address

**Installer default**

Network connection information.

**Usage examples:**

- What's your IP address?
- What's your network address?
- Tell me your network address
- What network are you connected to?
- Tell me your IP address

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-ip](https://github.com/OpenVoiceOS/ovos-skill-ip) · `pip install ovos-skill-ip` · Maturity: Stable

### Speedtest

**Installer default**

Runs an internet bandwidth test using speedtest.net.

**Usage examples:**

- run a speedtest

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-speedtest](https://github.com/OpenVoiceOS/ovos-skill-speedtest) · `pip install ovos-skill-speedtest` · Maturity: Stable

### Boot Finished

**Installer default**

Provides notifications when OpenVoiceOS has fully started and all core services are ready. It
listens for the `mycroft.ready` bus event (emitted once every core service reports ready) and
speaks a short confirmation. This is useful on headless devices where you cannot otherwise tell startup
finished.

**Usage examples:**

- Disable ready notifications.
- Is the system ready?
- Enable ready notifications.

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-boot-finished](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) · `pip install ovos-skill-boot-finished` · Maturity: Stable

### Dictation

**Installer default**

Continuously transcribes user speech to a text file while enabled.

**Usage examples:**

- start dictation
- end dictation

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-dictation](https://github.com/OpenVoiceOS/ovos-skill-dictation) · `pip install ovos-skill-dictation` · Maturity: Stable

### Audio Recording

**Installer default**

Record and manage audio clips directly from your assistant.

**Usage examples:**

- new recording named {name}
- start recording
- start a recording called {name}
- start a new audio recording called {name}
- begin recording

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-audio-recording](https://github.com/OpenVoiceOS/ovos-skill-audio-recording) · `pip install ovos-skill-audio-recording` · Maturity: Stable

### Commands

**Manual install only**

Allows you to execute shell scripts and system commands via voice. Useful for headless boxes
where you want a voice shortcut to a maintenance script instead of SSHing in.

**Usage examples:**

- run script ___
- launch command ___

The blank is a phrase you define yourself: the skill matches nothing by voice until you map
at least one spoken phrase to a script or command under `alias` in its `settings.json`. With
an alias named `generate report`, "run script generate report" runs the mapped command.

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-cmd](https://github.com/OpenVoiceOS/ovos-skill-cmd) · `pip install ovos-skill-cmd` · Maturity: Stable

---

**Read next:** [Skill Examples](skill-examples.md)
**Related:** [Alerts & Time](skill-examples-alerts-time.md) · [It's not behaving](everyday-help.md) · [Your First Skill](first-skill.md)
