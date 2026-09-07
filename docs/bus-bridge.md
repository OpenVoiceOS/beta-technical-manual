# Bus Bridges

!!! abstract "In a nutshell"
    A bridge is whatever component sits between the internal messagebus and
    an external channel, a satellite connection, a chat gateway, a link to
    another deployment, and makes messages on one side reach the other. It
    does two jobs and nothing more: it gives every external participant a
    stable address on the bus, and it carries their traffic across without
    changing what it means. Everything else people associate with a
    bridge, access policy, per-participant preferences, multi-device
    topologies, falls out of composing that address and that unchanged
    traffic with the rest of the platform's specifications.

??? info "📐 Formal specification"
    **[OVOS-BRIDGE-1 — Bus Bridge & Opaque Relay](https://github.com/OpenVoiceOS/architecture/blob/dev/bridge-1.md)**. Builds on [OVOS-MSG-1](https://github.com/OpenVoiceOS/architecture/blob/dev/msg-1.md), [OVOS-SESSION-1/2](session.md), and [OVOS-CONTEXT-1](context.md). See also the [spec index](architecture-specs.md).

## What a bridge actually does

To the internal bus, a bridge looks like the source of every message its
external participants send. To an external participant, the bridge is
its entire connection to the rest of the platform. A bridge treats what
arrives from outside as opaque: it does not need to understand a
participant's protocol beyond turning it into conformant bus messages and
back.

Two obligations make this work:

- **Give every participant a stable address.** On first contact the
  bridge stamps a unique identifier into the outgoing message's
  `source`, generating one if the participant has none of its own. Every
  reply routes back to that identifier, so two participants sharing the
  same session, including the reserved device-local session, are still
  told apart.
- **Carry context unchanged.** Everything in a message's context crosses
  the bridge exactly as it arrived, with one narrow exception: a bridge
  is allowed to translate identifiers as messages cross the boundary (see
  below). Anything a deployment wants to do beyond that, restrict a
  participant, prefer a pipeline, seed a context entry, is a separate
  layer sitting on top of a transparent bridge, not a change the bridge
  makes on its own initiative.

A bridge that fabricates, drops, or edits a field beyond that one
exception is not doing NAT, it is impersonating the participant or the
platform.

## Identity translation (NAT)

A bridge may rewrite a participant's session identifier as it crosses the
boundary, translating between the participant's own naming and whatever
the hub-side deployment expects. This is exactly Network Address
Translation applied to session identity: each side keeps its own
namespace, and the bridge maintains the mapping between them.

The mapping is keyed by **participant**, not by connection. A participant
that disconnects and reconnects later must get back the same hub-side
identifier it held before, because state keyed on that identifier,
scheduler entries, skill registrations, a live intent context, depends
on the identifier staying stable across the gap. How the bridge
recognizes a returning participant as the same one is a deployment
concern outside the specification; that the mapping survives the
reconnect once recognized is not.

## Two ways to carry a session

A bridge relates to the sessions it carries in one of two ways, chosen
per participant:

- **Relaying.** The external participant already speaks the session
  model and manages its own state. The bridge is a transparent pipe: it
  copies the session out of the external payload on the way in and back
  in on the way out, and never inspects or edits its content on its own.
  A satellite in a hub-and-satellite mesh, or a peer deployment across a
  federation link, works this way.
- **Managing.** The external participant has no concept of a session at
  all, a chat room, an SMS gateway, anything opaque. The bridge owns the
  session lifecycle on that participant's behalf: it assigns a session
  identifier per participant, builds a session object for messages that
  arrive without one, and folds the updates it observes back into its
  own store for the next message from that same participant.

A managing bridge fronting several concurrent participants must give
each one a distinct session identifier; that distinctness is what lets
the bridge correlate the platform's response events back to the
participant that triggered them.

## Where a bridge shows up

A bridge is not one component with one job description. The same
obligations underlie several shapes a deployment can take:

- **Satellite and hub** — one or more lightweight satellites send
  utterances to a hub that owns intent matching and skill dispatch, and
  receive spoken responses and the end-of-turn session back.
- **Cascading deployments** — a local deployment runs its own pipeline
  first and only forwards to a more capable remote deployment when
  nothing local matched, carrying what it already tried as context.
- **A satellite registering its own skills** on the hub, so the hub's
  intent pool includes intents that only make sense for that one
  satellite's session.
- **TTS as a service**, where a satellite with no local speech synthesis
  asks the hub to render audio and ships it back across the bridge as
  encoded bytes instead of text.

None of these needs a protocol of its own. Each is what the bridge's two
obligations, addressing and unchanged relay, produce once combined with
the session, pipeline, and context mechanisms those pages already
describe.

## Policy at the boundary

Because a bridge carries session fields transparently, a deployment can
enforce policy simply by setting fields on the way in, no separate
protocol needed. A layer sitting at the bridge boundary can deny a
participant access to specific skills, intents, or pipeline stages by
populating the relevant denylist fields; there is no matching allowlist,
so policy can only narrow what a participant reaches, never grant it
something the platform would not otherwise offer. A participant can
likewise express a pipeline or transformer preference, and policy always
wins over preference where the two conflict.

The one rule this depends on: a boundary component that injects policy
this way must reapply it on **every** message from the governed
participant, not once at connect time. A participant is the authority
over its own session content and may legitimately send a session that
omits the injected fields on a later message; a gate that only checks
once at the start has silently stopped gating the moment that happens.

---
**Related:** [Sessions](session.md) · [Scheduled Events](scheduler-service.md) · [Bus Service](bus-service.md) · [Intent Context](context.md) · [HiveMind](hivemind-agents.md)
