# Maturity Scale

!!! abstract "In a nutshell"
    Many pages in this manual carry a **maturity** badge. It tells you how much weight a
    component can bear in a real deployment: a rock-solid dependency, a usable-but-moving
    target, or an early experiment that may change under you. The rating comes from the
    health of the component's source repository, not its version number. See the levels
    below, then read the criteria under [Why it's not the version number](#why-its-not-the-version-number) for the detail.

## The levels

| Badge | Level | What it means for you |
|---|---|---|
| ⬤⬤⬤⬤⬤ | **Mature** | Long-lived, well-proven, widely deployed, actively maintained. Depend on it freely. |
| ⬤⬤⬤⬤◯ | **Stable** | Established and production-ready, maintained, with real docs. Safe for production; API changes are rare and announced. |
| ⬤⬤⬤◯◯ | **Beta** | Works and is in real use, but younger or still settling — expect the occasional breaking change. Fine to build on with an eye on releases. |
| ⬤⬤◯◯◯ | **Alpha** | Functional but early: the API churns, coverage is thin, and it may change substantially. Try it, pin it, don't build a product on it yet. |
| ⬤◯◯◯◯ | **Proof-of-concept** | A spike or reference implementation. It may work, but it is not maintained as a product and may disappear. For exploration only. |
| ⚠️ | **Deprecated** | The repository is archived or no longer maintained. Avoid it for new work; the page notes what replaces it where a replacement exists. |

!!! info "How maturity is judged"
    A component's rating comes from the **health of its source repository**, not its version
    number. OVOS packages are versioned continuously from conventional commits. A `0.x`
    version says little about how well-proven the code is. A foundational library can sit at
    `0.8` with hundreds of releases, while a brand-new experiment can ship a `1.0`. Instead, the
    rating weighs signals that track maturity: how long the repository has existed,
    how actively it is maintained (recent commit activity), the volume of open issues and pull
    requests it fields, and whether it carries real in-repo documentation and tests.

!!! warning "Maturity is not a recommendation"
    A badge rates how *reliable and maintained* a component is. It does not rate whether it is
    the right choice for your use case. A component can be **Mature** (rock-solid and well-proven)
    and still be the wrong tool for a given job. A page may recommend against broad use of
    something whose code is perfectly stable. Always read the page's own recommendation alongside
    the badge.

## Why it's not the version number

A version like `1.2.0` is set by the release pipeline from commit conventions. A single `feat:`
commit can move a `0.x` library to the next minor, and a `chore!:` moves it to a new major. That
makes versions a precise record of *what changed*, but a poor proxy for *how much you can rely on
it*. Repository health is a better signal: age, sustained maintenance, an engaged issue tracker,
and in-repo docs. It answers the only question a maturity badge should answer: **if I depend on
this, will it still be here and still work in a year?**

Ratings are a point-in-time judgement and move as repositories do. Treat a badge as guidance, not
a guarantee.

!!! note "A release channel is not a maturity guarantee"
    A [release channel](release-channels.md) (stable/testing/alpha) only bounds the version
    range of `ovos-core` itself. It says nothing about the maturity of the individual
    plugins it happens to pull in. A stable-channel install can still resolve to a
    **Beta**-rated (or even Alpha-rated) plugin as a dependency. Check each plugin's own
    maturity badge in the manual before relying on it. Do not assume "stable
    channel" means "every component is production-grade."

---
**Read next:** [Plugin Manager](plugin-manager.md) · [Concepts Overview](concepts-overview.md)
**Related:** [Formal Specifications](architecture-specs.md) · [Manual & Advanced Install](release-channels.md) · [High-level Overview](architecture-overview.md)
