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

!!! warning "The GUI WebSocket binds to all interfaces by default"
    Unlike the bus, the GUI WebSocket ships bound to `0.0.0.0`. It has no authentication, no
    origin check, and no TLS option, and anything it receives is forwarded straight onto the
    core bus. Set `gui_websocket.host` to `127.0.0.1` unless a remote display genuinely needs
    network access. See [GUI Service: Configuration](gui-service.md#configuration) for the
    full warning and the VPN/reverse-proxy alternative.

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

---
**Read next:** [Production Operations](production-operations.md)
**Related:** [Security Model](security-model.md) · [Satellites](satellites.md) · [HiveMind Agents](hivemind-agents.md)
