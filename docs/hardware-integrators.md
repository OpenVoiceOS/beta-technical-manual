# Building Hardware on OVOS

!!! abstract "In a nutshell"
    You may want to build a physical device, such as a smart speaker, a robot, or a custom
    kiosk, that listens and talks using OVOS. Most of the software underneath does not care
    what board you run it on. The part that does care about hardware is a small layer called
    [PHAL](phal.md) (Platform/Hardware Abstraction Layer). PHAL is also where you plug in
    your own LEDs, buttons, and sensors. This page maps what is generic and what is
    Raspberry-Pi-specific. It shows how to write a driver for your own LED ring or button
    panel, what resources your device needs, and what OVOS does and does not do for
    over-the-air updates and on-screen UI.

---

## SBC-agnostic vs Raspberry-Pi-only

Most of the OVOS stack is just Python talking to ALSA (Linux's standard sound system) and the
network. It runs the same way on a Raspberry Pi, an x86 mini-PC, an Orange Pi, or a laptop. A
few pieces are tied to specific Raspberry-Pi/Mycroft hardware:

| Component | Portability | Why |
|---|---|---|
| `ovos-messagebus`, `ovos-core`, `ovos-audio`, `ovos-dinkum-listener`, `ovos-PHAL`, skills | **Any Linux SBC / PC** | Pure Python + ALSA + network; no board-specific code |
| Wake word / STT / TTS / VAD plugins | **Any Linux SBC / PC** | CPU (or GPU) inference; heavier models just need more RAM/CPU. For concrete sizing, use the [Raspberry Pi tiers](install-raspovos.md#step-1-prepare-your-hardware) as a baseline: a Pi 3-class board handles wake word locally with cloud speech (or only the very smallest local models), Pi 4-class (4 GB) runs local ONNX STT/TTS comfortably, Pi 5-class adds headroom for Whisper-class models |
| [`ovos-i2csound`](i2c-sound.md) | **Raspberry Pi (i2c HATs)** | Auto-detects and configures i2c sound HATs specific to the Pi's i2c bus layout |
| [`VocalFusionDriver`](mark2.md#the-ovos-kernel-driver-vocalfusiondriver) | **Raspberry Pi (SJ201/Mark 2 hardware)** | Out-of-tree kernel module + device-tree overlays for the XMOS VocalFusion DSP mic array |
| [`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1), [`ovos-PHAL-plugin-mk2-v6-fan-control`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk2-v6-fan-control) | **Mycroft Mark 1 / Mark 2 only** | Drive specific hardware that only exists on those boards |
| [raspOVOS](install-raspovos.md) image | **Raspberry Pi only** | It's a Raspberry Pi OS image |

If you are designing new hardware, use a generic microphone or ALSA sound card and a plain
Linux install. The [`ovos-installer`](ovos-installer.md) works the same way on a Pi or an
x86 box. Only reach for the Pi-specific pieces above if you reuse an i2c HAT or the SJ201
board design.

---

## Writing your own hardware driver: `AbstractLed` / `AbstractSwitches`

`ovos-hardware-helpers` also ships an `AbstractFan` base (covered below) for
fan-speed and thermal-shutdown control.

!!! note "Illustrative skeletons"
    The `MyRingLed` and switch examples below are skeletons, not complete, copy-pasteable
    drivers. Real hardware needs the actual bus, SPI, or GPIO calls for your board filled in
    where the example stops short.

Custom LEDs and buttons are the two things almost every maker adds. Instead of writing your
own bus-message plumbing, subclass the abstract base classes in
[`ovos-hardware-helpers`](https://github.com/OpenVoiceOS/ovos-hardware-helpers). Wrap the
result in a [PHAL plugin](phal-authoring.md). See that page for the entry-point
and validator mechanics. This section covers the hardware interface itself.

### LEDs: `AbstractLed`

```python
from ovos_hardware_helpers.led import AbstractLed


class MyRingLed(AbstractLed):
    """Minimal LED ring driver — replace set_led/fill/show with real hardware calls."""

    def __init__(self, num_leds: int = 12):
        self._num_leds = num_leds
        self._state = [(0, 0, 0)] * num_leds

    @property
    def num_leds(self) -> int:
        return self._num_leds

    @property
    def capabilities(self) -> dict:
        return {"num_leds": self._num_leds, "brightness_control": True}

    def set_led(self, led_idx: int, color: tuple, immediate: bool = True):
        self._state[led_idx] = color
        if immediate:
            self.show()

    def fill(self, color: tuple):
        self._state = [color] * self._num_leds
        self.show()

    def show(self):
        # Push self._state to real hardware here (SPI/I2C/GPIO write).
        pass

    def shutdown(self):
        self.fill((0, 0, 0))
```

For a full, real-hardware reference implementation, see
[`ovos-PHAL-plugin-dotstar`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-dotstar). It wraps
a DotStar (APA102) LED strip's SPI driver in an `AbstractLed` subclass, plus the surrounding
PHAL plugin and validator boilerplate. It still imports `AbstractLed` from the deprecated
`ovos_plugin_manager.hardware.led` compat path (the same class, re-exported) rather than
`ovos_hardware_helpers.led` shown above — import from `ovos_hardware_helpers.led` in new
drivers to avoid the deprecation warning.

`AbstractLed` also ships a `scale_brightness(color_val, bright_val)` static helper for dimming.
The library's `eval_color()` helper (in `ovos_hardware_helpers.led`) turns a color name, hex
string, or RGB tuple into a normalized color object using
[`ovos-color-parser`](color-parser.md). This lets your plugin accept `"Mycroft blue"` as well
as `(0, 168, 255)`.

### Buttons: `AbstractSwitches`

```python
from ovos_hardware_helpers.switches import AbstractSwitches


class MyButtonPanel(AbstractSwitches):
    @property
    def capabilities(self) -> dict:
        return {"volume": True, "mute": True, "action": True}

    def on_action(self):
        pass  # e.g. bus.emit(Message("mycroft.mic.listen"))

    def on_vol_up(self):
        pass

    def on_vol_down(self):
        pass

    def on_mute(self):
        pass

    def on_unmute(self):
        pass

    def shutdown(self):
        pass
```

### Fans: `AbstractFan`

```python
from ovos_hardware_helpers.fan import AbstractFan


class MyFanController(AbstractFan):
    def set_fan_speed(self, percent: int):
        pass  # drive a PWM pin, 0-100

    def get_fan_speed(self) -> int:
        return 0  # last commanded 0-100 speed

    def get_cpu_temp(self) -> float:
        return -1.0  # celsius, or -1.0 if not available

    def shutdown(self):
        pass  # set the fan to a reasonable speed before exit
```

Wire an instance of any of these classes up inside a `PHALPlugin.__init__`. Poll your GPIO or
i2c hardware on a background thread, or drive it from an interrupt callback, and call the
matching `on_*`, `set_led`, or `set_fan_speed` methods. See
[PHAL: Writing PHAL Plugins](phal-authoring.md) for the full plugin lifecycle,
validator, and entry-point registration.

---

## Resource footprint

There is no published, current benchmark of OVOS's CPU/RAM footprint across hardware targets.
Treat any specific number you see elsewhere with suspicion. The real cost depends entirely on
which STT, TTS, and wake-word plugins you pick. As a sizing anchor, the
[raspOVOS images](install-raspovos.md) run the full stack with cloud speech on a Pi 3
(barely), cloud STT with on-device TTS on a Pi 4, and fully on-device speech (local STT
and TTS) on a Pi 4/5 with 4 GB+ RAM — those tiers are the closest thing to a documented
reference deployment. A tiny wake-word model and a cloud STT server
cost almost nothing locally. A local Whisper model needs real CPU or a GPU. Measure the
footprint on your own target hardware instead of relying on an unverified number:

```bash
# Memory: sum RSS of every OVOS process
ps -u ovos -o rss,comm --sort=-rss | grep -E 'ovos|mycroft'

# Or per systemd unit, if using the units above
systemctl --user status ovos-skills.service | grep Memory

# CPU, live, while you talk to it
top -b -n 1 -u ovos
```

Run the same commands idle and mid-conversation. The delta tells you what your wake word, STT,
and TTS choice actually costs on your board. That number matters far more than any generic
published figure.

### Sizing by relative cost, not measured numbers

Without a published number to anchor on, reason about relative cost instead: which plugin
choices are light, medium, or heavy compared to each other. One fact stays fixed: the
always-on core (`ovos-messagebus`, `ovos-core`, `ovos-audio`, `ovos-dinkum-listener`,
`ovos-PHAL`, and whatever skills you load) runs on every device, regardless of which STT, TTS,
or wake-word models you pick. That core must fit on your board before you add any model on
top of it. Size the board for the core first, then budget headroom for the models.

On top of that fixed base, from lightest to heaviest:

- **Lightest**: an energy/noise-threshold [VAD](vad-plugins.md#ovos-vad-plugin-noise) with no
  model download, a small wake-word model such as
  [`ovos-ww-plugin-precise-onnx`](wake-word-plugins.md#ovos-ww-plugin-precise-onnx), and cloud
  [STT](stt-plugins-reference.md#ovos-stt-plugin-azure)/[TTS](tts-plugins-reference.md#ovos-tts-plugin-azure) such as
  Azure, Polly, or Edge-TTS. Inference happens on someone else's server, so the device only
  needs enough CPU for the always-on core plus audio capture and playback.
- **Middle**: local, on-device inference using a small or quantized model. Examples:
  [`ovos-stt-plugin-onnx-asr`](stt-plugins-reference.md#ovos-stt-plugin-onnx-asr) with a small
  `int8`-quantized model, [`ovos-tts-plugin-phoonnx`](tts-plugins-reference.md#ovos-tts-plugin-phoonnx),
  and [`ovos-vad-plugin-silero`](vad-plugins.md#ovos-vad-plugin-silero)'s small neural VAD model.
  `int8` weights consistently have a lower footprint than `fp32` for the same model.
- **Heaviest**: local Whisper-class or other large general-purpose models. See the `large`
  variants in the [STT plugin reference](stt-plugins.md). Several plugins in that table
  recommend a GPU or `use_cuda: true` for this reason. Running these well on a small board
  without a GPU is likely to disappoint.

Pick a tier that leaves headroom above the fixed core cost. Do not pick one that just barely
fits the model alone.

---

## Over-the-air updates

!!! warning "OVOS does not ship an OTA update system"
    There is no built-in over-the-air update mechanism, update server, or delta-update
    protocol. Updating an OVOS device means running `pip`/`uv` against a
    [release channel's constraints file](release-channels.md#choosing-a-release-channel). This
    is the same command whether you run it by hand over SSH or push it out with your own
    device-management tooling, such as Ansible, a custom MDM agent, or a cron job. See
    [Staged Upgrades and Rollback](staged-upgrades.md#staged-upgrades-and-rollback)
    for the update-and-rollback pattern. If your product needs image-level OTA that swaps the
    whole OS image, not just Python packages, bring your own solution, such as Mender,
    SWUpdate, or RAUC. OVOS has no opinion on that layer.

---

## Screens: where things stand today

If your device has a display, [`ovos-gui`](gui-service.md) provides the protocol.
[`ovos-shell`](ovos-shell.md), or a Qt5/QML client speaking the same
[GUI protocol](gui-protocol.md), renders it, with a [homescreen](homescreen.md) skill as the
default idle view. This works today on Linux desktops and the
[GUI-capable installer path](ovos-installer.md), but the legacy Qt5 stack is deprecated
pending the GUI rework. If you are starting a from-scratch hardware design, plan for a
voice-first experience with an optional screen, not the other way around. Treat the GUI
layer as an extra your device can degrade gracefully without, not a hard dependency for
launch.

---

---
**Read next:** [i2c Sound & Audio Setup](i2c-sound.md)
**Related:** [PHAL](phal.md) · [Mark 2 Hardware](mark2.md) · [Production Operations](production-operations.md) · [Mark 1 Hardware](mark1.md)
