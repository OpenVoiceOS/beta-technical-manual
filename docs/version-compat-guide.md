# Writing Version-Compatible Skills and Plugins

!!! abstract "In a nutshell"
    OVOS ships as a dozen independently versioned packages, not one product with one
    version number. If you maintain a skill or plugin that must run on more than one
    of those version combinations at once, this page lists the four sanctioned ways to
    write that compatibility, with a worked example for each drawn from a real break
    described in [Updating From Older OVOS](updating-from-older-ovos.md). It also says
    when to stop shimming and pin a dependency floor instead.

## When to bother

Most authors should not carry compatibility code. If you publish a skill or plugin
against the current `ovos-workshop`/`ovos-plugin-manager` API and pin a sane floor in
`pyproject.toml`, that is enough. Write compatibility code only when you have a real
reason to support more than one OVOS generation from the same codebase:

- **Distro-packaged older cores.** raspOVOS images, Debian/Arch packages, or other
  fixed snapshots that lag behind the `testing` channel (see
  [Release Channels](release-channels.md)) and cannot be bumped on demand.
- **A fleet you do not fully control.** HiveMind satellites, community devices, or any
  install base where you cannot force every node to upgrade together.
- **A published plugin with many downstream users.** A wake word or TTS plugin on PyPI
  gets installed against whatever core each user already runs. Breaking one generation
  to support another has a real cost you do not pay if you just track latest.

