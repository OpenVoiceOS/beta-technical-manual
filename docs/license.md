# License

!!! abstract "In a nutshell"
    OVOS follows a **universal donor** licensing policy: the code should be usable by anyone,
    anywhere, with no strings attached. In practice that means permissive licenses, mostly
    Apache 2.0 or BSD, for all core components, with a short, explicitly documented list of
    exceptions. Each exception is either a dependency forcing a stricter license on one
    specific plugin, or a plugin repository that never shipped a `LICENSE` file at all.

Under the universal donor policy, OVOS code should be usable anywhere by anyone, with no conditions attached. OVOS is predominantly Apache 2.0 or BSD licensed. The exceptions are a small minority of plugins, and every one of them is listed in the table below. Each exception exists either because a dependency forces a stricter license, or because the plugin's own repository never shipped a `LICENSE` file at all.

Individual plugins or skills may carry their own license when they wrap a dependency that requires it. For example, a TTS plugin that wraps an AGPL-licensed engine cannot itself be relicensed under a more permissive term. Core components are kept fully free. Any code whose license cannot be controlled lives in an optional plugin instead, flagged as such.

This also means avoiding LGPL code, for the reasons explained in
[this discussion of the GPL classpath exception](https://softwareengineering.stackexchange.com/questions/119436/what-does-gpl-with-classpath-exception-mean-in-practice/326325#326325).

Padatious used to be listed here. It was ported from libfann to pure numpy, so
it is Apache-2.0 with no reservations and is no longer an exception.

## Policy properties

The license policy has the following properties:

- It gives the user of the software complete and unrestrained access, so they may
  inspect, modify, and redistribute their changes:
    - **Inspection**: anyone may inspect the software for security vulnerabilities.
    - **Modification**: anyone may modify the software to fix issues or add features.
    - **Redistribution**: anyone may redistribute the software on their own terms.
- It is compatible with GPL licenses. Projects licensed as GPL can be distributed with OVOS.
- It allows incorporating GPL-incompatible free software, such as CDDL-licensed code.

The policy does not restrict what software may run *on* OVOS. Thanks to the plugin
architecture, even traditionally tightly-coupled components such as drivers can be
distributed separately, so plugin maintainers are free to choose whatever license fits their
own project.

---

## Notable licensing exceptions

The repositories below do not follow the universal donor policy. Check their licenses are compatible with your use case before depending on them.

| Repository | License | Reason |
|---|---|---|
| [ovos-tts-plugin-mimic3](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3) | AGPL | depends on [mimic3](https://github.com/MycroftAI/mimic3) ([AGPL-3.0](https://github.com/MycroftAI/mimic3/blob/master/LICENSE)). This plugin is **archived**. See [Deprecated & Archived Repositories](deprecated-repos.md) for the current replacement |
| [ovos-tts-plugin-espeakNG](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG) | GPL | depends on [espeak-ng](https://github.com/espeak-ng/espeak-ng) ([GPL-3.0](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING)) |
| [ovos-tts-plugin-SAM](https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM) | see repo (no license file) | the package self-declares Apache-2.0 in its `pyproject.toml`. The repository ships no `LICENSE` file. The underlying S.A.M. engine is reverse-engineered abandonware with no clear upstream license |
| ovos-tts-plugin-phoonnx (built into [phoonnx](https://github.com/TigreGotico/phoonnx)) | Apache-2.0 (code); models per model card | the `phoonnx` repository gained an Apache-2.0 `LICENSE` in 2026; individual voices still carry their own model-card terms. See the [TTS plugin table](tts-plugins-reference.md) |
| [ovos-tts-plugin-beepspeak](https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak) | no license file | novelty R2-D2-style TTS plugin. The repository ships no `LICENSE` file |
| [ovos-tts-plugin-lux](https://github.com/OpenVoiceOS/ovos-tts-plugin-lux) | see repo (no license file) | zipvoice-based voice-cloning TTS plugin. The package self-declares Apache-2.0 in its `setup.py` (with the OSI Apache classifier), but the repository ships no standalone `LICENSE` file |
| [ovos-stt-plugin-HiTZ](https://github.com/OpenVoiceOS/ovos-stt-plugin-HiTZ) | no license file | archived/deprecated Basque STT plugin. The repository ships no `LICENSE` file |
| [kw-template-matcher](https://github.com/OpenVoiceOS/kw-template-matcher) | see repo (no license file) | template-matching library + `opm.transformer.intent` plugin. The `setup.py` classifier says MIT, but the repository ships no `LICENSE` file |

The rows above with **no license file** are not a rejection of the universal donor policy.
They are repositories that never declared one, so no license can be assumed for redistribution
purposes. Treat "no license file" as more restrictive than any permissive license, not less.

See also: [Why OpenVoiceOS Uses Permissive Licenses](https://blog.openvoiceos.org/posts/2023-02-28-permissive-licenses) (OVOS blog).

---
**Read next:** [Reference Overview](reference-overview.md)
**Related:** [Deprecated & Archived Repositories](deprecated-repos.md) · [OVOS Repository Index](ecosystem-index.md) · [Contributing](contributing.md)
