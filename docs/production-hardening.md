# Production Hardening

!!! abstract "In a nutshell"
    OVOS ships several network services, and most bind to `127.0.0.1` by default, but not all of
    them do. This page lists every port, its default bind, and whether it has auth or TLS, plus
    the rules to follow before you open any of them on a shared network.

!!! tip "Is this page for you?"
    Looking for systemd units, readiness probes, log locations, backups, or staged upgrades
    instead? See [Production Operations](production-operations.md). This page is the
    security-hardening slice of that material.

---

## Network hardening

OVOS ships several network services. Most bind to `127.0.0.1` by default. Some do not. Check
each one before you open a port on a shared network.

| Service | Port | Default bind | Auth? | TLS? |
|---|---|---|---|---|
| [Messagebus](bus-service.md) | 8181 | `127.0.0.1` | None | Optional (`websocket.ssl`) |
| [GUI WebSocket](gui-service.md#configuration) | 18181 | `127.0.0.1` (older configs may carry `0.0.0.0`) | None | None |
| [Skill Settings web UI](skill-settings.md) | 8000 | `0.0.0.0` (all interfaces) | Basic auth, default `ovos`/`ovos` | None (put a proxy in front for TLS) |
| [STT server](stt-server.md) | 8080 | `0.0.0.0` | None | None (put a proxy in front for TLS) |
| [TTS server](tts-server.md) | 9666 | `0.0.0.0` | None | None (put a proxy in front for TLS) |
| [Translate server](translate-server.md) HTTP API | 9686 | `0.0.0.0` | None | None (put a proxy in front for TLS) |
| [Translate server](translate-server.md) MCP endpoint | 9687 | `127.0.0.1` | None | None |
| [HiveMind](hivemind-agents.md) listener | 5678 | `0.0.0.0` | Access key + password (Noise handshake) | Optional (`ssl` + `cert_dir`/`cert_name` in server config) |

!!! warning "The GUI WebSocket has no authentication, origin check, or TLS"
    Like the bus, the GUI WebSocket ships bound to `127.0.0.1` — but it has no
    authentication, no origin check, and no TLS option at all, and anything it receives is
    forwarded straight onto the core bus. Widen `gui_websocket.host` to `0.0.0.0` only if a
    remote display genuinely needs network access, and re-check configs from before the
    loopback default, which may still carry `0.0.0.0`. See
    [GUI Service: Configuration](gui-service.md#configuration) for the full warning and the
    VPN/reverse-proxy alternative.

### Rules to follow

- Keep every service in the table on `127.0.0.1` unless you have a specific, deliberate reason
  to open it.
- Never expose the messagebus or the GUI WebSocket to the internet. Either one gives full
  control of the assistant, and the GUI socket gives it with no authentication at all (see
  [Security & Trust Model: The bus has no authentication](security-model.md#the-bus-has-no-authentication)).
- If satellite devices need to reach the bus directly (uncommon; most setups should use
  HiveMind instead, see below), bind it to `0.0.0.0` only on a network you control, and
  firewall the port to that network's subnet. For example, with `ufw`, allow only a trusted
  LAN:

  ```bash
  ufw allow from 192.168.1.0/24 to any port 8181 proto tcp
  ufw deny 8181/tcp
  ```

  Replace `192.168.1.0/24` with your actual LAN subnet.
- For anything beyond a single trusted LAN (a phone on mobile data, a satellite in another
  building, a device you don't administer), use [HiveMind](hivemind-agents.md) instead of
  opening the bus. HiveMind gives satellites an authenticated, encrypted channel without
  widening the bus itself. See [Composable Deployments: Satellites](satellites.md) for how a
  satellite fits into a wider topology.
- Serving the bus itself over TLS (for the cases above where it does need to leave localhost)
  is covered in [Bus restart / reconnect behavior: Serving the bus over TLS](bus-reconnect.md#bus-restart-reconnect-behavior).

### Reverse-proxying the HTTP servers

The [STT](stt-server.md), [TTS](tts-server-deployment.md), [translate](translate-server.md), and
[persona](persona-server.md) servers are all plain `uvicorn` apps with no built-in TLS, so
fronting them with a reverse proxy for HTTPS is the normal deployment shape. Doing that has one
sharp edge: `uvicorn` only honors the proxy's `X-Forwarded-Proto` header from an address it
already trusts, and by default that's `127.0.0.1` alone. A proxy running anywhere else — another
container, another host — is untrusted, so `uvicorn` ignores the header and reports the request as
plain `http://`. If the app or the proxy then redirects based on that (a common HTTPS-enforcement
pattern), the redirect's `Location` comes back `http://` instead of `https://`, and a client that
follows redirects turns its next request into a `GET` with no body — silently dropping whatever
the original `POST` was carrying.

The symptom is an opaque `400` partway through a request sequence, and it shows up only with
clients that follow redirects; driving the same endpoint directly with `curl` succeeds, which
sends the search in the wrong direction (the proxy, not `uvicorn`'s trust list).

Fix it by telling `uvicorn` which address to trust, via the `FORWARDED_ALLOW_IPS` environment
variable (none of these four servers exposes a CLI flag for it; only `--host` and `--port` are
their own). Scope it to the actual proxy address — for a proxy running as another container on
the Docker bridge network, that's the bridge gateway IP (commonly `172.17.0.1`), not a wildcard:

```bash
FORWARDED_ALLOW_IPS=172.17.0.1 ovos-tts-server --engine {YOUR_TTS_PLUGIN}
```

A wildcard (`FORWARDED_ALLOW_IPS=*`) makes `uvicorn` trust the header from any source, which
defeats the point of the check on a server reachable from more than one network.

To confirm this is the bug rather than something else, compare the `Location` header of a
redirect hit directly against the container versus through the proxy: a scheme change
(`https://` direct, `http://` through the proxy) is the whole fault, and confirms the proxy's
address needs adding to `FORWARDED_ALLOW_IPS`.

---
**Read next:** [Production Operations](production-operations.md)
**Related:** [Security Model](security-model.md) · [Satellites](satellites.md) · [HiveMind Agents](hivemind-agents.md)
