# Migrating Bus Topics Off the Legacy Namespace

!!! abstract "In a nutshell"
    Remote/HiveMind operators and anyone producing or consuming bus
    messages are affected. `ovos-bus-client` 2.x added a transitional
    bridge that accepts both legacy and spec topics, and it is on a path to
    removal. Fix it by moving every producer and consumer to `ovos.*` spec
    topics now, while both spellings still work.

    This page is the migration checklist. For how the bridge works and its
    flags, see [Bus Namespace Migration](bus-namespace-migration.md).

!!! warning ""Dual-emit" is literal again for canonical emits"
    The bridge translates incoming messages on the **receive** side (`modernize`), and —
    since bus-client 2.8.3a1 — a canonical emit of any mapped topic also puts a real,
    marked legacy-spelled twin frame on the wire, so pre-spec wire listeners keep hearing
    it. One canonical `emit()` is therefore **two** websocket messages by default; disable
    with the `OVOS_BUS_WIRE_LEGACY_TWINS` env var or `websocket.wire_legacy_twins` config
    key (added 2.8.4a1) only when no pre-spec listener is on the bus. Legacy-spelled emits
    are not twinned; their canonical counterpart is receive-side only.

### The bus-client legacy-topic dual-emit and its removal

This is the change every remote/HiveMind operator needs to plan for, and
it is still mid-flight: the project built a transitional bridge so a
fleet with some satellites upgraded and some not could keep working while
topics migrated from legacy `mycroft.*`/`recognizer_loop:*` spellings to
the `ovos.*` spec namespace, then spent several follow-up commits fixing
bugs in that bridge itself, including one that doubled every message on
the raw firehose for about a week. The bridge is on by default in current
releases; its planned removal sits on an unmerged pull request gated on
the fleet already being upgraded, so operators are meant to move onto
`ovos.*` topics now, while both spellings still work, rather than wait for
the kill switch to force the issue.

The commit-level history of that bridge:

1. `679f120` (#228, 2026-06-25): opt-in (default OFF) dual-emit + dedup bridge.
2. `e25ab12` (#230, 2026-06-25): split into two flags, **both default ON**
   during the migration window: `modernize` (env `OVOS_BUS_MODERNIZE`,
   config `websocket.modernize`) and `emit_legacy` (env
   `OVOS_BUS_EMIT_LEGACY`, config `websocket.emit_legacy`).
3. `4a08946` (#232, 2026-06-25): dedup logic delegated to
   `ovos_spec_tools.NamespaceTranslator` (shared with `FakeBus`).
4. `0f0a241` (#258, 2026-07-03): fixes a bug where the dual-emit doubled
   every message on the raw `on_message` firehose between #230 and this fix.
5. Planned removal: the open kill-switch pull request
   [ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272)
   (commit `f1a481d` on its branch, not merged to `dev`) deletes the bridge
   entirely: `MessageBusClient` then speaks OVOS-MSG-1 spec topics only, the
   `emit_legacy`/`modernize`/`intent_reemit_blanket` flags are deleted, and
   passing them raises `RuntimeError`. Its stated merge condition is a fleet
   already upgraded. See [Upcoming Changes](upcoming-changes.md).

Migration: move every producer and consumer to `ovos.*` spec topics now,
while the bridge still covers both spellings. Remove explicit
`emit_legacy`/`modernize`/`intent_reemit_blanket` arguments from your
`MessageBusClient` construction so the eventual flag deletion cannot break
you. The mapping tables (`ovos_spec_tools.MIGRATION_MAP`, `SPEC_TO_LEGACY`)
remain available for migration tooling.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Legacy-only `mycroft.*`/`recognizer_loop:*` topics, no bridge | before `679f120` (2026-06-25) | n/a | superseded by dual-emit |
| Dual-emit bridge (`modernize`/`emit_legacy`, both default ON) | `e25ab12` (2026-06-25) | current releases (bridge on by default) | pending: [ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272), unmerged |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Remote Clients](updating-remote-clients.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
