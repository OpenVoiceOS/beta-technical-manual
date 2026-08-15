# Updating Remote Bus Clients From Older OVOS

## In a nutshell

This page is for anyone connecting to the bus as a separate process:
HiveMind satellites, custom dashboards, external automation, or any code
that parses raw wire messages instead of going through a skill. Entries
are in date order: start at the version you are currently running and
read forward to your target version. For the Big-ticket migrations (the
changes with the widest blast radius, including the bus-client dual-emit
bridge), see
[Updating from Older OVOS](updating-from-older-ovos.md#big-ticket-migrations).

## If you consume the message bus remotely (HiveMind and other clients)

### `mycroft-bus-client` package retirement (package-level, not wire-level)

Every repo in the org switched its dependency and imports from the
upstream `mycroft-bus-client` package to `ovos-bus-client`. This is a
Python import change, not a wire change: listed here because it is the
package-level ancestor of the topic-level migration above.

- Migration: `pip install ovos-bus-client`. `from mycroft_bus_client
  import Message` → `from ovos_bus_client.message import Message` (or
  `from ovos_bus_client import MessageBusClient`).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before 2023-04 | |
| Deprecated but functional | isinstance compat kept briefly, `04def5d` | |
| Dropped | starting `9396c71` (2023-04-05) | ovos-bus-client's own extraction |

The ecosystem-wide dependency swap landed at `b1a9d39e16` (2023-04-11) in
`ovos-core`, and matching one-line swaps in `ovos-audio` (`426a48b`) and
`ovos-messagebus` (`a1bc1c1`), all within the same week.

### GUI wire protocol: template rework in development, nothing shipped

A template-based GUI wire protocol (OVOS-GUI-1 §3-4: `gui.value.set` +
`gui.page.show` with a `PageTemplates` enum and `show_*` helpers) is being
built on unmerged `ovos-bus-client` branches. None of it is on `dev`: the
shipping `GUIInterface` and `EnclosureAPI` wire behavior is unchanged, and
no migration is needed yet. Watch the `ovos-bus-client` release notes
before depending on either the old primitives staying public or the new
templates existing.

### HiveMind agent protocol and messagebus-solver removed from ovos-bus-client

`ovos_bus_client/hpm.py` (`OVOSAgentProtocol`/`OVOSProtocol`) and
`ovos_bus_client/opm.py` (the `neon.plugin.solver`-based chat class) were
deleted, along with the `hivemind.agent.protocol` entry point.

- Migration: `from ovos_bus_client.hpm import OVOSAgentProtocol` → install
  `hivemind-ovos-agent-plugin` and import from there (the entry-point
  *name* is preserved, so HiveMind-core configs need no change, only the
  dependency install). `ovos_bus_client.opm` (QuestionSolver-based chat) →
  `ovos-messagebus-chat-plugin` (implements `ChatEngine`, uses
  `SessionManager` for multi-turn state).
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | before `d526e99` | |
| Deprecated but functional | unverified | |
| Dropped | `2.0.0a1` | (ovos-bus-client `d526e99`, #207, 2026-05-18) |

### Per-service legacy topic migrations (spec-bus adoption, 2026-06)

Every listener/core service in the org migrated its own emit/listen sites
to `ovos_spec_tools.SpecMessage` constants around the same time. Wire
compatibility with legacy producers and consumers comes from the
`ovos-bus-client` bridge (receive-side re-dispatch plus marked legacy wire
twins for canonical emits), not from any per-service config flag:

| Legacy topic | Spec topic | Landed in |
|---|---|---|
| `recognizer_loop:utterance` | `ovos.utterance.handle` (`SpecMessage.UTTERANCE`) | ovos-core `1672e35ed0` (#772/#775) · ovos-dinkum-listener `d9dc04e` (#232) · ovos-simple-listener `b8326fa` (#26) · mycroft-classic-listener `4458a3f` (#23, `1.0.0a1`) |
| `mycroft.awoken` | `SpecMessage.LISTENER_AWOKEN` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `recognizer_loop:record_begin` / `record_end` | `SpecMessage.LISTENER_RECORD_STARTED` / `_ENDED` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `mycroft.mic.listen` | `SpecMessage.MIC_LISTEN` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` · ovos-audio `d730aef` (#165, `2.0.0a1`) |
| `recognizer_loop:audio_output_start` / `_end` | `SpecMessage.AUDIO_OUTPUT_STARTED` / `_ENDED` | ovos-audio `d730aef` (#165, `2.0.0a1`, the emit side) · ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `recognizer_loop:sleep` | `SpecMessage.LISTENER_SLEEP` | ovos-dinkum-listener `d9dc04e` · mycroft-classic-listener `4458a3f` |
| `mycroft.stop`, per-skill stop pings, `complete_intent_failure` | `ovos.stop`, `ovos.stop.ping`, `ovos.intent.unmatched` | ovos-core `690cb42` (#802, first tag `3.0.0a1`) |
| `stop.openvoiceos.stop.response` | removal pending, not replaced | ovos-core `2b05201705`, **unmerged** (feature branch): would stop `StopService` registering itself as a skill. On current `dev` the legacy stop service still registers as `stop.openvoiceos`; once this lands, do not count it as a participating skill in custom global-stop aggregation |

- Migration: subscribe to the `ovos.*` spec topics; the bus-client bridge keeps
  legacy producers and consumers working in the meantime (its own flags are
  `OVOS_BUS_MODERNIZE` / `OVOS_BUS_EMIT_LEGACY` / `OVOS_BUS_WIRE_LEGACY_TWINS`,
  see [Bus Namespace Migration](bus-namespace-migration.md)). Prefer
  `ovos_spec_tools.SpecMessage.*` constants over hardcoded topic strings
  going forward, since their literal values are not always the same as
  the legacy strings they replace.
Lifecycle:

| Phase | Version | Notes |
|---|---|---|
| Active | legacy-only, before the per-service SpecMessage migrations (2026-06) | |
| Deprecated but functional | bridged: receive-side re-dispatch everywhere, plus wire twins for canonical emits since bus-client `2.8.3a1` | |
| Dropped | no hard drop has shipped | `ovos-bus-client`'s bridge removal is the unmerged kill-switch [PR #272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272) (commit `f1a481d` on its branch) |

No `legacy_namespace` flag exists in shipped `ovos-core`: the branch that proposed
it (`f4c00d90b2`/`f9862a760e`) was superseded by the unconditional spec-topic emits
plus the bus-client bridge. Shipped `ovos-core` listens only on the spec topics;
a legacy `recognizer_loop:utterance` from an old satellite reaches it through the
bridge, not through any core-side compatibility flag.

### SESSION-1 spec adoption: shipped

`SessionManager` enforces one live `Session` object per id (singleton, `7a2e39f`,
#249). Code holding a stale `Session` reference expecting it to stay independent
from the manager's canonical instance will observe shared-state changes it did
not make.

The rest of the SESSION-1 rebuild has shipped too: `SessionManager` subclasses
the `ovos-spec-tools` session registry (`d453cac`, #254, first tag `2.6.2a2`),
session TTL/pruning is deprecated (`prune_sessions` logs a deprecation warning),
and `serialize()` omits empty list-valued override fields per SESSION-1 §3.4, so
absence of a key like `pipeline` on the wire means "deployment default".

- Migration: read sessions through `Session.deserialize()`/the `Session`
  class, not by holding raw references or indexing the raw wire dict.

### Legacy `mycroft.*`/`recognizer_loop:*` topic bridge scheduled for removal

See [The bus-client legacy-topic dual-emit and its removal](migration-bus-dual-emit.md)
for the full timeline. The short version for remote clients: the
bridge is on by default in current releases, and the open kill-switch
[ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272)
deletes it once the fleet has migrated. After it merges,
`MessageBusClient` speaks OVOS-MSG-1 (`ovos.*`) topics only, and a
HiveMind satellite still emitting or expecting legacy topics silently
stops being received. Migrate ahead of it.

---

**Read next:** [Version-Compatible Skills & Plugins](version-compat-guide.md) · [Upcoming Changes](upcoming-changes.md)
**Related:** [Updating from Older OVOS](updating-from-older-ovos.md) · [Bus Service](bus-service.md)
