# RaspOVOS: A Beginner's Guide to Setting Up Your Raspberry Pi with OVOS

!!! abstract "In a nutshell"
    This is a step-by-step guide to turning a Raspberry Pi (a small, inexpensive computer) into a working OVOS voice assistant by flashing a ready-made "raspOVOS" image onto an SD card or USB drive. It walks you through hardware choices, writing the image, first boot, connecting to Wi-Fi, and the handy commands you'll use afterward. raspOVOS is the flagship, turnkey OpenVoiceOS experience for the Raspberry Pi — flash it and boot straight into a working assistant, no manual install steps required. See the [Glossary](glossary.md) for unfamiliar terms.

!!! tip "Turnkey Raspberry Pi image"
    **raspOVOS** is a ready-made, actively maintained image built specifically for the
    Raspberry Pi — the quickest way to get a full OVOS voice assistant running on Pi
    hardware. If you're installing on non-Pi hardware, or want to install onto an
    existing Raspberry Pi OS setup instead of flashing a new image, use the
    **[`ovos-installer`](ovos-installer.md)** instead.

This tutorial is designed for users new to Raspberry Pi and raspOVOS. Follow these steps to set up and optimize your device for the best experience.

---

## Step 1: Prepare Your Hardware

### Raspberry Pi Model Recommendations

- **Recommended:** Raspberry Pi 4 or 5.
    - For offline [STT](stt-plugins.md) (speech-to-text), the **Raspberry Pi 5** offers significant performance improvements.
- **Minimum Requirement:** Raspberry Pi 3.
    - **Note:** The Raspberry Pi 3 will work but may be **extremely slow** compared to newer models.
- **Not supported:** Raspberry Pi Zero (and other boards below the Pi 3) fall under the stated
  minimum — don't expect a usable experience there; start from a Pi 3 or newer.

### Picking a plugin combo for your Pi tier

The Pi model above sets the ceiling on what you can run comfortably. As a starting point per
tier (see [STT Plugins](stt-plugins.md), [TTS Plugins](tts-plugins.md),
[Wake Word Plugins](wake-word-plugins.md) and [VAD Plugins](vad-plugins.md) for the full rosters):

- **Pi 3 (minimum):** lean on cloud services or the lightest local plugins — a small wake-word
  model, an energy/noise VAD, and cloud STT/TTS (or, if you need fully offline, the smallest
  local models you can find). Avoid local Whisper-class STT/TTS here; it is the heaviest option
  in the rosters and this is the board least equipped to run it.

  ```jsonc
  // ~/.config/mycroft/mycroft.conf — Pi 3 / lightweight tier: cloud STT, local energy VAD
  {
    "stt": {
      "module": "ovos-stt-plugin-server",
      "ovos-stt-plugin-server": {
        // without "urls", this plugin silently falls back to public community servers
        "urls": ["http://<your-server-ip>:8080/stt"]
      }
    },
    "listener": {
      "VAD": {
        "module": "ovos-vad-plugin-webrtcvad"
      }
    }
  }
  ```

  See [STT server](stt-server.md) if you want to self-host that server instead of using a
  public one.

