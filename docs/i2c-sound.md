# i2c Sound & Audio Setup

!!! abstract "In a nutshell"
    Many Raspberry Pi voice devices use an add-on **sound board (a "HAT")** for their microphones
    and speaker, such as the [Mark 2](mark2.md)'s SJ201 or a Respeaker. Before OVOS can hear or
    speak, that board has to be **detected**, given the **right driver**, and wired into the
    system's **audio config**. This page covers the small OVOS tools that do that on the
    [raspOVOS](install-raspovos.md) image. The [ovos-installer](ovos-installer.md) handles the
    Mark 2 differently. See [Mark 2 Hardware](mark2.md) and the [Glossary](glossary.md) for terms.

Raspberry Pi sound HATs sit on the **i2c bus** and need three things before audio works. The
board must be **identified**, the correct **kernel driver / ALSA settings** applied, and the
system's **audio routing** (sound server, default device, volume) configured. OVOS splits this
across a few focused tools, used mainly by the [raspOVOS](install-raspovos.md) image.

!!! info "Two different hardware paths"
    The tools on this page are the **raspOVOS image** path. The ansible
    [ovos-installer](ovos-installer.md) does **not** use them for the [Mark 2](mark2.md). It
    builds the [`VocalFusionDriver`](mark2.md#the-ovos-kernel-driver-vocalfusiondriver) kernel
    module instead. Pick the path that matches how you installed OVOS.

---

## `ovos-i2c-detection`: identify the board

[`OpenVoiceOS/ovos-i2c-detection`](https://github.com/OpenVoiceOS/ovos-i2c-detection) is a small
set of scripts that probe the i2c bus and answer "what board is this?" It exposes checks such
as:

- `is_sj201_v6`: Mycroft SJ201 **dev kit** board (revision 6)
- `is_sj201_v10`: SJ201 **production** board (revision 10)
- `is_texas_tas5806`: the TAS5806 amplifier (used to confirm an SJ201 v10)
- `is_wm8960`: WM8960-based HATs such as the ReSpeaker 2-mic (i2c `0x1a`). Adafruit's 2-mic Voice Bonnet is detected separately by `is_adafruit_amp` (i2c `0x4b`)

This is the primitive that tells the [Mark 2](mark2.md) dev kit apart from the retail unit, and
it is used by the detection and configuration tools below.

## `ovos-i2csound`: detect and configure at boot

[`OpenVoiceOS/ovos-i2csound`](https://github.com/OpenVoiceOS/ovos-i2csound) is a shell script
plus a systemd service (`i2csound.service`) that runs at boot. It **auto-detects the attached
i2c sound HAT and configures ALSA** for it. It writes the detected board name to
**`/etc/OpenVoiceOS/i2c_platform`**, a marker other components read to know what hardware they
are on. An absent file means no supported card was found. It supports the SJ201 and a range of
Respeaker-style HATs, and is the piece that "makes the microphone and speaker exist" on a
raspOVOS image.

Install is a one-time `sudo ./install.sh` on apt-based systems, followed by a reboot. On a
raspOVOS image it is already baked in.

!!! tip "You should see"
    `install.sh` finishes by printing:

    ```text
    Installation complete. Please reboot your system to apply changes.
    ```

    After the reboot, confirm detection worked by reading the marker file it writes:

    ```bash
    cat /etc/OpenVoiceOS/i2c_platform
    ```

    A supported board's name (e.g. `SJ201V6`) means detection succeeded. If the file does not
    exist, `ovos-i2csound` ran but did not find a supported sound card.

## `raspovos-audio-setup`: manage the audio configuration

[`OpenVoiceOS/raspovos-audio-setup`](https://github.com/OpenVoiceOS/raspovos-audio-setup) is the
ongoing **audio-configuration** layer (scripts and systemd services) that sits above detection.
Where `ovos-i2csound` brings the card up, `raspovos-audio-setup` keeps audio working as things
change:

- Set the default soundcard, combine audio sinks, and manage USB-soundcard volume.
- Survive hardware changes, such as plugging in a USB soundcard live or moving the SD card to
  different hardware.
- Expose more complex setups, such as echo cancellation, in a friendlier way.
- Work across `alsa`, `pipewire`, or `pulseaudio`, and even on non-OVOS Raspberry Pi images.

End users normally interact with just one entry point: **`ovos-audio-setup`**, an interactive
menu (installed to `/usr/local/bin`) to pick the default soundcard, enable or disable the
automation, and revert changes. It is also scriptable. `ovos-audio-setup <choice>` runs a menu
option directly. The other scripts (`soundcard-autoconfigure`, `combine-sinks`,
`usb-autovolume`) are not run by hand. Systemd units and udev rules drive them automatically on
boot and USB sound events.

When picking the default output, `soundcard-autoconfigure` follows a **fixed priority order**:

1. the `ovos-i2csound` hint in `/etc/OpenVoiceOS/i2c_platform` (the marker described above), if it
   names a known platform
2. **USB** soundcard
3. user-installed **HAT**
4. onboard **headphones** (`bcm2835`, not present on Pi 5)
5. **HDMI** (`vc4-hdmi`), as a last resort

!!! tip "Debugging no-audio devices"
    Each tool writes a log to `/tmp`, the first place to look when a device has no sound:

    - `/tmp/autosoundcard.log`: soundcard autoconfiguration
    - `/tmp/autovolume-usb.log`: USB volume udev events
    - `/tmp/autosink.log`: combined sink creation

!!! note "Alpha"
    `raspovos-audio-setup` is an alpha-stage project. It is useful, but still stabilizing.

## `ovos-tools`: raspOVOS shell helpers

[`OpenVoiceOS/ovos-tools`](https://github.com/OpenVoiceOS/ovos-tools) is a set of helper bash
utilities used by [raspOVOS](install-raspovos.md) and usable on other Linux systems. It
includes some of the audio and diagnostic helpers exposed by the image's
[command set](raspovos-commands-reference.md#helpful-commands).

---

*Source code: [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound), [OpenVoiceOS/ovos-i2c-detection](https://github.com/OpenVoiceOS/ovos-i2c-detection), [OpenVoiceOS/raspovos-audio-setup](https://github.com/OpenVoiceOS/raspovos-audio-setup).*

---
**Read next:** [Mark 1 Hardware](mark1.md)
**Related:** [Mark 2 Hardware](mark2.md) · [raspOVOS image](install-raspovos.md) · [PHAL](phal.md) · [Hardware Integrators](hardware-integrators.md)
