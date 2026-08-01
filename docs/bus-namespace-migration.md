# Bus namespace migration

!!! abstract "In a nutshell"
    The [Formal Specifications](architecture-specs.md) renamed many legacy bus topics into the
    `ovos.*` namespace. `ovos-bus-client` bridges old and new names automatically, so producers
    and consumers can each switch at their own pace. The bridge is a pending removal — see the
    warning below.

## Namespace migration

The [Formal Specifications](architecture-specs.md) rename many bus topics into
the `ovos.*` namespace, for example `recognizer_loop:utterance` →
`ovos.utterance.handle` and `complete_intent_failure` → `ovos.intent.unmatched`
(the full list is the [legacy ↔ spec table](bus-events.md#legacy-spec-migration)).
A few families, such as the `mycroft.skill.handler.*` / `ovos.intent.handler.*`
trio, are deliberately **not** bridged. See that page's "Not bridged" note.
Renaming a topic across an
ecosystem of independently-released repos cannot happen in one coordinated step.
So **`ovos-bus-client` migrates automatically and incrementally**. The legacy
and the new names interoperate transparently while the ecosystem moves over.

The canonical legacy to spec topic map lives in the `NamespaceTranslator` from
[`ovos-spec-tools`](spec-tooling.md), and each `MessageBusClient` applies it on the
**receive** side, not by putting a second copy on the wire:

```mermaid
sequenceDiagram
    participant Producer
    participant Bus as ovos-messagebus
    participant Client as BusClient<br/>(any process)
    participant LegacyHandler as legacy topic<br/>handler
    participant SpecHandler as ovos.* topic<br/>handler

    Producer->>Bus: emit(recognizer_loop:utterance)
    Bus->>Client: broadcast<br/>recognizer_loop:utterance
    Client->>Client: on_message:<br/>NamespaceTranslator lookup
    Client->>LegacyHandler: dispatch<br/>recognizer_loop:utterance
    Client->>SpecHandler: locally re-dispatch<br/>ovos.utterance.handle
```

*Diagram: a producer emits the legacy recognizer_loop:utterance topic, the bus broadcasts it unchanged, and each receiving MessageBusClient uses the NamespaceTranslator to dispatch it to both the legacy handler and, re-dispatched locally, the spec ovos.utterance.handle handler.*

- A single logical `emit()` sends exactly **one** message over the websocket: the topic the
  caller actually chose.
- When that message arrives back over the websocket (to every connected client, including the
  sender), each client's `on_message` handler locally re-dispatches it under its counterpart
  topic(s) too, using the translator to reshape the payload where the shape changed. This is a
  listener-delivery convenience *inside each process*, not a second bus message. The broadcast
  server never sees or re-broadcasts a counterpart frame.
- **listen**: subscribing to *either* name (`bus.on(...)`) also delivers the counterpart, with
  **de-duplication** so a handler that would match both fires exactly once.

The result: a producer and a consumer can each switch from a legacy topic to its `ovos.*`
spec name **in any order, with no coordination**, without every component switching at once.

### Turning the bridges off

Each direction is independently controllable (default `true`), via environment
variable or bus configuration:

| Direction | Env var | Config key | Effect |
|---|---|---|---|
| modernize | `OVOS_BUS_MODERNIZE` | `modernize` | a received **legacy** topic is also locally re-dispatched under its `ovos.*` counterpart |
| emit_legacy | `OVOS_BUS_EMIT_LEGACY` | `emit_legacy` | a received **`ovos.*`** topic is also locally re-dispatched under its legacy counterpart |

Because the bridging happens per-process on receive, turning a direction off only stops that
process from locally delivering the counterpart to its own handlers. A deployment whose
components all speak `ovos.*` can set `emit_legacy=false` once no local handler still needs
the legacy delivery, and disable `modernize` once no legacy producers remain.

!!! warning "The bridge is scheduled for removal"
    [ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272) is an
    open kill-switch pull request that deletes the bridge entirely: after it merges,
    clients speak `ovos.*` spec topics and nothing else, and setting the `modernize` /
    `emit_legacy` flags raises `RuntimeError`. Its stated merge condition is a fleet
    already upgraded to spec topics. Migrate remote consumers to the spec names ahead of
    it. See [Upcoming Changes](upcoming-changes.md).

!!! note "Bridged is not the same as conformant"
    [`ovos-test-harness`](spec-tooling.md) asserts spec behavior on the
    canonical `ovos.*` topics. A component becomes *spec-conformant* once it
    speaks `ovos.*` directly. The bridge keeps it **interoperable** in the
    meantime, but it does not make it conformant.

---
**Read next:** [messagebus Service](bus-service.md)
**Related:** [Bus Events Reference](bus-events.md) · [Spec Tooling](spec-tooling.md) · [Upcoming Changes](upcoming-changes.md)
