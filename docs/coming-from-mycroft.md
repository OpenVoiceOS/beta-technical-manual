# Coming from Mycroft

!!! abstract "In a nutshell"
    You had a Mycroft device or a `mycroft-core` install and you want to know what daily
    use looks like on OVOS. Short answer: the same habits work. The wake word is still
    "Hey Mycroft" by default, skills still answer the same phrases, and dialog files and
    intents behave the way you remember. What changed is everything behind the scenes:
    there is no cloud account anymore. New to the words here? See the
    [Glossary](glossary.md).

This page is for people who *use* a voice assistant. If you wrote Mycroft skills and want
to port them, read [Migrating from Mycroft](migrating-from-mycroft.md) instead.

## What stays the same

- The default wake word is still "Hey Mycroft". You can change it, but you do not have to.
- Skills, intents, and dialog files use the same model. Community skills you remember
  (weather, timers, music) exist as OVOS skills.
- The configuration file is still called `mycroft.conf`.

## What is different for you

- **No account, no pairing.** There is no `home.mycroft.ai` and no pairing code on first
  boot. The device works out of the box.
- **Settings live on the device.** Anything you used to change on the Mycroft web
  dashboard is now a local setting. Most everyday changes work by voice or through a
  small config edit. Start with [Make it yours](personalize.md).
- **Speech services are yours to pick.** STT and TTS come from swappable plugins. You can
  run them on-device, on your own server, or use public servers. See
  [Choosing Plugins](choosing-plugins.md).
- **Old Mycroft hardware keeps working.** The Mark II and Raspberry Pi setups (Picroft)
  have a direct successor in the [RaspOVOS image](install-raspovos.md).
- **Skill installation changed.** There is no Mycroft Marketplace. Skills install like
  Python packages. See [Skill Installer](skill-installer.md).

## Where to go next

- [Install with ovos-installer](ovos-installer.md) or the [RaspOVOS image](install-raspovos.md)
- [Make it yours](personalize.md), then [Fun stuff to try](showcase.md)
- Something not working? Start at [It's not behaving](everyday-help.md)