If none of these apply, track the current `dev` API and let your dependency floor do
the work described in [Dependency-floor discipline](#dependency-floor-discipline)
below.

## The four sanctioned techniques

### a. Import-location fallback

Use this when a symbol moved between packages or between modules inside the same
package, and both the old and new location can be imported side by side without
conflict. Try the new path first, fall back to the old one on `ImportError`.

`ovos-workshop` `5.0.0` (2025-06-07) moved `converse()` off `OVOSSkill` and onto a
mixin, `ConversationalSkill`. Before `5.0.0`, a skill overrode `converse()` directly on
`OVOSSkill`. From `5.0.0` on, the mixin must also be inherited or the override is
silently never called by the pipeline (`ovos-workshop` `f725f5e`, #339):

```python
from ovos_workshop.skills import OVOSSkill

try:
    from ovos_workshop.skills.converse import ConversationalSkill
    _BASES = (OVOSSkill, ConversationalSkill)
except ImportError:
    # pre-5.0.0: converse() lived directly on OVOSSkill, no mixin exists
    ConversationalSkill = object
    _BASES = (OVOSSkill,)


class MySkill(*_BASES):
    def can_converse(self, message) -> bool:
        # only called when ConversationalSkill is present; harmless no-op otherwise
        return True

    def converse(self, message=None):
        ...
```

The same pattern applies to the `ovos-utils` `0.1.0` gutting (released 2024-09-10; deletion commit `3a77617`, 2023-12-29),
which deleted almost every helper that had accumulated in `ovos_utils` since the
Mycroft era. For example `get_mycroft_bus`/`wait_for_reply` moved to
`ovos_bus_client.util`:

```python
try:
    from ovos_bus_client.util import get_mycroft_bus, wait_for_reply
except ImportError:
    # pre-0.1.0 (before 2024-09-10): helpers still lived in ovos_utils
    from ovos_utils.messagebus import get_mycroft_bus, wait_for_reply
```

### b. Version-gated behavior

Use this when the two generations cannot both exist as importable symbols at once, for
example a renamed method on the same class, or a whole class that got deleted rather
than moved. Every OVOS package ships a `version.py` module with integer constants
(`VERSION_MAJOR`, `VERSION_MINOR`, `VERSION_BUILD`, `VERSION_ALPHA`) between
`START_VERSION_BLOCK`/`END_VERSION_BLOCK` markers. Import the constants from the
package that owns the break and branch on them. This needs no extra dependency and no
string parsing.

`ConversationalSkill.can_answer` was renamed to `can_converse` in `ovos-workshop`
`7.0.0` (`1fdd532`, #348), one day after the `can_answer` name shipped in `5.0.0`.
Define both names and delegate one to the other so callers on either generation find
the method they expect:

```python
from ovos_workshop.version import VERSION_MAJOR as WORKSHOP_MAJOR

class MySkill(OVOSSkill, ConversationalSkill):
    def can_converse(self, message) -> bool:
        return True

    if WORKSHOP_MAJOR < 7:
        # ovos-workshop 5.0.0-6.0.1 called this method can_answer
        def can_answer(self, message) -> bool:
            return self.can_converse(message)
```

For a break that landed inside a minor or build release, compare the tuple:

```python
from ovos_workshop import version

if (version.VERSION_MAJOR, version.VERSION_MINOR) >= (7, 1):
    ...  # post-break behavior
```

The `CommonQuerySkill` removal is the sharper case: the class itself is gone in
`ovos-workshop` as of `6382d0a` (#400, 2026-04-08, pre-`8.0.0`), so you cannot import
it unconditionally even inside a `try`/`except` used only for typing. Prefer the
modern `@common_query` decorator (`ovos_workshop.decorators.common_query`) when it
exists, and only import the deprecated base class on cores old enough to still ship
it:

```python
from ovos_workshop.decorators import common_query

try:
    from ovos_workshop.skills.common_query_skill import CommonQuerySkill
    _HAS_LEGACY_CQS = True
except ImportError:
    # dropped in ovos-workshop 6382d0a (2026-04-08), pre-8.0.0
    CommonQuerySkill = OVOSSkill
    _HAS_LEGACY_CQS = False


class MySkill(OVOSSkill, CommonQuerySkill if _HAS_LEGACY_CQS else OVOSSkill):
    @common_query()
    def answer_common_query(self, utterance, lang):
        # modern cores dispatch through the decorator; on cores old enough to
        # still ship CommonQuerySkill, its own CQS_match_query_phrase/CQS_action
        # abstract methods must also be implemented for that path to fire
        ...
```

### c. Signature both-ways compat for plugin authors

Use this when a plugin template method's argument list changed. Give the parameter a
default so the same method body satisfies both the old caller, which passes an
argument, and the new caller, which calls with none.

`ovos-plugin-manager` 2.0 changed the `HotWordEngine` contract:
`found_wake_word(audio_data)` became `found_wake_word()`, with audio now fed
separately through `update(chunk)`. Both `mycroft-classic-listener` (`19d9961`, #12,
2026-01-09) and `ovos-simple-listener` (`34e2219`, #20, 2026-01-23) landed the
caller-side change on the same opm bump, so a plugin still expecting one positional
argument gets called with zero and raises `TypeError` on any updated listener:

```python
from ovos_plugin_manager.templates.hotwords import HotWordEngine


class MyWakeWordPlugin(HotWordEngine):
    def update(self, chunk: bytes) -> None:
        # opm 2.0+ callers feed audio here; older callers never call this,
        # so buffer it yourself and fall back to accumulating in found_wake_word
        self._buffer = chunk

    def found_wake_word(self, audio_data=None) -> bool:
        # opm 2.0+: called with no arguments, audio already fed via update()
        # pre-2.0: called with the raw audio chunk directly
        chunk = audio_data if audio_data is not None else self._buffer
        return self._detect(chunk)
```

### d. Config/data both-ways compat

Use this when a config key or data-file schema was renamed and you cannot control
whether every consumer on your fleet has upgraded yet. Read (or accept) both the old
and the new key, preferring the new one.

Persona files are the shipped example: solver-style handler lists used the key
`"solvers"`. Newer configs use `"handlers"`, and `ovos-persona` accepts both so a
persona JSON shared across a mixed fleet keeps working during migration (see
[Building Agent Plugins](building-agent-plugins.md#migrating-a-solver-plugin-to-an-agent-engine)):

```json
{
  "name": "MixedPersona",
  "handlers": ["my-new-chat-engine"],
  "solvers": ["ovos-solver-failure-plugin"]
}
```

If you write code that loads persona files yourself instead of relying on
`ovos-persona` to do it, read both keys and merge them, new key first:

```python
handlers = persona_cfg.get("handlers", []) + persona_cfg.get("solvers", [])
```

The OCP-to-`ovos-media` config split is the same pattern at the deployer-config level.
`ovos-media` `89a50c0` (#19, 2024-03-29) renamed the config root key `OCP` to `media`
and flipped the MPRIS toggle's polarity (`disable_mpris`, on by default, became
`enable_mpris`, off by default). Reading both root keys keeps a shared `mycroft.conf`
working across mixed-version devices:

```python
media_cfg = config.get("media", config.get("OCP", {}))
enable_mpris = media_cfg.get("enable_mpris", not media_cfg.get("disable_mpris", True))
```

## Dependency-floor discipline

Every technique above adds branches you must test and maintain. Before reaching for
one, ask whether a `pyproject.toml` floor or cap is the honest alternative. OVOS
follows a deprecate-then-drop lifecycle almost everywhere (see [How OVOS versions
break](updating-from-older-ovos.md#how-ovos-versions-break)): active, then deprecated
but functional with a warning, then dropped. If the break you are worried about is
still in its deprecated-but-functional phase, you often do not need a shim at all,
just a floor that excludes the versions before the replacement existed:

```toml
[project]
dependencies = [
    "ovos-workshop>=5.0.0",   # ConversationalSkill mixin required, no pre-5.0 shim
    "ovos-plugin-manager>=2.0.0",  # found_wake_word() no-arg contract only
]
```

Shim when your users genuinely span both sides of a drop you cannot control (a distro
snapshot, a fleet you do not own). Pin a floor when you control your own install
target and would rather drop old-version support than carry branches forever. A floor
is also the only honest choice once a technique above stops being possible, for
example after `CommonQuerySkill` is fully removed and there is no import to fall back
to.

## Testing across versions

Test every branch you ship, not just the current one. A compat shim with no test for
its old-version branch is dead code with a false sense of safety.

The manual's [constraints files](release-channels.md#choosing-a-release-channel)
pattern gives you a ready-made two-version CI matrix. Install against the `testing`
channel for the current behavior and against a pinned older constraints snapshot (or
an explicit old-version pin) for the legacy branch:

```yaml
# .github/workflows/test-compat.yml
name: Compat matrix
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        include:
          - name: current
            constraints: https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-testing.txt
          - name: legacy
            constraints: https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install (${{ matrix.name }})
        run: uv pip install ".[test]" -c "${{ matrix.constraints }}"
      - name: Run tests
        run: pytest test/
```

Write one test per branch of every compat shim: one that asserts the new-path
behavior when the modern symbol is importable, and one that asserts the fallback
fires correctly when it is patched out or the modern symbol is absent. A shim that
only ever runs its new-path branch in CI has never actually tested the old-version
support it claims to offer.

## When NOT to do this

Some breaks are not shimmable, and trying anyway produces code that looks safe and
is not.

**Wire behavior scheduled for removal.** The `ovos-bus-client` legacy-topic dual-emit
bridge (`modernize`/`emit_legacy`, both default ON from `e25ab12`, 2026-06-25) is
scheduled for deletion by the open kill-switch
[ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272). After
it merges, `MessageBusClient` speaks OVOS-MSG-1 spec topics only and passing
`emit_legacy`, `modernize`, or `intent_reemit_blanket` to the constructor raises
`RuntimeError`.

There will be no client-side shim for this: migrate remote clients and
satellites to `ovos.*` spec topics while the bridge still covers both spellings. Do
not write new code that shims legacy topic names. See [The bus-client
legacy-topic dual-emit and its removal](migration-bus-dual-emit.md)
for the full migration path.

**Pre-fork mycroft-core.** The `MycroftSkill` compat metaclass that let classic
Mycroft skills load under OVOS was removed in `ovos-workshop` `2d684a1` (#235,
2024-10-15). There is no import-fallback or version gate that restores it, because the
whole loading and initialization model changed, and it is not only a symbol location. If you are
still carrying a skill written against `mycroft-core`, that is a port, not a compat
shim. Follow [Migrating From Mycroft](migrating-from-mycroft.md) instead.

---
**Read next:** [Skill Design Best Practices](skill-best-practices.md)
**Related:** [Migrating from Mycroft](migrating-from-mycroft.md) · [Skill Metadata File](skill-json.md) · [Runtime Requirements in OVOS](skill-runtime-requirements.md) · [Maturity Scale](maturity.md)
