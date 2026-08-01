# Bus recipes

!!! abstract "In a nutshell"
    A few small, runnable patterns for talking to a live bus directly, without going through a
    skill: connect and wait for a response, drive it from the command line, and watch traffic
    live.

## Bus recipes

A few small, runnable patterns for talking to a live bus directly, without going through a skill.

### Connect, emit, and wait for a response

```python
from ovos_bus_client import MessageBusClient, Message

bus = MessageBusClient()
bus.run_in_thread()  # connects on a background daemon thread

# fire-and-forget
bus.emit(Message("ovos.utterance.handle", {"utterances": ["what time is it"], "lang": "en-US"}))

# request/response: send a message, then wait for a specific reply type
response = bus.wait_for_response(
    Message("intent.service.adapt.manifest.get"),
    reply_type="intent.service.adapt.manifest",
    timeout=3.0,
)
if response is not None:
    print(response.data)  # {"intents": [...]} — the registered Adapt intent manifest

bus.close()
```

!!! warning "`ovos.session.sync` can't be used this way"
    A tempting-looking request/response pair is `Message("ovos.session.sync")` replying with
    `ovos.session.update_default`. But `MessageBusClient.emit()` always auto-injects a
    `session` object into `message.context` before sending if one isn't already present. That
    turns every `ovos.session.sync` this client emits into a *session sync* (carrying context),
    not the legacy *bare default-session request* that triggers an echo. So it never gets a
    reply this way. `intent.service.adapt.manifest.get` above is a plain request/response pair
    with no such caveat.

`MessageBusClient()` with no arguments reads `host`/`port`/`route` from `mycroft.conf`'s
`websocket` section (see [messagebus Configuration](bus-service.md#configuration) above).
`run_in_thread()` starts the WebSocket loop on a daemon thread so the call returns immediately.
`wait_for_response` blocks the calling thread until a message of `reply_type` arrives or the
timeout elapses, returning `None` on timeout.

### From the command line

The [`ovos-bus-client` CLI tools](cli-tools.md#talking-to-a-running-ovos-ovos-bus-client) wrap
the same client for quick, no-code interaction with a running assistant:

- `ovos-say-to "what time is it"`: inject an utterance as if spoken.
- `ovos-listen`: trigger listening, as if the wake word fired.
- `ovos-speak "hello"`: make OVOS speak a phrase.

### Watching the bus live

For interactively inspecting every message flowing across the bus (useful when a recipe above
isn't behaving as expected), run `ovos-busmon`, a browser-based web UI (FastAPI + WebSocket)
for live bus traffic. It subscribes like any other client and streams each message to the
browser as it is broadcast. Install it with `pip install ovos-busmon`.

!!! note "Upcoming: `AsyncMessageBusClient`"
    An in-progress change adds an async/await-native `AsyncMessageBusClient` alongside the
    threaded `MessageBusClient` used in the recipes above, for callers already running an
    asyncio event loop (e.g. FastAPI servers) that would rather avoid a background thread.

---
**Read next:** [messagebus Service](bus-service.md)
**Related:** [CLI Tools](cli-tools.md) · [Bus Events Reference](bus-events.md)
