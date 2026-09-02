# Bus restart / reconnect behavior

!!! abstract "In a nutshell"
    When `ovos-messagebus` restarts, every connected client detects the drop, backs off, and
    reconnects on its own. Messages sent during the outage are lost, not queued. This page
    covers the reconnect mechanics and how to serve the bus over TLS.

## Bus restart / reconnect behavior

Restarting `ovos-messagebus` is the single most common operational disruption, because every
other service (`ovos-core`, `ovos-dinkum-listener`, `ovos-audio`, `ovos-PHAL`) holds a
`MessageBusClient` connection to it. What each of those clients does when that connection drops
is defined once, in `ovos-bus-client`'s `MessageBusClient`, and applies identically to every
service built on it.

**Detecting the drop.** A closed socket reaches the client's `on_error` handler. A clean close
that never errors is not distinguished from one that does. Both a `WebSocketConnectionClosedException`
and a plain `ConnectionRefusedError`/`ConnectionResetError` land there. `on_error` clears the
"connected" flag, closes the socket, and reconnects.

**Backoff.** Reconnection starts at a 5-second delay and doubles on each further failure, capped
at 60 seconds (`self.retry = min(self.retry * 2, 60)`), so a device left disconnected for a while
does not overload the bus with reconnect attempts. A successful reconnect resets the delay back to
5 seconds for next time.

**In-flight calls during the outage.** `emit()` (and therefore `wait_for_response()`, which calls
`emit()` internally) waits for the connection to come back rather than failing fast. It waits up
to 10 seconds, and if the client had already started running before that, it then waits with
**no further timeout** until the socket reconnects.

`wait_for_message()` / `wait_for_response()`'s
own reply-timeout only starts counting once the message is actually sent. So a call made while
the bus is down can block well past the `timeout` value you passed it, for as long as the bus
stays down. Once the client is reconnected, waits resume normally and time out as documented.

**Messages sent during the outage are lost, not queued.** The client does not buffer messages
while disconnected. Nothing is stored and re-sent once the socket reopens. Any `emit()` that was
allowed through only unblocks (and actually sends) after reconnection, but nothing produced by a
process that isn't running a client at all during the gap is retried later. Downstream services
should treat a bus restart as a full session reset for anything time-sensitive: session state
communicated over the bus is fine (a fresh `ovos.session.sync` happens automatically once the
socket reopens), but any request/response pair straddling the restart is simply lost from the
requester's point of view until it emits again.

**Malformed frames don't trigger a reconnect.** A frame that fails to deserialize, or whose
session carrier isn't a JSON object, is dropped and logged. It does not tear the connection down
or trigger the reconnect path above. Only a genuine socket-level failure does.

See [Production Operations](production-operations.md#keep-services-running-systemd-units) for how
this interacts with `systemd`'s own `Restart=`/`After=` ordering across the OVOS services.

!!! info "Serving the bus over TLS"
    Set `websocket.ssl: true` and the Tornado `ovos-messagebus` serves `wss://` itself — nothing
    needs to sit in front of it. Point it at an existing certificate with `websocket.ssl_cert`
    and `websocket.ssl_key`:

    ```jsonc
    "websocket": {
        "ssl": true,
        "ssl_cert": "/etc/ssl/certs/ovos-bus.crt",
        "ssl_key": "/etc/ssl/private/ovos-bus.key"
    }
    ```

    If `ssl` is on but no cert/key are configured, the bus generates a self-signed pair on first
    start (under `$XDG_DATA_HOME/OpenVoiceOS/ovos-messagebus/certs/`). This path needs the `ssl`
    extra (`pip install --pre "ovos-messagebus[ssl]>=0.1.0a1"`), and the bus refuses to start rather than fall
    back to plaintext if it's missing. Clients built on `ovos-bus-client` reach a `wss://` bus by
    setting the same `websocket.ssl: true`. [HiveMind](hivemind-agents.md) is the other route to
    encrypted transport across hosts. (The alternative `webrockets` backend does not terminate TLS
    itself. Use the default Tornado backend to serve `wss://` directly.)

---
**Read next:** [messagebus Service](bus-service.md)
**Related:** [Production Operations](production-operations.md) · [HiveMind](hivemind-agents.md)
