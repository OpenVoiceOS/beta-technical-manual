# Core Libraries

!!! abstract "In a nutshell"
    OVOS is built on a handful of shared Python libraries that the services and skills all depend
    on, including the messagebus client, general utilities, and typed message models. Their detailed
    API reference lives **in each library's own repository** (every one ships a `docs/` folder), so
    this page is a **map**: what each library is for, and a direct link to its source and docs.
    Keeping the API reference at the source avoids it drifting out of sync with the code. See the
    [Glossary](glossary.md) for terms.

!!! info "Why this is just links"
    The library repos themselves maintain per-library API docs (each has a `docs/`
    folder rendered on GitHub). Re-hosting them here would mean keeping two copies in sync, so the
    manual links out to the authoritative source instead. Use the links below.

---

## `ovos-bus-client`

The client for the OVOS [messagebus](bus-service.md): the `MessageBusClient`, the `Message`
object, `Session` handling, and the high-level helper APIs (GUI, Enclosure, OCP) that wrap common
bus chores. It also ships the `ovos-listen` / `ovos-speak` / `ovos-say-to` / `ovos-simple-cli`
[command-line tools](cli-tools.md).


- Source: [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client)
- API docs: [`/docs`](https://github.com/OpenVoiceOS/ovos-bus-client/tree/dev/docs)
- In the manual: [messagebus Service](bus-service.md) (architecture & message flow).
- License: Apache-2.0

## `ovos-utils`

The grab-bag of shared helpers used across OVOS: logging, process/lifecycle management, bus-event
decorators, language helpers, sound playback, and many small utilities. It also provides the
`ovos-logs` [log tool](cli-tools.md).

- Source: [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils)
- API docs: [`/docs`](https://github.com/OpenVoiceOS/ovos-utils/tree/dev/docs)
- License: Apache-2.0

## `ovos-pydantic-models`

Typed [Pydantic](https://docs.pydantic.dev/) models for OVOS bus messages: a schema layer that
lets tools validate and introspect message types instead of passing around raw dicts.

- Source: [OpenVoiceOS/ovos-pydantic-models](https://github.com/OpenVoiceOS/ovos-pydantic-models)
- Protocol reference: [MessageBus Protocol Reference](https://openvoiceos.github.io/ovos-pydantic-models/), a
  browsable catalog of every modelled message, grouped by subsystem
- License: Apache-2.0

The models are generated semi-automatically from source, so the published catalog can lag or
diverge from the code. Treat it as a map of the message space, not as the contract. The
[formal specifications](architecture-specs.md) remain the authority on required behavior.

## `ovos-plugin-manager` (OPM)

Discovers, loads, and configures every kind of OVOS plugin via entry-point groups. Covered in the
manual at [Plugin Manager](plugin-manager.md).

- Source: [OpenVoiceOS/ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager)
- API docs: [`/docs`](https://github.com/OpenVoiceOS/ovos-plugin-manager/tree/dev/docs)
- License: Apache-2.0

## `ovos-workshop`

The skill-author framework — the `OVOSSkill` base classes, decorators, intent registration, GUI
helpers, and skill lifecycle. Covered in the manual under [Skill Development](workshop-overview.md).

- Source: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop)
- API docs: [`/docs`](https://github.com/OpenVoiceOS/ovos-workshop/tree/dev/docs)
- License: Apache-2.0

## `ovos-config`

The layered configuration system (defaults → system → user → runtime). Covered in the manual at
[Configuration](config.md).

- Source: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config)
- API docs: unlike the libraries above, `ovos-config` has no separate `docs/` folder. Its
  [`README`](https://github.com/OpenVoiceOS/ovos-config/blob/dev/README.md) is the API reference.
- License: Apache-2.0

## `kw-template-matcher`

A standalone template-expansion and fuzzy-matching utility for prototyping NLU grammars:
expands templates with optional phrases (`[optional]`), alternatives (`(choice1|choice2)`), and
slots (`{slot_name}`), then fuzzy-matches free text against the expansions (via `rapidfuzz` /
`simplematch`) with slot extraction. It also ships an OPM plugin: the entry point labeled `ovos-keyword-template-matcher`
registers under the `opm.transformer.intent` group (the pip/PyPI package name is
`keyword-template-matcher`, without the prefix) (`KeywordTemplateMatcher`, an intent
transformer that hooks intent registration on the bus). Use the library directly when
hand-authoring or prototyping matching rules. License note: the `setup.py` classifier says MIT,
but the repository ships no `LICENSE` file (see [Licensing](license.md) for how to treat that).

- Source: [OpenVoiceOS/kw-template-matcher](https://github.com/OpenVoiceOS/kw-template-matcher)

---

These libraries are transitive dependencies of `ovos-core` and are version-bounded by
the same [release-channel constraints files](release-channels.md) rather than pinned
independently. You don't normally choose their versions yourself.

For the full list of OVOS repositories, including plugins, skills, and tools, see the
[OVOS Repository Index](ecosystem-index.md).

---
**Read next:** [Language Names](lang-parser.md)
**Related:** [OVOS Repository Index](ecosystem-index.md) · [Plugin Manager](plugin-manager.md) · [Bus Service](bus-service.md) · [Configuration](config.md)
