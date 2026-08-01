# Observability

!!! abstract "In a nutshell"
    OVOS has no built-in metrics endpoint or dashboard. Day-to-day debugging leans on a
    live bus monitor and logs, and fleet-wide alerting is something you build yourself on top
    of the [readiness probe](production-operations.md#knowing-when-the-assistant-is-actually-ready).

## Observability: what exists and what doesn't

!!! warning "There is no built-in metrics endpoint"
    OVOS does not expose a Prometheus-style `/metrics` endpoint or any built-in dashboard. The
    closest thing is usage-metric uploads, and those are **explicitly opt-in**: disabled by
    default, with nothing sent anywhere unless you deliberately configure an endpoint (see the
    commented-out `opendataConfig`-style keys in the default `mycroft.conf`, and
    [`ovos-opendata-server`](ecosystem-index.md) if you want to run your own collector). That
    is a telemetry pipeline you opt into, not an operational metrics/monitoring system.

For day-to-day, per-device debugging, use:

- **`ovos-busmon`**: a browser-based web UI (FastAPI + WebSocket) that streams the live message traffic on a device's bus in
  real time. The fastest way to see whether wake word → STT → intent → TTS is actually firing.
- **`ovos-logs`** (see [Production Operations: log locations](production-operations.md#log-locations-and-shipping-them-out)) for historical logs.
- The [readiness probe](production-operations.md#knowing-when-the-assistant-is-actually-ready) as a synthetic check you
  can run from outside the device (cron, a monitoring agent, a CI job) on a schedule.

There is no supported way to scrape per-request latency or error rates across a fleet today.
If you need that, you will need to build it on top of the bus messages yourself.

### Building fleet-wide alerting yourself

Since there is no push-based metrics endpoint, fleet alerting has to be built the other way
around. Something outside each device polls its
[readiness probe](production-operations.md#knowing-when-the-assistant-is-actually-ready) on a schedule and reports a
non-zero exit to whatever already pages you. A `systemd` timer wrapping the probe script from
[Production Operations](production-operations.md#knowing-when-the-assistant-is-actually-ready) is enough to get started:

```ini title="~/.config/systemd/user/ovos-alert.service"
[Unit]
Description=Check OVOS readiness and alert on failure

[Service]
Type=oneshot
ExecStart=/bin/sh -c '/usr/local/bin/ovos-ready-probe || /usr/local/bin/notify-monitoring-agent "ovos not ready"'
```

```ini title="~/.config/systemd/user/ovos-alert.timer"
[Unit]
Description=Run the OVOS readiness check every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

```bash
systemctl --user enable --now ovos-alert.timer
```

`notify-monitoring-agent` above is a stand-in for whatever already collects failures on your
fleet: a `curl` to a Healthchecks.io/Cronitor-style dead-man's-switch URL, a call into your
monitoring agent's CLI, an email, a webhook. The same pattern works as a plain `cron` entry
(`*/5 * * * * /usr/local/bin/ovos-ready-probe || /usr/local/bin/notify-monitoring-agent ...`) on a
system without `systemd --user` timers. This is something you build, not something OVOS ships.
But it is the whole shape of a working readiness alert: schedule the probe, act on its exit code.

---
**Read next:** [Privacy & Security](privacy-security.md)
**Related:** [Production Operations](production-operations.md) · [Production Hardening](production-hardening.md) · [Ecosystem Index](ecosystem-index.md)
