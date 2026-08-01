# Accessibility

!!! abstract "In a nutshell"
    OVOS is a **voice-first** assistant. Talking to it and hearing it talk back is the primary
    way to use it, not a fallback for a graphical app. That matters if you, or someone you're
    setting this up for, can't reliably use a screen, mouse, or keyboard. A voice interface
    removes those requirements entirely for day-to-day use. This page states plainly what OVOS
    does and does not offer today: the install path that avoids a screen reader fighting an
    installer wizard, how to slow down or change the speaking voice for long listening sessions,
    and an honest note on where support is currently thin. See the [Glossary](glossary.md) for
    terms and [Troubleshooting](troubleshooting.md) if something isn't working.

---

## Voice is not a fallback here

Every core interaction works with sound alone, no display required. That includes waking the
assistant, asking a question, hearing the answer, adjusting [volume](skill-examples-utilities.md#volume),
and asking what it can do. This isn't a design aspiration. A skill is not required to register
any [GUI](gui-service.md) page at all, and a skill with nothing to show on screen simply speaks
its response instead. The current OVOS GUI stack is itself
[deprecated and not generally usable](gui-service.md) while its replacement is built. So today,
voice-only really is how most OVOS devices operate in practice, screen or no screen.

## Installing without fighting a screen reader

The interactive [`ovos-installer`](ovos-installer.md) wizard is a series of arrow-key menus in a
terminal. That can be awkward to navigate with a screen reader reading a live, redrawing TUI.
The installer has a second path built for exactly this kind of non-interactive setup: a
[**scenario file**](ovos-installer.md#non-interactive-scenario-install). This is a plain YAML
file that lists every choice up front (installation method, channel, profile, features), and the
installer reads and applies it without displaying a single menu. Write (or have someone write)
the scenario file once, in a plain text editor, and run the installer against it. This avoids
the interactive wizard entirely. Write the file to `~/.config/ovos-installer/scenario.yaml`
before running the installer, and it reads that file automatically instead of showing any menus.
See [Non-interactive (scenario) install](ovos-installer.md#non-interactive-scenario-install) for
the full file format and ready-made examples.

## Tuning speech for long listening sessions

For someone listening to OVOS for extended periods, two things help most: a comfortable speaking
rate, and a voice that stays intelligible at that rate. There is no single global "speaking rate"
setting shared by every voice. OVOS supports many [TTS plugins](tts-plugins.md), and any rate or
voice key a given engine accepts lives in that plugin's own configuration block. It is keyed by
the plugin's module name, under `tts` in `mycroft.conf`, following the pattern
`tts.<module-name>.<key>` (for example, `tts.ovos-tts-plugin-matxa-multispeaker-cat.voice`).
[`ovos-tts-plugin-matxa-multispeaker-cat`](tts-plugins.md#ovos-tts-plugin-matxa-multispeaker-cat)
and [`ovos-tts-plugin-edge-tts`](tts-plugins.md#ovos-tts-plugin-edge-tts) each expose their own
`voice` key for picking a specific speaker. This manual's [TTS Plugins](tts-plugins.md) reference
does not currently document a dedicated rate or speed key for any individual plugin. Check that
plugin's own repository for one before falling back to SSML below.

Rate control is per-plugin config, so check the active plugin's page first. [SSML](ssml.md)'s
`<prosody rate="...">` tag is a niche fallback, applied per-utterance from a skill. It is
**experimental** and only honored by a couple of TTS plugins (currently espeakNG and Amazon
Polly). Every other plugin just strips the tag and speaks the plain text, so it does nothing for
most voices:

!!! note "This one is for people who write skills"
    The snippet below is Python code that goes inside a skill. If you do not write
    skills, ask the skill author for a rate option, or pick a calmer voice instead.

```python
from ovos_utils.ssml import SSMLBuilder

ssml_text = SSMLBuilder(speak_tag=True).say_slow("Here is the reminder you asked for.").build()
self.speak(ssml_text)
```

Sending SSML is always safe. An unsupported voice just ignores it and speaks the plain text. But
don't rely on it as your primary rate-control mechanism. Prefer a plugin's own rate or speed
config key where one exists.

## Motor and cognitive access

Voice-first interaction is itself the main accessibility feature for limited dexterity. Nothing
in day-to-day use requires precise pointing, a keyboard, or reaching a physical control. A
[wake word](wake-word-plugins.md) and speech cover waking, asking, and adjusting
[volume](skill-examples-utilities.md#volume) without touching the device at all. Two things are worth
tuning specifically for this:

- **Wake-word sensitivity.** If pressing a physical button or repeating a phrase precisely is
  hard, tune the wake word to trigger more easily rather than relying on a hands-on retry. See
  [Wake-word Plugins](wake-word-plugins.md#wake-word-configuration) for the `sensitivity` and
  `trigger_level` keys, and the "It's not listening to me" section of
  [It's Not Working](everyday-help.md#its-not-listening-to-me) for the quick version.
- **Fewer, calmer confirmation steps.** For anyone who finds fast disambiguation prompts hard to
  follow, a common need for cognitive or attention-related disabilities, favor skills and
  phrasing that resolve in one turn over ones that chain several "did you mean X or Y"
  clarifications. Keep requests short and literal. [What can I say?](skill-examples.md) lists the
  phrasing each skill actually expects, which avoids triggering a clarification round-trip at
  all. This is a usage pattern more than a config switch. OVOS has no built-in setting that slows
  down or simplifies its clarification dialog today.
- **If speaking isn't reliable.** Voice-first is itself a barrier for non-verbal users and anyone
  with a motor speech disorder, severe stutter, or temporary voice loss. The documented
  text-input fallback is `ovos-simple-cli` (see [Command-line Tools](cli-tools.md)), which opens
  an interactive typed chat with the running assistant. You type instead of speaking and get the
  same responses.

## Where support is thin

- **Typed input is terminal-only.** `ovos-simple-cli` gives a text alternative to speech, but
  there is no GUI or on-screen typed-input path, so it assumes comfort with a terminal.

- **The legacy GUI stack is deprecated.** Anything that depended on visual screen content, rather
  than speech, is not a reliable path regardless of assistive technology. See
  [GUI Service](gui-service.md) for the current status and the replacement effort underway.
- **No dedicated screen-reader integration exists for the installer's interactive wizard mode**
  beyond the scenario-file path above. The wizard itself is a standard terminal menu, not one
  built with screen-reader affordances.
- **Speaking-rate control is per-plugin, not a single global switch** (see above). Expect to look
  up the specific voice or plugin in use rather than finding one universal setting.
- **No visual transcript or captioning of spoken output exists for Deaf or Hard-of-Hearing
  users.** What OVOS speaks is not also written to a screen anywhere in the stack today. The
  deprecated GUI stack noted above never implemented this either. A Deaf or Hard-of-Hearing user
  currently has no supported way to read what the assistant said.
- **No dedicated tuning exists for limited dexterity or cognitive load beyond what's described
  above.** Wake-word sensitivity and phrasing choices help, but there is no built-in "simplified
  mode" or slower confirmation flow.

---

**Read next:** [Make it yours](personalize.md) · [It's not behaving](everyday-help.md)
**Related:** [Wake-word Plugins](wake-word-plugins.md) · [Command-line Tools](cli-tools.md) · [SSML](ssml.md) · [Troubleshooting & Debugging](troubleshooting.md)
