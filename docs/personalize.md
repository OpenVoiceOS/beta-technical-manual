# Make It Yours

!!! abstract "In a nutshell"
    You just installed OVOS and it works. Now you want it to sound like *your* assistant: a
    different name to wake it up, a different voice answering you, or a different language
    altogether. All three are small edits to the same file, `~/.config/mycroft/mycroft.conf`.
    This page is a quick-reference for all three. Each section links to the full page with
    more detail and more options.

!!! tip "Want to do this by voice instead of editing files?"
    Everything below needs opening a text file and a restart. If you'd rather change your wake
    word, voice, or volume by *talking* to your assistant, see
    [What can I say?](skill-examples.md) and [It's Not Working: Quick Fixes](everyday-help.md)
    for what's already possible hands-free (e.g. volume) versus what still needs a config edit
    (wake word, voice, language).

All the settings below live in your personal config file at
**`~/.config/mycroft/mycroft.conf`** (create it if it doesn't exist yet. See
[Configuration Management](config.md) for how the layering works). It's JSON with comments
allowed (JSONC). Open it with any text editor, for example:

```bash
nano ~/.config/mycroft/mycroft.conf
```

!!! tip "Prefer a browser over a terminal?"
    RaspOVOS images ship two web editors: `ovos-yaml-editor` edits this same
    configuration in the browser (port 9210), and `ovos-skill-config-tool` edits
    individual skill settings (port 8000). Open `http://<device-ip>:9210` from any
    computer on your network. On other installs you can add them with pip. See
    [RaspOVOS](install-raspovos.md) for details.

    To change one skill's own settings, not the global config, use the [Web-Based
    Settings UI](skill-settings.md#web-based-settings-ui-community) instead. No
    terminal needed.

Before restarting, double-check the file still parses. A stray missing comma or bracket will
stop it from loading. Because `mycroft.conf` allows `//` comments, plain `json.tool` will
reject it even when it's fine. Use the same comment-aware loader OVOS itself uses. This runs
a small Python command directly in the terminal. Paste it exactly as shown:

```bash
python3 -c "from ovos_utils.json_helper import load_commented_json; load_commented_json('$HOME/.config/mycroft/mycroft.conf'); print('OK')"
```

This prints `OK` if the file is valid, or a `JSONDecodeError` with a line/column pointing at the
mistake if it isn't. You can also confirm a specific value actually took effect after restarting
with `ovos-config show --section <name>` (see [Configuration Management](config.md#cli-reference)
for the full CLI). Once the file parses cleanly, apply the change:

--8<-- "snippets/restart-ovos.md"

## Change your wake word

```json
{
  "listener": { "wake_word": "hey_computer" },
  "hotwords": {
    "hey_computer": { "module": "ovos-ww-plugin-vosk", "listen": true }
  }
}
```

As with voices below, the plugin must be installed into the same environment OVOS runs in
before the config can use it (`pip install ovos-ww-plugin-vosk` for this example). Take a
custom hotword like this one, with no `fallback_ww` configured. A module that fails to
load is logged loudly (an `ERROR` with a traceback in the listener log) and simply dropped,
so the assistant stops responding to that wake word.

The shipped default `hey_mycroft`
behaves differently. Its config chains through `fallback_ww` entries (tflite → precise →
vosk → pocketsphinx), so a failed primary engine there falls back to the next engine.
The assistant keeps listening, though each failed engine still logs its own `ERROR`
(see [Wake-word Plugins](wake-word-plugins.md)). Full walkthrough,
plugin choices, and tuning: [Wake-word Plugins](wake-word-plugins.md#change-your-wake-word).

## Change your voice

Install the plugin's package first. Unlike most tweaks on this page, this one does
require a terminal today. There is no on-device UI for installing plugins yet. `phoonnx`
ships the `ovos-tts-plugin-phoonnx` plugin,
so without it OVOS has nothing to load and the voice won't actually change. Activate the
same Python [virtual environment](glossary.md) OVOS runs in
*before* running this, or the plugin installs somewhere OVOS never looks. On raspOVOS
images and ovos-installer setups this is the environment the installer created, for
example `source ~/.venvs/ovos/bin/activate`:

```bash
pip install phoonnx
```

Make sure to install it into the same Python environment OVOS itself runs in. See the
note in [TTS Plugins](tts-plugins.md#change-your-voice).

```json
{
  "tts": {
    "module": "ovos-tts-plugin-phoonnx"
  }
}
```

Browse voice samples and see every available plugin: [TTS Plugins](tts-plugins.md#change-your-voice).

## Make it talk slower

There is no single global speaking-rate setting. Rate lives in the active TTS plugin's own
config block, under whichever key that plugin exposes, so check its entry in
[TTS Plugins](tts-plugins.md) first. If you are setting up a device for someone who needs a
slower, steadier voice, [Accessibility](accessibility.md#tuning-speech-for-long-listening-sessions)
walks through picking a voice that stays clear at a reduced rate.

## Change your language

```json
{
  "lang": "de-DE"
}
```

This one line is enough on its own. STT, TTS, and every language-aware plugin follow the
global `lang` automatically. Want the *recommended* plugins/voices for that language instead
of your current ones? Run `ovos-config autoconfigure -l de-DE --offline` afterwards. Full
picture, supported-language table, and gaps to watch for: [Language Support](lang-support.md).

!!! tip "Switching language"
    `lang` sets the primary language. To also understand a second language without
    replacing the primary one, add it to `secondary_langs`. See [Language
    Selection](lang-selection.md) for how OVOS picks a language per utterance from
    these two keys.

---

**Read next:** [Fun stuff to try](showcase.md)
**Related:** [Configuration Management](config.md) · [Wake-word Plugins](wake-word-plugins.md) · [TTS Plugins](tts-plugins.md) · [Language Support](lang-support.md)
