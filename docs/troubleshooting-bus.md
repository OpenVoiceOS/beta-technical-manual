# Watching the Bus: `ovos-busmon`

!!! abstract "In a nutshell"
    `ovos-busmon` is a small web app that streams every message on the OVOS messagebus live to a
    browser tab, so you can watch an utterance move through the pipeline without tailing six
    separate log files. This page is the deep dive: install, config, and a walkthrough. For the
    staged decision tree that this tool supports, see [Troubleshooting &
    Debugging](troubleshooting.md).

All the stages in the troubleshooting guide talk to each other over the
[messagebus](bus-service.md): the listener emits an utterance message, the intent service emits a
match, the skill emits a `speak`, and so on. **[`ovos-busmon`](https://github.com/OpenVoiceOS/ovos-busmon)**
is a small web app that connects to the bus as a client and streams every one of those messages
live to a browser tab, in one filterable, searchable timeline.

!!! note "Bus messages, not logs"
    `ovos-busmon` shows **live bus messages only**. It does **not** parse the log files. It
    complements the log tooling ([`ovos-logs`](cli-tools.md#reading-the-logs-ovos-logs) and the
    per-service `*.log` files), it doesn't replace it. For a terminal-based **log** viewer, the
    community project [ovos-tui-client](https://github.com/andlo/ovos-tui-client) reads the OVOS
    logs directly.

!!! tip "Zero-install demo"
    A hosted static build is available at
    [openvoiceos.github.io/ovos-busmon](https://openvoiceos.github.io/ovos-busmon/). No `pip
    install` needed. Because it's the **static-page** build (not the FastAPI-backed server), the
    browser connects straight to the bus itself, so it only works when the **browser runs on the
    same machine as OVOS**. For remote or multi-device use, run the full `pip install ovos-busmon`
    server below.

Internally, it is a FastAPI + WebSocket/SSE service that opens an `ovos-bus-client` connection to
the messagebus and keeps an in-memory ring buffer of everything it sees. The browser UI lets you:

- filter the live stream by message type (glob patterns, e.g. `ovos.*` or `recognizer_loop:*`)
- full-text search across message type, data, context, and session
- filter by session ID, source, and destination
- pause/resume capture and sort newest/oldest first
- export the captured buffer as JSON/JSONL for later inspection
- inject an arbitrary message onto the bus from the UI (the same trick as `ovos-say-to`, but visual)
- group the live stream into a **timeline**: per-session, expandable traces with category badges, so
  you can follow a single utterance across Stages 2-5 as one interaction instead of scanning the raw feed
- type an utterance into the **chat panel** (`POST /api/chat`). It emits a `recognizer_loop:utterance`
  with a stable session ID (so multi-turn/converse works), letting you replay a failing interaction
  deterministically without speaking

There is also a zero-install mode: the UI is a single static page that can open a WebSocket straight
to `ws://<device>:8181/core` with no server component at all. This is useful for a one-off look
without installing anything.

---

## Installing and running it

```bash
pip install ovos-busmon
ovos-busmon
```

To hack on it (or track `dev`), install from a clone instead:

```bash
git clone https://github.com/OpenVoiceOS/ovos-busmon
cd ovos-busmon
pip install .
ovos-busmon
```

By default it binds to `http://127.0.0.1:8005` and connects outward to a messagebus at
`localhost:8181`. Both ends are configurable through environment variables (or a `.env` file next to
where you run it):

| Variable | Default | Meaning |
|---|---|---|
| `OVOS_BUS_HOST` / `OVOS_BUS_PORT` | `localhost` / `8181` | Where the *target* OVOS messagebus is. |
| `BUSMON_HOST` / `BUSMON_PORT` | `127.0.0.1` / `8005` | Where busmon's own web UI listens. |
| `BUSMON_USERNAME` / `BUSMON_PASSWORD` | *(unset)* | HTTP Basic auth for the web UI. Auth is off unless set. |
| `BUSMON_TOKEN` | *(unset)* | Shared-secret token auth (works with the live SSE UI, unlike HTTP Basic). |
| `BUFFER_SIZE` | `2000` | How many messages the ring buffer keeps. |

A Docker route is also available (`docker compose up --build` from the repo), using the image
`jarbasai/ovos-busmon:latest`. Its bundled compose file binds the container to `127.0.0.1:8005` only
and sets `OVOS_BUS_HOST=host.docker.internal` so it can reach a bus running on the host.

!!! warning "Local debugging only: never expose this to the internet"
    `ovos-busmon` mirrors **every** message on the bus, including STT transcripts, intent matches,
    and skill responses. Authentication is off by default; a non-loopback bind refuses to start
    unless `BUSMON_TOKEN` or `BUSMON_USERNAME`/`BUSMON_PASSWORD` is set. Its message-injection
    feature also lets anyone who can reach it emit arbitrary commands onto your assistant's bus.
    Keep it bound to `127.0.0.1` or your local LAN, set a strong token or password before binding
    wider, and never port-forward it to the public internet.

---

## A concrete walkthrough

1. Start `ovos-busmon`. It comes up even if the bus is unreachable: its capture connection
   auto-reconnects on its own, so you can start it before the OVOS device is up and it
   begins capturing once the bus becomes reachable, with no restart needed.
2. Open `http://127.0.0.1:8005` in a browser and log in with the configured credentials.
3. Speak (or trigger) an utterance on the OVOS device.
4. Filter by `recognizer_loop:*`. The first hit is the raw utterance leaving the listener
   (Stage 2 of [Troubleshooting](troubleshooting.md#stage-2-did-the-micwake-word-fire)). If
   nothing appears here, the problem is upstream of the bus entirely (Stage 1).
5. Filter by `ovos.intent.matched` and `ovos.utterance.handled`. These tell you which pipeline
   stage claimed the utterance and confirm the lifecycle actually closed (Stage 4/5 of
   [Troubleshooting](troubleshooting.md#stage-4-which-pipeline-stage-matched-or-didnt)).
6. Filter by `ovos.utterance.speak`. Its absence, with everything else present, points at a silent
   skill handler. Its presence with no audio points at the TTS/playback stage (Stage 6).

Each stage of [Troubleshooting & Debugging](troubleshooting.md) cites the exact message type to
filter on, so this same walkthrough can be repeated stage-by-stage instead of glancing at the
whole stream at once.

---
**Read next:** [Troubleshooting & Debugging](troubleshooting.md)
**Related:** [Command-line Tools](cli-tools.md) · [Bus Service](bus-service.md) · [Debugging Intent Matching](debugging-intent-matching.md)
