# ovos-spec-tools

!!! note "Maturity: Beta ⬤⬤⬤◯◯"
    In real use but still settling. Watch releases for the occasional breaking change. Rated by [repository health](maturity.md), not version.

!!! abstract "In a nutshell"
    [**ovos-spec-tools**](https://github.com/OpenVoiceOS/ovos-spec-tools) is the one
    conformant implementation of the low-level primitives the [Formal
    Specifications](architecture-specs.md) describe: template expansion, locale
    loading, dialog rendering, language matching, the message envelope, session
    handling, and the keyword-intent builder. Depend on it instead of hand-rolling
    these pieces again.

??? info "Formal specification"
    This library serves the **[OpenVoiceOS/architecture](https://github.com/OpenVoiceOS/architecture)** specs. See the [spec index](architecture-specs.md).

---

[**ovos-spec-tools**](https://github.com/OpenVoiceOS/ovos-spec-tools) is the
**single conformant implementation** of the low-level primitives the specs
describe. OVOS components used to reimplement template expansion, resource
loading, and language matching in several places, and the copies drifted.
Rather than reimplement (and re-introduce the bugs), depend on this package. It
is dependency-light (the core has **no dependencies**) and tracks the specs
clause-for-clause.

## Primitives

| Primitive | Spec | What it does |
|-----------|------|--------------|
| Sentence-template expander | [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) | Expands `(a\|b)` / `[opt]` / `{slot}` / `<vocab>` into the sentences it denotes |
| Locale resource loader | [OVOS-INTENT-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | Loads a skill's `locale/` `.intent` / `.dialog` / `.voc` / `.entity` / `.blacklist` / `.prompt` files |
| Dialog & prompt renderer | [OVOS-INTENT-2 §4](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | Renders a spoken `.dialog` line or a `.prompt` with slot substitution |
| Language-tag matching | [OVOS-INTENT-2 §2.2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) *(non-normative)* | Picks the closest available BCP-47 language for a request |
| Message envelope | [OVOS-MSG-1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md) | The `{type, data, context}` `Message` and its `forward`/`reply`/`response` derivations |
| `Session` / `SessionManager` | [OVOS-SESSION-1](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md) | The registered session-carrier field set with omission-not-null (de)serialization, plus a process-wide one-object-per-`session_id` registry that folds each incoming snapshot onto the live object and re-stamps `forward`/`reply`/`response` derivations with it |
| Context gating & decay | [OVOS-CONTEXT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md) | Stateless helpers over the flat `session.intent_context` map: `gate_satisfied`/`is_live`/`decrement`/`prune`/`enforce_cap` for `requires_context`/`excludes_context` gating and decay, plus `context_supplied_slots`/`context_slot_candidates` for context-sourced slot fill |
| `IntentBuilder` / `Intent` | [OVOS-INTENT-4 §5](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md) | Adapt-free, plugin-agnostic keyword-intent definition (`require`/`optionally`/`one_of`/`exclude`/`build()`), mapping to the `ovos.intent.register.keyword` payload. `voc_match` matches an utterance against a `.voc` file. Source-compatible with the `ovos-workshop` classes it replaces |
| `SpecMessage` | multiple ([PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md), [INTENT-4](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-4.md), [STOP-1](https://github.com/OpenVoiceOS/architecture/blob/dev/stop-1.md), [PERSONA-1](https://github.com/OpenVoiceOS/architecture/blob/dev/persona.md), [FALLBACK-1](https://github.com/OpenVoiceOS/architecture/blob/dev/fallback.md), …) | An enum of every canonical `ovos.*` spec bus topic, plus `MIGRATION_MAP`/`NamespaceTranslator`: the legacy-to-`ovos.*` rename table the [namespace bridge](bus-namespace-migration.md) applies |
| `ovos-spec-lint` | [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) / [-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) | A linter that validates a `locale/` folder against the resource-format specs, including `.blacklist`/`.entity` naming and slot-free constraints |

```bash
pip install ovos-spec-tools            # core — no dependencies (Python 3.10+)
pip install ovos-spec-tools[langcodes] # adds smart language fallback
```

```python
from ovos_spec_tools import expand, LocaleResources, render, render_prompt, closest_lang, Message

expand("(turn|switch) [the] light")             # every sentence the template denotes
res = LocaleResources("my-skill/locale")
render(res.load_dialog("weather", "en-US"),     # a spoken response
       slots={"temperature": 21})
render_prompt("Summarize: {{text}}",            # a .prompt string — whole text is
              slots={"text": "..."})            # the prompt, {{name}} slots filled
                                                # (PromptRenderer is the stateful form)
closest_lang("en-AU", ["pt-BR", "en-US"])       # -> 'en-US'
m = Message("ovos.intent.list", {}, {"source": "skill.id"})
m.response({"intents": ["..."]}).serialize()    # -> the 'ovos.intent.list.response' JSON
```

## ovos-spec-lint

Lint a skill's locale folder against the grammar and format specs:

```bash
ovos-spec-lint my-skill/locale
```

`ovos-spec-lint` also takes a `--spec-version` flag, for linting a skill that targets an older
runtime. It answers "would a runtime at spec version N ignore any of these files?". Accepted
values are `0` to `3`, and the default is **3**.

The gate only ever emits a warning, never an error, and it fires when a resource role is
*newer* than the version you name. Each role has the version it arrived in:

| Role | Requires |
|---|---|
| [`.blacklist`](resource-files.md) | 1 |
| `.prompt` | 2 |
| `<name>` | 3 |

So `--spec-version 0` warns about a `.blacklist`, and any value from 1 up says nothing about
it. Use the flag to check what an older deployment would silently drop, not to grade a
migration.

## Session, intents, and the topic vocabulary

The session carrier, the keyword-intent builder, and the canonical topic
vocabulary follow the same pattern: plain data plus stdlib-only helpers.

```python
from ovos_spec_tools import IntentBuilder, Session, SpecMessage

# OVOS-SESSION-1 wire-shape carrier; SessionManager (in ovos_spec_tools.session)
# is the optional one-object-per-session_id registry built on top of it
session = Session(session_id="default", lang="en-US")

# OVOS-INTENT-4 §5 keyword-intent structure — adapt-free, source-compatible
# with the ovos-workshop IntentBuilder skills already import
intent = IntentBuilder("HelloIntent").require("Hello").build()

SpecMessage.SPEAK.value  # -> 'ovos.utterance.speak', the spec-canonical topic name
```

`ovos-spec-tools` also owns the **vocabulary** of the legacy-to-`ovos.*` topic
rename: `SpecMessage` and `MIGRATION_MAP`, listed in the primitive table above.
The runtime bridge that applies that mapping on the wire lives in
`ovos-bus-client`. See [Bus namespace migration](bus-namespace-migration.md)
for that mechanism.

!!! tip "When to reach for it"
    Building an intent-matching pipeline plugin, a skill loader, a satellite, or any third-party
    tool that touches OVOS templates, locale files, language selection, or the
    bus envelope? Depend on `ovos-spec-tools` instead of hand-rolling. That is
    exactly the drift the package exists to prevent. See also
    [Resource Files](resource-files.md) and [Language Selection](lang-selection.md).

---
**Read next:** [Specification Tooling](spec-tooling.md) · [ovos-test-harness](spec-test-harness.md)
**Related:** [Formal Specifications](architecture-specs.md) · [Bus namespace migration](bus-namespace-migration.md) · [MessageBus Service](bus-service.md)
