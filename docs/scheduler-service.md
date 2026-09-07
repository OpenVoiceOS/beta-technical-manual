# Scheduled Events

!!! abstract "In a nutshell"
    A skill that wants something to happen later, a timer, an alarm, a
    recurring reminder, does not keep its own clock. It asks the scheduler
    to fire an event at a wall-clock instant, and goes on with its life. The
    scheduler remembers the request on disk, fires the event even if the
    device rebooted in between, and tells the owner when it missed one. From
    a skill, this is `self.schedule_event` and friends. See [Scheduling
    Events](ovos-skill.md#scheduling-events) for that API. This page
    describes what the scheduler itself guarantees underneath it.

??? info "📐 Formal specification"
    **[OVOS-SCHEDULER-1 — Scheduled Events](https://github.com/OpenVoiceOS/architecture/blob/dev/scheduler-1.md)** is prescriptive: where the shipped scheduler differs from it, the implementation is wrong. See also the [spec index](architecture-specs.md).

The scheduler is one service on the bus. Any component, a skill, a plugin,
a remote participant relayed through a [bridge](bus-bridge.md), asks it to
fire a named event at a future instant and gets that event back on the bus
when the time comes. The component does not need to stay running in the
meantime: the scheduler tracks due dates on its own and survives the
requester's restart, and its own.

## Identity and naming

A schedule belongs to the component that created it, identified by the
`skill_id` the request message carried, not by any field in the request
body. Two components can each use the id `"morning"` without colliding,
because a schedule's true identity is the pair (`skill_id`, `id`).

The event a schedule fires must be named `<skill_id>.<name>`, the owner's
own namespace plus a name it picks. A schedule can never be made to fire
an event that impersonates another component's message type, because the
namespace prefix is enforced at request time. From a skill, this
enforcement is invisible: `self.schedule_event(handler, when, name="tick")`
composes the qualified event name for you.

## Timing forms

A schedule expresses its due date in exactly one of four shapes:

- **`at`** — an absolute instant.
- **`in`** — a delay from the moment the request is accepted, measured
  against a monotonic clock so a wall-clock step never moves it early or
  late while the scheduler keeps running.
- **`every`** — a fixed period between occurrences, anchored to a start
  instant that never shifts, even when one occurrence fires late. A
  component that re-creates the same recurring schedule on every one of
  its own restarts keeps the original phase instead of re-anchoring each
  time, as long as it omits the anchor on the re-creation.
- **`local`** — a wall-clock time and set of weekdays evaluated in a
  named time zone, the shape an alarm or a daily reminder wants. A
  daylight-saving transition that skips or repeats a wall-clock instant
  is resolved deterministically: the first instant after a gap, the first
  of two instants during a repeat.

## What gets replayed

A schedule's `context`, everything routing-related about the request that
created it, is captured at creation and stored untouched. When the
schedule fires, that context rides the fired event exactly as it was
given, with one field added describing the occurrence itself: the
schedule's id, its owning `skill_id`, when it was due, and when it
actually fired. This is what lets an alarm set from a remote device ring
back on that same device: the scheduler never has to understand routing,
it only has to hand back what it was given.

A fired event is ordinary bus traffic once it lands. It carries the
session the request named, but firing it makes no claim that session
still exists anywhere. A consumer that no longer recognizes the session
treats it like any other message naming an unknown one.

## Misfire policy

An occurrence the scheduler does not fire within a grace period after its
due instant, sixty seconds by default, is a **misfire**, whether the
scheduler was down or just running late. Each schedule picks one of two
policies for its misfires:

- **`late`** (the default) — fire the most recent missed occurrence once,
  dropping any earlier ones the same schedule missed.
- **`skip`** — drop every missed occurrence without firing any of them.

Either way the scheduler announces what it missed on its own topic before
performing a late fire, so an owner can tell "fired on time" apart from
"fired late because the device was off" apart from "silently dropped."

## Restart behavior

Every accepted schedule is written to disk before the scheduler
acknowledges it, except one explicitly marked **ephemeral** — a schedule
whose owner wants it to die with the current process, such as a
conversation keep-alive timer. A restart discards ephemeral schedules and
nothing else: every persisted schedule is reloaded, its due date
recomputed against the current time, and any occurrence it missed while
the scheduler was down is handled under its misfire policy the moment the
scheduler comes back up. A component never has to re-create its schedules
after a restart to keep them alive. It only re-creates them if it wants a
fresh due date.

Sending the same schedule request twice, same owner, same id, has the
same effect as sending it once: the second request replaces the first
rather than adding a duplicate. This is what makes "re-create my
schedules every time I start" a safe pattern for a component that does
not otherwise track what it already asked for.

## Ownership

A component can only read, replace, or cancel a schedule whose owning
`skill_id` matches its own. Two components using the same schedule name
never collide, because the id is scoped to the owner, and one component
can never accidentally reach into another's schedule by guessing its
name.

A schedule outlives the process that created it by default. A component
that stops and does not want its pending schedules to fire in its absence
must cancel them, or have created them as ephemeral in the first place. A
fire with nobody listening is not an error. The scheduler still records
it as the schedule's most recent fire, so the owner can reconcile by
reading its own schedules back the next time it starts.

---
**Related:** [Scheduling Events](ovos-skill.md#scheduling-events) · [A reminder skill](recipe-reminder-persistence.md) · [Bus Bridges](bus-bridge.md) · [Sessions](session.md)
