# ovos-test-harness

!!! note "Maturity: Beta ⬤⬤⬤◯◯"
    In real use but still settling. Watch releases for the occasional breaking change. Rated by [repository health](maturity.md), not version.

!!! abstract "In a nutshell"
    [**ovos-test-harness**](https://github.com/OpenVoiceOS/ovos-test-harness) is the
    executable counterpart of the [Formal Specifications](architecture-specs.md). It
    pins an exact combination of OVOS repos, runs a real stack, and asserts one
    observable bus behavior per normative clause. Use it to pre-flight a cross-repo
    change before merge, not just to check one repo in isolation.

??? info "Formal specification"
    This suite proves conformance to the **[OpenVoiceOS/architecture](https://github.com/OpenVoiceOS/architecture)** specs. See the [spec index](architecture-specs.md).

---

[**ovos-test-harness**](https://github.com/OpenVoiceOS/ovos-test-harness) is the
**executable counterpart** of the specs. Each test asserts one observable bus
behavior a spec mandates, against a *real running OVOS stack*. If the specs are
the law, this harness is the courtroom. It puts a concrete combination of OVOS
repos on trial against the law and returns a verdict per normative clause:
**pass**, **`xfail`** (a documented gap), or **fail**.

## Why a separate repo

A single spec clause is only satisfied when a
*combination* of branches across a dozen repos lines up: `ovos-core`,
`ovos-workshop`, `ovos-bus-client`, the pipeline plugins, fixture skills. You
cannot prove that from inside any one repo, because that repo's CI installs only
its own package plus whatever pip resolves, and pip is free to downgrade a
sibling out of the exact combination you are trying to validate.

## The model

The harness is **not a package**. There is no `pip install .`.
Its [`requirements.txt`](https://github.com/OpenVoiceOS/ovos-test-harness) is the
**stack under test**: every line pins one repo to an exact git ref or version, so
CI never re-resolves and never downgrades a component. Each test then:

- imports the spec vocabulary from [`ovos-spec-tools`](spec-tools-lib.md), so a topic name is *provably spec-defined* rather than a magic string.
- drives and captures the live bus through [`ovoscope`](https://github.com/OpenVoiceOS/ovoscope) (see [Testing Skills](ovoscope-overview.md)).
- asserts the spec-mandated behavior and records pass / `xfail` / fail.

## Coverage

All 21 specs on the architecture `dev` branch currently have
conformance suites (SESSION-1 and SESSION-2 share one suite. INTENT-4 has both an
orchestrator suite and a per-plugin registration-compliance suite). The
authoritative spec→suite traceability matrix lives in the repo's
[`docs/coverage.md`](https://github.com/OpenVoiceOS/ovos-test-harness/blob/dev/docs/coverage.md).
Documented conformance gaps are recorded as `xfail` entries and catalogued in
[`docs/known-gaps.md`](https://github.com/OpenVoiceOS/ovos-test-harness/blob/dev/docs/known-gaps.md).

## Pre-flighting a cross-repo change

To certify an unmerged combination,
maintainers pin the candidate branches in `requirements.txt` and open a harness
PR. CI then installs exactly that stack and runs the full conformance suite
against it, flipping each ref to `@dev` as it merges. One structural limit: two
branches of the *same* repo cannot both be installed, so pick one ref per repo.

This is where an implementation is **proven to conform** to the merged
architecture specs. It is the bridge between the prescriptive Markdown and the code
that has to honour it.

---
**Read next:** [Specification Tooling](spec-tooling.md) · [ovos-spec-tools](spec-tools-lib.md)
**Related:** [Formal Specifications](architecture-specs.md) · [Testing Skills](ovoscope-overview.md) · [MessageBus Service](bus-service.md)
