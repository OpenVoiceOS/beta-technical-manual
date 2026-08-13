# Coming From Alexa or Google Assistant?

!!! abstract "In a nutshell"
    OVOS is a voice assistant you run yourself, not a product you buy off a shelf. So the
    on-ramp looks different from Alexa or Google Assistant. This page gives an honest
    comparison: what's the same, what's missing, what setup looks like, and what works the
    moment you're done. Read it before you start.

## The short version

- There is **no retail OVOS device** you can buy today and plug in. The closest equivalent is
  flashing the [RaspOVOS](install-raspovos.md) image onto a Raspberry Pi and its SD card. That
  is a half-hour, one-time setup, not an unbox-and-go experience.
- There is **no companion phone app** for pairing or day-to-day control, the way the Alexa or
  Google Home apps work. You set up and configure OVOS over SSH in a terminal, or by editing a
  text file. See [Make It Yours](personalize.md).
- There is **no generally usable on-screen visual assistant**. See
  [Screens on OVOS Today](gui-status.md) for the honest state of that. OVOS is voice-first. A
  screen, where present, is a bonus, not the primary interface.
- **Smart-home control isn't automatic.** Alexa and Google devices come with smart-home skills
  built in. OVOS needs a one-time Home Assistant setup. See
  [OVOS & Home Assistant](home-assistant.md).
- **"Skill" means something different here.** Both platforms use the word, but OVOS has no
  centralized skill store or certification process. You install skills directly, with
  `pip` or the OVOS installer, not through a marketplace.
- In exchange, you get an assistant that runs on hardware you choose and is not tied to one
  company's cloud. For the parts you choose to run locally, it doesn't have to send your voice
  anywhere at all. See [Privacy & Security](privacy-security.md) for exactly what a default
  install does and doesn't send over the network.

## What setup actually looks like

There's no pairing screen or app-based wizard. You either:

1. Flash the [RaspOVOS](install-raspovos.md) image to an SD card and boot a Raspberry Pi with
   it. This is the closest thing to "unbox and go" that exists today.
2. Run the [ovos-installer](ovos-installer.md) against an existing Linux install (Raspberry Pi
   OS or a regular desktop or laptop). This is a guided, menu-driven wizard, but you run it from
   a terminal, typically over SSH if the device is headless.

If you've never used SSH before, budget extra time for that step. Or use the RaspOVOS image,
which needs none of it.

## What works on day one

Once installed, these work immediately with no extra setup. They roughly match what you'd
expect from Alexa or Google Assistant out of the box:

- Timers, alarms, and reminders
- Weather
- General knowledge questions (via DuckDuckGo, Wikipedia, and similar)
- Internet radio
- Jokes and small talk

See [What can I say?](skill-examples.md) for the full, browsable list. See
[Screens on OVOS Today](gui-status.md) if you're wondering about visual responses on a device
with a screen.

## What needs extra setup

- **Smart-home control** (lights, thermostats, scenes) needs a Home Assistant instance and a
  one-time skill setup. See [OVOS & Home Assistant](home-assistant.md).
- **A specific wake word, voice, or language** other than the defaults needs an edit to a config
  file, not a voice command or an app toggle. See [Make It Yours](personalize.md).
- **Playing your own music library or a streaming service** beyond internet radio needs an
  additional plugin. See [What can I say?](skill-examples.md).

## What you won't be able to move across

Some Echo habits have no equivalent. It is better to know that before you unplug anything.

- **Synchronized multi-room audio.** Speaker groups that play the same thing in step across
  rooms are not part of OVOS itself. Each device is independent. Synchronized playback needs
  a system-level solution such as [Snapcast](https://github.com/badaix/snapcast), which
  neither OVOS nor the [RaspOVOS](install-raspovos.md) image ships. You wire it up yourself,
  and it is not driven by voice.
- **Shopping and to-do lists.** [ovos-skill-alerts](skill-examples-alerts-time.md) manages
  todos and lists by voice ("add milk to the shopping list"), locally — but nothing syncs
  to a phone app the way Alexa's list does.
- **Voice shopping, calling, and messaging.** OVOS has no purchasing, no drop-in, no
  announcements between devices, and no calls.
- **A phone app.** Configuration is a file you edit, not an app screen.
  [Make It Yours](personalize.md) walks through the edits you are most likely to want.

Everything in this list is something you can build. OVOS is a toolkit, and skills are Python.
None of it arrives working the way it does on an Echo.

---

**Read next:** [Install with ovos-installer](ovos-installer.md) · [RaspOVOS](install-raspovos.md)
**Related:** [OVOS & Home Assistant](home-assistant.md) · [What can I say?](skill-examples.md) · [Privacy & Security](privacy-security.md) · [Screens on OVOS Today](gui-status.md)
