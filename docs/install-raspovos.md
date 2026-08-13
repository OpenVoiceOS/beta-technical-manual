# RaspOVOS: A Beginner's Guide to Setting Up Your Raspberry Pi with OVOS

!!! abstract "In a nutshell"
    This is a step-by-step guide to turning a Raspberry Pi (a small, inexpensive computer) into a working OVOS voice assistant by flashing a ready-made "raspOVOS" image onto an SD card or USB drive. It walks you through hardware choices, writing the image, first boot, connecting to Wi-Fi, and the handy commands you'll use afterward. raspOVOS is a ready-made OpenVoiceOS image for the Raspberry Pi: flash it and boot into a working assistant. Read the status warning below before choosing it for a new setup. See the [Glossary](glossary.md) for unfamiliar terms.

!!! warning "Project status: stable images paused, development active"
    The last **stable** raspOVOS images date from mid-2025 and are not receiving updates,
    so they are not the recommended install path for a new setup. The repository itself is
    actively developed — CI work continues and newer **DEV** images appear on the
    [releases page](https://github.com/OpenVoiceOS/raspOVOS/releases) — but DEV images are
    untested builds toward the refreshed image on the roadmap, not something to hand a
    newcomer. Check the repository for status before flashing. For a supported setup on a
    Raspberry Pi, install Raspberry Pi OS and use the [ovos-installer](ovos-installer.md).
    This guide stays for people running an existing raspOVOS image.

This tutorial is designed for users new to Raspberry Pi and raspOVOS. Follow these steps to set up your device.

---

## Step 1: Prepare Your Hardware

### Raspberry Pi Model Recommendations

- **Recommended:** Raspberry Pi 4 or 5.
    - For offline [STT](stt-plugins.md) (speech-to-text), the **Raspberry Pi 5** offers significant performance improvements.
- **Minimum Requirement:** Raspberry Pi 3.
    - **Note:** The Raspberry Pi 3 will work but may be **extremely slow** compared to newer models.
- **Not supported:** Raspberry Pi Zero (and other boards below the Pi 3) fall under the stated
  minimum. Don't expect a usable experience there. Start from a Pi 3 or newer.

### Picking a plugin combo for your Pi tier

!!! tip "You can skip this section on a first read"
    The image ships with working defaults for your Pi. Come back here later if you want
    to swap the speech engines. The config blocks below are optional tuning, not setup
    steps.

The Pi model above sets the ceiling on what you can run comfortably. As a starting point per
tier (see [STT Plugins](stt-plugins.md), [TTS Plugins](tts-plugins.md),
[Wake-word Plugins](wake-word-plugins.md) and [VAD Plugins](vad-plugins.md) for the full rosters):

- **Pi 3 (minimum):** lean on cloud services or the lightest local plugins: a small wake word
  model, an energy/noise VAD, and cloud STT/TTS. If you need fully offline, use the smallest
  local models you can find. Avoid local Whisper-class STT/TTS here. It is the heaviest option
  in the rosters, and this is the board least equipped to run it.

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

- **Pi 4:** a comfortable middle ground for local, on-device models. The `hybrid` and `offline`
  raspOVOS images actually ship [`ovos-tts-plugin-piper`](tts-plugins-reference.md#ovos-tts-plugin-piper)
  as the default TTS for this tier, and this is what the config below uses. Note the shipped
  default lags the current recommendation: the piper plugin is archived/deprecated in the
  [TTS catalog](tts-plugins.md), with [`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx)
  as its maintained successor — the images predate that transition. The shipped piper still
  works; phoonnx is the swap to make if you install anything yourself.

  ```jsonc
  // ~/.config/mycroft/mycroft.conf — Pi 4-class tier: local ONNX STT, shipped Piper TTS
  {
    "stt": {
      "module": "ovos-stt-plugin-onnx-asr",
      "ovos-stt-plugin-onnx-asr": {
        "model": "nemo-parakeet-tdt-0.6b-v3",
        "quantization": "int8"
      }
    },
    "tts": {
      "module": "ovos-tts-plugin-piper"
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
  larger local models, including Whisper-class STT, if you want to stay fully offline. The
  `offline` raspOVOS image actually ships
  [`ovos-stt-plugin-citrinet`](stt-plugins-reference.md#ovos-stt-plugin-citrinet) as the default STT (with
  `ovos-stt-plugin-fasterwhisper` shipped only for a few languages), and
  [`ovos-tts-plugin-piper`](tts-plugins-reference.md#ovos-tts-plugin-piper) as the default TTS. The config
  below uses those shipped defaults. Optional swaps, not what ships by default, are
  `ovos-stt-plugin-fasterwhisper` (a larger, more accurate Whisper-class model, if your language
  isn't one of the ones it already ships for) and `ovos-tts-plugin-phoonnx`.

  ```jsonc
  // ~/.config/mycroft/mycroft.conf — Pi 5-class tier: shipped Citrinet STT, Piper TTS
  {
    "stt": {
      "module": "ovos-stt-plugin-citrinet"
    },
    "tts": {
      "module": "ovos-tts-plugin-piper"
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

!!! note "What each variant actually ships"
    These are starting-point configs, not a description of the exact image running on your
    Pi. The `hybrid`/`offline` raspOVOS images ship `ovos-tts-plugin-piper` for TTS, and the
    `offline` image ships `ovos-stt-plugin-citrinet` for STT (`ovos-stt-plugin-fasterwhisper`
    only for a handful of languages). The plugins above are all valid choices you can opt into,
    but if you expect the running image to already match one of these snippets exactly, check
    what actually shipped first.

!!! tip "How to apply these settings"
    To apply these settings, see [Make It Yours](personalize.md) for where `mycroft.conf`
    lives and how to edit it.

### Storage Options

- **SD Card or USB Storage:**
    - You can use either a microSD card or a USB drive.
- **Recommended:** USB SSD Drive for maximum speed and performance.
    - Connect the USB drive to the **blue USB 3.0 port** for optimal performance.

### Power Supply Considerations
Raspberry Pi boards are **picky about power supplies**. Insufficient power can cause performance issues, random reboots, or the **undervoltage detected** warning (a lightning bolt symbol in the top-right corner of the screen).

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

Get the latest image from the
[raspOVOS Releases page](https://github.com/OpenVoiceOS/raspOVOS/releases). Images are named
`raspOVOS-<lang>-bookworm-arm64-<variant>.img.xz`. Pick the one matching your language and one
of three **variants**, which trade on-device processing against the Pi tier you chose in Step 1:

- **`lite`**: delegates both STT and TTS to public OVOS servers with a minimal intent pipeline.
  It is the lightest option and the one that *might* run on a **Pi 3**.
- **`hybrid`**: runs TTS on-device but still uses public STT servers, with a balanced intent
  pipeline. Recommended for a **Pi 4**.
- **`offline`**: runs both STT and TTS on-device with the full intent pipeline. Needs at least
  **4 GB RAM (Pi 4/5, 8 GB preferred)**.

A Pi 3 user should pick `lite`. A Pi 5 user who wants to stay fully offline should pick
`offline`. `DEV`-prefixed releases are untranslated base images for developers. Skip them.

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

!!! warning "Keep the default username, change the password"
    **Do NOT change the default username** (`ovos`). The system requires it to function
    properly.

    **If you skip this step**, the image boots with its stock credentials: username `ovos`,
    password `ovos`, hostname `raspOVOS`. These are published defaults, so the device is
    reachable over SSH by anyone on the network who knows them. Set a real password here, or
    change it at first boot, if the device will be reachable on a network you don't fully trust.

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
      text-only command screen, not a graphical desktop. See [Make It Yours](personalize.md)
      and [It's Not Working: Quick Fixes](everyday-help.md) for the basics of using it.

4. **Check System Status:**

    - Use the `ologs` command to monitor logs and confirm that the system has fully initialized.
      Note that `ologs` excludes `bus.log`, so if the device never speaks and `ologs` shows
      nothing useful, tail the messagebus log too: `tail -f ~/.local/state/mycroft/bus.log`.

---

## Step 4: Setting Up Wi-Fi

### Option 1 (recommended): Configure Wi-Fi Using Raspberry Pi Imager
The most reliable method is to set up Wi-Fi during the imaging process, in Step 2 above.
Use this whenever you have a computer to flash the image with.

1. Open Raspberry Pi Imager and select Edit Settings Option.

2. Enter your **SSID (Wi-Fi network name)** and **password** in the Wi-Fi configuration fields.

3. Write the image to your SD card or USB drive, and your Wi-Fi will be pre-configured.

### Option 2 (fallback, work-in-progress): Audio-Based Wi-Fi Setup (ggwave)

Use this only if you didn't set Wi-Fi credentials at imaging time and have no other way
to reach the device (no monitor/keyboard, no Ethernet). It is a work in progress and gives
no on-screen confirmation. Treat it as a fallback, not the primary path.

1. Open [ggwave Wi-Fi setup](https://openvoiceos.github.io/ovos-audio-transformer-plugin-ggwave/) on a device with speakers.

2. Enter your **SSID** and **password** and transmit the data as sound.

3. Place the transmitting device near the Raspberry Pi microphone.

4. If successful, the **raspOVOS device** (not the transmitting phone/laptop) plays an acknowledgment tone.

    - If decoding fails or credentials are incorrect, the raspOVOS device plays an error tone instead.

**Note:** ggwave is a **work-in-progress** feature. It does not show dialogs or give on-screen feedback.

![ggwave Wi-Fi setup web page with SSID/password fields and a "transmit" button](https://github.com/user-attachments/assets/ce2857b1-b93f-4092-99f3-43f555e04920)

---

## Step 5: Running OVOS

### OVOS First Launch

- On the first run, OVOS may take longer to initialize.
- A working Internet connection is required for OVOS to consider itself ready and
  announce it out loud. If Wi-Fi isn't configured yet or the network is unreachable,
  the device stays silent instead. Check `ovos-status` and the `ologs` output (see
  below) to confirm the services actually started, even without a spoken confirmation.
  See [raspOVOS Troubleshooting](raspovos-troubleshooting.md#ovos-fails-to-speak-i-am-ready), "OVOS Fails to Speak
  'I am Ready'", if it never speaks up once online.

---

## Step 6: Using OVOS Commands

When you log in, raspOVOS prints a welcome banner listing its built-in helper commands. These
are **raspOVOS-specific shell helpers** (aliases and small scripts baked into the image). They
are part of the raspOVOS image, not a standard `pip install` of OVOS. Run `ovos-help` at any
time to reprint the full list, and see the [RaspOVOS Commands Reference](raspovos-commands-reference.md)
for the complete list — including web interfaces, package management, plugin inspection, and log
commands like `ologs` for checking logs in real time.

---

With your Raspberry Pi set up, you can start exploring the features of OpenVoiceOS.

---

## Now try it

Your device is up and listening. Two places to go next:

- **[What can I say?](skill-examples.md)**: a catalog of things you can actually say to it, organized by what's installed.
- **[Fun stuff to try](showcase.md)**: a list of fun things to show off once the basics work.

---

*Source code: [OpenVoiceOS/raspOVOS](https://github.com/OpenVoiceOS/raspOVOS).*

---

**Read next:** [What can I say?](skill-examples.md) · [Fun stuff to try](showcase.md)
**Related:** [ovos-installer](ovos-installer.md) · [RaspOVOS Troubleshooting](raspovos-troubleshooting.md) · [Make it yours](personalize.md) · [Coming from Mycroft](coming-from-mycroft.md)
