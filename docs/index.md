<div class="ovos-hero">
  <h1>OpenVoiceOS Technical Manual</h1>
  <p>The complete guide to using, building on, and understanding the OVOS voice assistant, from your first install to the deepest internals.</p>
</div>

!!! abstract "In a nutshell"
    OpenVoiceOS (OVOS) is a free, open-source voice assistant you run yourself. It is an
    open alternative to Alexa or Google Assistant. This manual covers every layer of it:
    installing a ready-made device, writing your first skill, and the internals of the
    messagebus and intent pipeline underneath. Pick a path below that matches what you
    want to do. You don't need to read it front to back.

![OVOS Logo](https://github.com/OpenVoiceOS/ovos_assets/blob/master/Logo/ovos-logo-512.png?raw=true){ align=right width="160" }

## What is OpenVoiceOS?

**OpenVoiceOS (OVOS)** is a free, open-source, [privacy-respecting](privacy-security.md)
**voice assistant**. Think of it as an open alternative to Alexa or Google Assistant that
*you* control. It listens for a wake word, understands what you ask, and responds with
speech, and optionally a screen.

OVOS code follows a universal donor policy, predominantly Apache-2.0/BSD; exceptions are
listed on [License](license.md).

You can run it on a Raspberry Pi, a desktop, or a server. It is **modular**, built from
many small, swappable pieces called *plugins* and *skills*. You can change how it hears,
thinks, and speaks, or teach it brand-new abilities.

!!! tip "New to all this? Don't worry."
    This manual covers everything from "I just want it working" to "I'm rewriting the
    intent pipeline." You don't need to read it front to back. Pick the path below that
    matches what you want to do. Unfamiliar word? Check the **[Glossary](glossary.md)**.

!!! note "OVOS is do-it-yourself"
    There's no phone app and no plug-and-play appliance to buy. You get OVOS running by
    flashing an SD-card image or working from a terminal. See below. It's not hard, but
    it is hands-on.

---

## Start here

If you just want a working voice assistant with the least fuss, install Raspberry Pi OS
on a Raspberry Pi and run the **[ovos-installer](ovos-installer.md)**, a guided wizard.
The flash-and-boot **[raspOVOS](install-raspovos.md)** image is an alternative, but its
images are in a maintenance pause, so check its status first. Everyone else, pick your
path in the grid below.

---

## Choose your path

<div class="grid cards" markdown>

-   :material-rocket-launch: __I just want to run OVOS__

    ---

    Get a working voice assistant on your device.

    [:octicons-arrow-right-24: ovos-installer (start here)](ovos-installer.md) ·
    [Make it yours](personalize.md) ·
    [Advanced / manual install](release-channels.md) ·
    [Skill examples](skill-examples.md)

-   :material-account-question: __Coming from Alexa or Google?__

    ---

    An honest look at what's the same, what's different, and what to expect on day one.

    [:octicons-arrow-right-24: Coming from Alexa/Google](coming-from-alexa.md)

-   :material-school: __I want to build a skill__

    ---

    Teach OVOS to do something new: your first voice skill, step by step.

    [:octicons-arrow-right-24: Your first skill (10-min tutorial)](first-skill.md) ·
    [Design guidelines](skill-design-guidelines.md) ·
    [Anatomy of a skill](skill-structure.md)

-   :material-cog: __I want to understand how it works__

    ---

    Follow a spoken command from microphone to spoken reply.

    [:octicons-arrow-right-24: Architecture overview](architecture-overview.md) ·
    [Life of an utterance](life-of-an-utterance.md) ·
    [messagebus](bus-service.md)

-   :material-translate: __I want to help translate__

    ---

    Make OVOS speak your language. No coding required.

    [:octicons-arrow-right-24: Translator guide](ovos-localize-tutorial.md) ·
    [Language support](lang-support.md)

-   :material-robot-happy: __I want it to use AI / an LLM__

    ---

    Give your assistant a chat brain: ChatGPT-style, a local model, or a custom persona.

    [:octicons-arrow-right-24: Personas](personas.md) ·
    [Agent engines](agent-plugins.md) ·
    [Local LLM (GGUF)](gguf-plugin.md)

-   :material-lifebuoy: __It's not behaving__

    ---

    Something's not working. Quick, terminal-free fixes for common problems.

    [:octicons-arrow-right-24: It's not behaving](everyday-help.md) ·
    [Troubleshooting](troubleshooting.md)

-   :material-party-popper: __Fun stuff__

    ---

    Jokes, voice changing, personas, and other things to try once it's running.

    [:octicons-arrow-right-24: Fun stuff to try](showcase.md)

-   :material-swap-horizontal: __Coming from Mycroft__

    ---

    What changed, what stayed the same, and how to migrate a skill.

    [:octicons-arrow-right-24: Migrating from Mycroft](migrating-from-mycroft.md)

-   :material-shield-lock: __Privacy & Security__

    ---

    What OVOS talks to over the network, what runs on-device, and how to lock it down.

    [:octicons-arrow-right-24: Privacy & Security](privacy-security.md)

-   :material-server: __I want to run it in production__

    ---

    Fleet configuration, staged upgrades, readiness probes, and self-hosting.

    [:octicons-arrow-right-24: Production Operations](production-operations.md)

-   :material-source-pull: __I want to fix a bug or contribute code__

    ---

    Run a core repo from source, debug it, and get your fix merged.

    [:octicons-arrow-right-24: Development Environment](dev-environment.md) ·
    [Contributing](contributing.md)

-   :material-raspberry-pi: __I want to build a device__

    ---

    SBC-agnostic hardware, PHAL, and why on-device screens aren't a serious option yet.

    [:octicons-arrow-right-24: Hardware Integrators](hardware-integrators.md)

</div>

!!! tip "Accessibility"
    OVOS is voice-first by design, which makes it a strong fit for assistive use. See the
    **[Accessibility](accessibility.md)** statement for specifics.

---

## How OVOS is organized

OVOS is not one program. It's a small team of cooperating services that talk to each
other over a shared **[messagebus](bus-service.md)**. Knowing these components will
make the rest of the manual easier to follow:

!!! tip "Maturity badges"
    Most component and plugin pages open with a **maturity** badge (e.g. ⬤⬤⬤⬤◯ Stable), and
    the plugin catalogs carry a Maturity column. It tells you how much a component can be
    relied on, judged from repository health rather than version number. See the
    [Maturity Scale](maturity.md).

| Piece | In plain terms | Learn more |
|---|---|---|
| **Listener** | Hears the wake word and records your speech | [Speech Service](speech-service.md) |
| **STT** | Turns your speech into text | [STT plugins](stt-plugins.md) |
| **ovos-core** | The "brain": decides which skill should answer | [ovos-core](core.md) |
| **Skills** | The abilities (weather, timers, music…) | [Skill development](skills-overview.md) |
| **TTS** | Turns the reply text back into speech | [TTS plugins](tts-plugins.md) |
| **GUI** | Shows an optional screen or visuals (*legacy/deprecated, [current status](gui-status.md)*) | [GUI Service](gui-service.md) |
| **messagebus** | The shared channel they all talk over | [messagebus Service](bus-service.md) |

!!! info "Plugins vs. Skills: the two ways to extend OVOS"
    A **skill** adds an *ability* ("set a timer", "play the news"). A **plugin** swaps
    out a *building block* (a different speech-to-text engine, a new wake word, another
    voice). See the **[Plugin Ecosystem](plugins-index.md)** to explore what's available,
    or the **[OVOS Repository Index](ecosystem-index.md)** for a map of every public
    repository in the project.

---

## Explore by topic

### :material-city: Core Architecture

Understand the "brain" and "nervous system" of the platform:

*   **[Architecture Overview](architecture-overview.md)**: How all the components fit together.
*   **[Life of an Utterance](life-of-an-utterance.md)**: Trace a command from sound to speech.
*   **[messagebus Service](bus-service.md)**: Look closer at the communication backbone.
*   **[Configuration](config.md)**: Master the layered configuration system.

### :material-laptop: Developer Resources

Ready to build your own plugins or skills?

*   **[Skill Development](skills-overview.md)**: Learn how to write your first voice skill.
*   **[Plugin Ecosystem](plugins-index.md)**: Explore and create plugins for STT, TTS, VAD, and more.
*   **[Intent Pipelines](pipelines-overview.md)**: Understand how OVOS parses natural language.
*   **[Skill Testing](ovoscope-overview.md)**: Test your skills with `ovoscope`.

### :material-earth: Language Support

OVOS is built for a global community:

*   **[Overview](lang-support.md)**: Current status and requirements for full language support.
*   **[Contributing Translations](ovos-localize-tutorial.md)**: Help translate skills and intents with OVOS Localize. No coding needed.
*   **[Technical Parsers](lang-parser.md)**: How OVOS handles numbers, dates, and colors across languages.
*   **[Translation Plugins](translation-plugins.md)**: Explore translation plugins and self-hosting options.

---

## Who is behind OVOS?

OVOS is a community project stewarded by the **OpenVoiceOS V.z.w.**, a Belgian nonprofit
formed in 2023 (see the [project timeline](timeline.md)). Development happens in the open on
[GitHub](https://github.com/OpenVoiceOS). There is no commercial support contract to buy;
support is community-based — the [OVOS Chat on Matrix](https://matrix.to/#/#openvoiceos-skills:matrix.org)
for quick questions and the [Open Conversational AI forum](https://community.openconversational.ai/)
for longer discussions. Vendors embedding OVOS should read [Maturity](maturity.md) and the
[project timeline](timeline.md) to judge activity for themselves.

!!! info "Help improve these docs"
    This manual is maintained by the OVOS community. Every page is cross-checked against
    the real source code. If you find an error or something unclear, please
    [open a pull request or issue](https://github.com/TigreGotico/ovos-technical-manual).
