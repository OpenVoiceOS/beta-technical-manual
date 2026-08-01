# Specification Tooling

!!! note "Maturity: Beta ⬤⬤⬤◯◯"
    In real use but still settling. Watch releases for the occasional breaking change. Rated by [repository health](maturity.md), not version.

!!! abstract "In a nutshell"
    The [Formal Specifications](architecture-specs.md) say *what* must happen.
    Two pieces of tooling turn that from prose into something you can build on
    and check:

    - [**ovos-spec-tools**](spec-tools-lib.md): a ready-made, conformant
      implementation of the low-level primitives (template expansion, locale
      loading, sessions, the keyword-intent builder, the topic vocabulary).
    - [**ovos-test-harness**](spec-test-harness.md): an executable test suite
      that proves a running stack obeys the specs.

    A related, separate mechanism lets the ecosystem adopt the new `ovos.*`
    topic names without a flag day: see
    [Bus namespace migration](bus-namespace-migration.md).

??? info "Formal specification"
    These tools serve the **[OpenVoiceOS/architecture](https://github.com/OpenVoiceOS/architecture)** specs. See the [spec index](architecture-specs.md).

---

## ovos-spec-tools: the reference implementation

[ovos-spec-tools](spec-tools-lib.md) is the single conformant implementation of
the low-level primitives the specs describe: the sentence-template expander,
locale resource loader, dialog/prompt renderer, language matching, the message
envelope, `Session`/`SessionManager`, context gating, `IntentBuilder`, the
`SpecMessage` topic vocabulary, and the `ovos-spec-lint` locale linter. Depend
on it instead of reimplementing these pieces. See
[ovos-spec-tools](spec-tools-lib.md) for the full primitive table and usage.

## ovos-test-harness: the conformance suite

[ovos-test-harness](spec-test-harness.md) is the executable counterpart of the
specs. It pins an exact combination of OVOS repos (`ovos-core`,
`ovos-workshop`, `ovos-bus-client`, pipeline plugins, fixture skills) and runs
the full conformance suite against that real, running stack. It records a
pass/`xfail`/fail verdict per normative clause. Maintainers also use it to
pre-flight an unmerged cross-repo change before merge. See
[ovos-test-harness](spec-test-harness.md) for the coverage model and how to
pre-flight a change.

## Adopting the spec namespace: without a flag day

The specs rename many bus topics into the `ovos.*` namespace. Migrating an
ecosystem of independently-released repos to new topic names all at once is
impossible, so `ovos-bus-client` bridges old and new names automatically and
incrementally. `ovos-spec-tools` owns the **vocabulary** of that mapping
(`SpecMessage` / `MIGRATION_MAP`). The runtime bridge itself lives in
`ovos-bus-client`. See [Bus namespace migration](bus-namespace-migration.md)
for the full mechanism, the on/off switches, and the pending removal of the
bridge.

---
**Read next:** [ovos-spec-tools](spec-tools-lib.md) · [ovos-test-harness](spec-test-harness.md) · [Bus namespace migration](bus-namespace-migration.md)
**Related:** [Formal Specifications](architecture-specs.md) · [MessageBus Service](bus-service.md) · [Intent Service](intent-service.md) · [Core Libraries](core-libraries.md)