- **Pi 4:** a comfortable middle ground for local, on-device models — e.g.
  [`ovos-stt-plugin-onnx-asr`](stt-plugins.md#ovos-stt-plugin-onnx-asr) with a small,
  `int8`-quantized model, and [`ovos-tts-plugin-phoonnx`](tts-plugins.md#ovos-tts-plugin-phoonnx).

  ```jsonc
  // ~/.config/mycroft/mycroft.conf — Pi 4-class tier: local ONNX STT/TTS
  {
    "stt": {
      "module": "ovos-stt-plugin-onnx-asr",
      "ovos-stt-plugin-onnx-asr": {
        "model": "nemo-parakeet-tdt-0.6b-v3",
        "quantization": "int8"
      }
    },
    "tts": {
      "module": "ovos-tts-plugin-phoonnx"
    },
    "listener": {
      "VAD": {
        "module": "ovos-vad-plugin-silero"
      }
    },
    "hotwords": {
      "hey_mycroft": {
        "module": "ovos-ww-plugin-precise-onnx"
      }
    }
  }
  ```

- **Pi 5:** the offline STT performance improvement noted above gives you the most headroom for
  larger local models, including Whisper-class STT, if you want to stay fully offline.

  ```jsonc
  // ~/.config/mycroft/mycroft.conf — Pi 5-class tier: larger local STT model
  {
    "stt": {
      "module": "ovos-stt-plugin-fasterwhisper",
      "ovos-stt-plugin-fasterwhisper": {
        "model": "large-v3",
        "compute_type": "int8"
      }
    },
    "tts": {
      "module": "ovos-tts-plugin-phoonnx"
    },
    "listener": {
      "VAD": {
        "module": "ovos-vad-plugin-silero"
      }
    },
    "hotwords": {
      "hey_mycroft": {
        "module": "ovos-ww-plugin-precise-onnx"
      }
    }
  }
  ```

!!! tip "How to apply these settings"
    To apply these settings, see [Make It Yours](personalize.md) for where `mycroft.conf`
    lives and how to edit it.

### Storage Options

- **SD Card or USB Storage:**
    - You can use either a microSD card or a USB drive.
- **Recommended:** USB SSD Drive for maximum speed and performance.
    - Connect the USB drive to the **blue USB 3.0 port** for optimal performance.

### Power Supply Considerations
Raspberry Pi boards are notoriously **picky about power supplies**. Insufficient power can lead to performance issues, random reboots, or the appearance of the **undervoltage detected** warning (a lightning bolt symbol in the top-right corner of the screen).

- **Recommended Power Supplies:**
    - Raspberry Pi 4: 5V 3A USB-C power adapter.
    - Raspberry Pi 5: Official Raspberry Pi 5 USB-C power adapter or equivalent high-quality adapter with sufficient current capacity.
- **Common Issues:**
    - Using cheap or low-quality chargers or cables may result in voltage drops.
    - Long or thin USB cables can cause resistance, reducing the power delivered to the board.
- **How to Fix:**
    - Always use the official power adapter or a trusted brand with a stable 5V output.
    - If you see the **"undervoltage detected"** warning, consider replacing your power supply or cable.

---

## Step 2: Install RaspOVOS Image

### Download the raspOVOS image

Grab the latest image from the
[raspOVOS Releases page](https://github.com/OpenVoiceOS/raspOVOS/releases). Images are named
`raspOVOS-<lang>-bookworm-arm64-<variant>.img.xz` — pick the one matching your language and one of
three **variants**, which trade on-device processing against the Pi tier you chose in Step 1:

- **`lite`** — delegates both STT and TTS to public OVOS servers with a minimal intent pipeline;
  the lightest option and the one that *might* run on a **Pi 3**.
- **`hybrid`** — runs TTS on-device but still uses public STT servers, with a balanced intent
  pipeline; recommended for a **Pi 4**.
- **`offline`** — runs both STT and TTS on-device with the full intent pipeline; needs at least
  **4 GB RAM (Pi 4/5, 8 GB preferred)**.

So a Pi 3 user should pick `lite`, and a Pi 5 user who wants to stay fully offline should pick
`offline`. (`DEV`-prefixed releases are untranslated base images for developers — skip them.)

1. **Download and Install Raspberry Pi Imager**


    - Visit [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and download the appropriate version for your OS.
    - Install and launch the imager.


2. **Flash the Image to Storage**


    - Insert your SD card or USB drive into your computer.
    - In the Raspberry Pi Imager:
        - **Choose OS:** Select "Use custom" and locate the raspOVOS image file.
        - **Choose Storage:** Select your SD card or USB drive.


![Raspberry Pi Imager "Choose Device" screen listing supported Pi models](https://github.com/user-attachments/assets/92458289-a3c3-4c7b-afc8-126881445f9f)

![Raspberry Pi Imager "Choose OS" screen with "Use custom" selected to pick the raspOVOS image file](https://github.com/user-attachments/assets/36a83d0a-ebc2-4095-94ba-604ad78b5452)

![Raspberry Pi Imager "Choose Storage" screen listing the target SD card or USB drive](https://github.com/user-attachments/assets/47c92497-d1a2-4f2d-90be-189806736c0d)

3. **Advanced Configuration Options**


    - Click **Next** and select **Edit Settings** to customize settings, including:
        - **Password:** Change the default password.
        - **Hostname:** Set a custom hostname for your device.
        - **Wi-Fi Credentials:** Enter your Wi-Fi network name and password.
        - **Keyboard Layout:** Configure the correct layout for your region.

   **Important:** **Do NOT change the default username** (`ovos`), as it is required for the system to function properly.

![Raspberry Pi Imager "Edit Settings" general tab: hostname, username, password, and Wi-Fi fields](https://github.com/user-attachments/assets/9509ea57-ae46-4c0b-b9e9-97935579d207)

![Raspberry Pi Imager "Edit Settings" services/locale tab: SSH and keyboard layout options](https://github.com/user-attachments/assets/252af1a0-54dc-4450-aa4a-eb0f0a4d139f)

4. **Write the Image**


    - Click **Save** and then **Yes** to flash the image onto your storage device.
    - Once complete, safely remove the SD card or USB drive from your computer.

---

## Step 3: Initial Setup and First Boot

### Connect and Power On

- Insert the SD card or connect the USB drive to your Raspberry Pi.
- Plug in the power supply and connect an HDMI monitor to observe the boot process.

### First Boot Process

1. **Initialization:**


    - The system will expand the filesystem, generate SSH keys, and perform other setups.


2. **Reboots:**


    - The device will reboot **up to three times** during this process.


3. **Autologin:**


    - The `ovos` user will automatically log in to the terminal after boot. This is a
      text-only command screen, not a graphical desktop — see [Make It Yours](personalize.md)
      and [It's Not Working — Quick Fixes](everyday-help.md) for the basics of using it.


4. **Check System Status:**


    - Use the `ologs` command to monitor logs and confirm that the system has fully initialized.

---

## Step 4: Setting Up Wi-Fi

### Option 1 (recommended): Configure Wi-Fi Using Raspberry Pi Imager
The most straightforward and reliable method is to set up Wi-Fi during the imaging
process, in Step 2 above — use this whenever you have a computer to flash the image
with.

1. Open Raspberry Pi Imager and select Edit Settings Option.


2. Enter your **SSID (Wi-Fi network name)** and **password** in the Wi-Fi configuration fields.


3. Write the image to your SD card or USB drive, and your Wi-Fi will be pre-configured.

### Option 2 (fallback, work-in-progress): Audio-Based Wi-Fi Setup (ggwave)

Use this only if you didn't set Wi-Fi credentials at imaging time and have no other way
to reach the device (no monitor/keyboard, no Ethernet). It is a work in progress and
gives no on-screen confirmation, so treat it as a fallback, not the primary path.

1. Open [ggwave Wi-Fi setup](https://openvoiceos.github.io/ovos-audio-transformer-plugin-ggwave/) on a device with speakers.


2. Enter your **SSID** and **password** and transmit the data as sound.


3. Place the transmitting device near the Raspberry Pi microphone.


4. If successful, the **raspOVOS device** (not the transmitting phone/laptop) plays an acknowledgment tone.


    - If decoding fails or credentials are incorrect, the raspOVOS device plays an error tone instead.

🚧 **Note:** ggwave is a **work-in-progress** feature and does not have any dialogs or provide on-screen feedback. 🚧

![ggwave Wi-Fi setup web page with SSID/password fields and a "transmit" button](https://github.com/user-attachments/assets/ce2857b1-b93f-4092-99f3-43f555e04920)

---

## Step 5: Running OVOS

### OVOS First Launch

- On the first run, OVOS may take longer to initialize.
- A working Internet connection is required for OVOS to consider itself ready and
  announce it out loud — if Wi-Fi isn't configured yet or the network is unreachable,
  the device stays silent instead. Check `ovos-status` and the `ologs` output (see
  below) to confirm the services actually started even without a spoken confirmation,
  and see [raspOVOS Troubleshooting](raspovos-troubleshooting.md#ovos-fails-to-speak-i-am-ready)
  if it never speaks up once online.

---

## Step 6: Using OVOS Commands

### Helpful Commands

When you log in, raspOVOS prints a welcome banner listing its built-in helper commands. These
are **raspOVOS-specific shell helpers** (aliases and small scripts baked into the image) — they
are part of the raspOVOS image, not a standard `pip install` of OVOS. Run `ovos-help` at any time
to reprint the full list.

**Web interfaces:**

- `ovos-yaml-editor` — web editor for OVOS configuration (port 9210).
- `ovos-skill-config-tool` — web editor for individual skill settings (port 8000).

**Talking to OVOS:**

- `ovos-config` — manage your local OVOS configuration files.
- `ovos-listen` — activate the microphone to listen for a command.
- `ovos-speak <phrase>` — have OVOS speak a phrase to the user.
- `ovos-say-to <phrase>` — send an utterance to OVOS as if you had spoken it.
- `ovos-simple-cli` — chat with your device from the terminal.
- `ovos-docs-viewer` — open the documentation viewer (also `ovos-manual`, `ovos-skills-info`).

**Managing packages:**

- `ovos-install` — install OVOS packages with the correct version constraints.
- `ovos-update` — update all OVOS and skill packages.
- `ovos-force-reinstall` — force a full reinstall of all OVOS packages (last-resort repair).
- `ovos-freeze` — export installed OVOS packages to `requirements.txt`.
- `ovos-outdated` — list outdated OVOS/skill packages.
- `ovos-reset-brain` — reset the "OVOS brain" to a blank state by uninstalling all skills.

**Inspecting plugins:**

- `ls-skills` — list the `skill_id` of every installed skill.
- `ls-stt` / `ls-tts` / `ls-ww` / `ls-tx` — list installed [STT](stt-plugins.md) / [TTS](tts-plugins.md) / wake-word / [translation](translation-plugins.md) plugins.

**Sound/audio:**

- `ovos-audio-diagnostics` — print the active sound server, sinks, and default output device.
- `ovos-audio-setup` — interactive audio configuration menu (handy after wiring up a HAT).

**Logs and status:**

- `ologs` — view all logs in real time.
- `ovos-logs [COMMAND] --help` — a small tool to help navigate the logs.
- `ovos-status` — list OVOS-related systemd services.
- `ovos-restart` — restart all OVOS-related systemd services.
- `ovos-server-status` — check the live status of the public OVOS servers.

**Misc:**

- `ovos-commands` — usage examples for the installed skills.
- `ovos-support` — compile logs into a support package to share when asking for help.
- `ovos-help` — reprint this command list.

!!! note "Audio HAT setup on raspOVOS uses `ovos-i2csound`"
    On raspOVOS, an i2c sound HAT (such as a Respeaker or the Mark 2's SJ201) is detected and
    configured at boot by the **`ovos-i2csound`** service shipped in the image, which writes the
    detected board to `/etc/OpenVoiceOS/i2c_platform`. This is specific to the raspOVOS image —
    the [ovos-installer](ovos-installer.md) does **not** use it (see
    [Mark 2 Hardware](mark2.md) for the installer's kernel-driver approach).

### Check Logs in Real-Time

- Use the `ologs` command to monitor logs live on your screen.
- If you're unsure whether the system has finished booting, check logs using this command.

---

Enjoy your journey with raspOVOS! With your Raspberry Pi set up, you can start exploring all the features of OpenVoiceOS.

---

## Now try it

Your device is up and listening. Two places to go next:

- **[What can I say?](skill-examples.md)** — a catalog of things you can actually say to it, organized by what's installed.
- **[Fun stuff to try](showcase.md)** — a curated list of fun and impressive things to show off once the basics work.

---

*Source code: [OpenVoiceOS/raspOVOS](https://github.com/OpenVoiceOS/raspOVOS).*
