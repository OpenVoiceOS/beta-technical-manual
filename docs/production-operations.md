# Running OVOS in Production

!!! abstract "In a nutshell"
    A single OVOS assistant on your desk needs almost no care and feeding. Running many of
    them (a fleet of kiosks, a house full of satellite devices, a product built on top of
    OVOS) is a different job. You need services that restart themselves when they crash,
    a way to know the assistant is actually ready before you rely on it, logs you can ship
    somewhere central, and a safe way to upgrade a device (and undo the upgrade if it goes
    wrong) without physically touching it. This page collects the real, verified pieces for
    that job: systemd units, a readiness probe, log locations, staged upgrades with
    rollback, and how to run one shared speech backend for many thin clients. It assumes you
    are already comfortable with [installing OVOS](ovos-installer.md) and the
    [release channels](release-channels.md) page.

!!! tip "Is this page for you?"
    One assistant on your desk needs almost none of this. Read
    [Privacy & Security](privacy-security.md) instead. Several devices, a shared backend, or
    an assistant you don't sit next to: keep reading here.

---

## Keep services running: systemd units

OVOS itself does not manage process supervision. That is left to the OS. The
[`ovos-installer`](ovos-installer.md) and the [raspOVOS](install-raspovos.md) image both use
**systemd user units** for this. The examples below are adapted from the units raspOVOS
actually ships (`overlays/base_ovos/home/ovos/.config/systemd/user/` in the
[raspOVOS](https://github.com/OpenVoiceOS/raspOVOS) repository).

A top-level dummy target groups all the OVOS services so you can start/stop/enable the whole
stack as one unit:

```ini title="~/.config/systemd/user/ovos.service"
[Unit]
Description=OVOS A.I. Software stack.

[Service]
Type=oneshot
Group=ovos
ExecStart=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=default.target
```

Each real service is `PartOf=ovos.service` and `WantedBy=ovos.service`, so `systemctl --user
restart ovos.service` cascades to all of them, but each can also be restarted individually
without disturbing its siblings:

```ini title="~/.config/systemd/user/ovos-messagebus.service"
[Unit]
Description=OVOS Messagebus (Rust)
PartOf=ovos.service
After=ovos.service

[Service]
Group=ovos
UMask=002
ExecStart=/usr/local/bin/ovos_rust_messagebus
Restart=on-failure

[Install]
WantedBy=ovos.service
```

```ini title="~/.config/systemd/user/ovos-skills.service"
[Unit]
Description=OVOS Skills
PartOf=ovos.service
After=ovos.service
After=ovos-messagebus.service

[Service]
Type=notify
Group=ovos
UMask=002
ExecStart=%h/.venvs/ovos/bin/python /usr/libexec/ovos-systemd-skills
TimeoutStartSec=10m
TimeoutStopSec=1m
Restart=on-failure
StartLimitInterval=5min
StartLimitBurst=4

[Install]
WantedBy=ovos.service
```

If you are writing your own unit for a custom service (a skill runner, a persona server, a
thin-client bridge), the pattern worth keeping is:

- `Restart=on-failure`: restart on crash, not on a clean stop.
- `StartLimitInterval=` / `StartLimitBurst=`: give up (rather than loop forever) after
  repeated failures in a short window, so a broken deploy doesn't spin your CPU.
- `PartOf=`/`After=` the messagebus unit for anything that needs a live bus connection at
  startup.

`After=` only orders unit *start*. It says nothing about whether the messagebus is actually
accepting connections yet, and it says nothing about what happens when the bus unit *restarts*
later. See [Bus restart / reconnect behavior](bus-reconnect.md#bus-restart-reconnect-behavior) for
what a dependent service's existing bus connection does when that happens (short version: it
reconnects on its own with backoff, so `Restart=on-failure` on the messagebus unit is enough.
You do not need to also restart every dependent service).

```bash
systemctl --user daemon-reload
systemctl --user enable --now ovos.service
systemctl --user status ovos-skills.service
journalctl --user -u ovos-skills.service -f
```

!!! note "System vs user units"
    The units above are **user** units (`~/.config/systemd/user/`), matching how raspOVOS and
    the installer run OVOS as the `ovos` user. If you need OVOS to start before any user logs
    in (a headless kiosk), install the same unit files under `/etc/systemd/system/` instead and
    use `systemctl enable --now` (no `--user`). You will also need
    `loginctl enable-linger ovos` if you keep user units but want them running without an
    active login session.

!!! warning "`PIDLock` kills the previous process silently"
    Most OVOS services use `PIDLock` (from `ovos-utils`) to guard against two copies running
    under the same name. On construction, `PIDLock` kills any existing process holding that
    name's PID file, then writes its own PID. There is no warning or confirmation prompt.

    If you start a service by hand while a systemd-managed copy is already running under the
    same name, `PIDLock` kills the systemd-managed one. The PID file is deleted on exit via
    `SIGINT`/`SIGTERM` handlers, so a process killed harder than that (`SIGKILL`, power loss)
    can leave a stale PID file behind that the next start-up will happily reuse.

---

## Knowing when the assistant is actually ready

Services report a rolling status (`started` → `ready` → `error`/`stopping`) over the bus, and
the [`ovos-skill-boot-finished`](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) skill
polls each one and emits a single `mycroft.ready` message once every service it is configured to
wait on has reported ready. This is the signal to use in health checks, readiness probes, or an
`ExecStartPost` step, not "is the process running," which says nothing about whether the
voice pipeline can actually hear and answer you yet.

!!! note "Requires the boot-finished skill to be installed"
    `mycroft.ready` is emitted by a skill, not by `ovos-core` itself. It is pulled in by the
    `skills-audio` [extra](release-channels.md#what-are-ovos-extras)
    (`ovos-core[skills-audio]`, which pins `ovos-skill-boot-finished>=0.5.5a2` in `ovos-core`'s
    own `pyproject.toml`) and is installed by default on most full setups, but a from-scratch,
    headless, or minimal install must include it explicitly for the readiness probe below to
    ever get a response.

A minimal readiness probe using [`ovos-bus-client`](bus-service.md):

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()
response = bus.wait_for_response(
    Message("mycroft.ready.check"), reply_type="mycroft.ready", timeout=30
)
bus.close()
if response is None:
    raise SystemExit("OVOS did not report ready within 30s")
print("OVOS is ready")
```

Save that as `/usr/local/bin/ovos-ready-probe` and wire it into a unit as a post-start check:

```ini
ExecStartPost=/usr/local/bin/ovos-ready-probe
```

!!! warning "Timeout, not certainty"
    `wait_for_response` returns `None` on timeout. It does not raise. Always check for `None`.
    A bare `response.data` on a timed-out call raises `AttributeError`, not a clean failure.

!!! danger "The 30s timeout only applies once connected"
    `wait_for_response` calls `emit()` internally to send the request, and `emit()` waits on an
    internal connected-event with **no timeout** if the bus was never reachable. If the
    messagebus service isn't up yet when this probe runs — a real possibility right at
    `ExecStartPost` — the probe hangs forever instead of failing after 30s, and `systemd` never
    gets past the post-start check. Give the unit its own `TimeoutStartSec`, or add a bus-reachability
    check (e.g. a plain socket connect) before calling `wait_for_response`.

### Headless devices: choosing what "ready" means

[`ovos-skill-boot-finished`](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) is the
skill that actually answers `mycroft.ready.check` and decides what to wait for, via its
`ready_settings` setting. By default it waits for `skills` plus every installed skill to
register. For a server or a device with no GUI/audio you usually want to name only the
services that actually apply:

```yaml title="settings.json for ovos-skill-boot-finished"
ready_settings:
  - skills     # ovos-core skill loader reported ready
  - voice      # ovos-dinkum-listener reported ready (omit on a text-only/server node)
  - audio      # ovos-audio reported ready (omit if there is no speaker)
speak_ready: false   # don't speak a "ready" dialog on a headless box
ready_sound: false   # don't play a ready chime either
```

`network`/`internet`/`gui_connected` are also accepted `ready_settings` entries, and any
service exposing an OVOS `ProcessStatus` (including `PHAL`) can be named by its status key.

!!! warning "`mycroft.ready` only covers what you list"
    `mycroft.ready` only tracks the components named in `ready_settings`: skills, voice, and
    audio by default. It does **not** track the GUI or the media daemon unless you add
    `gui_connected` (or a media status key) yourself. That means a fleet can report "ready"
    while the screen is stuck (see [GUI status](gui-status.md)) or the media daemon
    (see [ovos-media](ovos-media.md)) is non-functional. The health check simply never asked
    about them.

---

## Log locations and shipping them out

OVOS services write rotating log files under `$XDG_STATE_HOME/mycroft/<service>.log`
(typically `~/.local/state/mycroft/`) by default — even with no `logging` section in
`mycroft.conf`. Check that directory first if you can't find a log file. A `logging`
section overrides the location and rotation:

```json
{
  "logging": {
    "logs": {
      "path": "~/.local/state/mycroft/",
      "max_bytes": 50000000,
      "backup_count": 6
    }
  }
}
```

Each service gets its own file named after it (`skills.log`, `bus.log`, `audio.log`,
`voice.log`, `gui.log`, ...).

`ovos-utils` also ships a small CLI, `ovos-logs`, for navigating those files without hunting
through each one by hand:

```bash
ovos-logs show -l skills            # page through skills.log (uses $PAGER/less)
ovos-logs slice -l bus -l skills -f ~/incident.log   # extract bus+skills since service start
ovos-logs slice -s "01-12-2023" -u "01-12-2023 17:00" # slice a specific window
ovos-logs reduce -s 1000000         # trim every log down to ~1MB (keep the tail)
```

For centralized log shipping (many devices to one place), point a standard log-forwarding
agent (Vector, Fluent Bit, Promtail, `rsyslog`) at the log directory, or redirect the systemd
unit's stdout to the journal (the default) and ship `journalctl` output instead. OVOS itself
does not include a log-shipping client.

---

## Backup and restore

Two kinds of state matter on an OVOS device: the packages that are installed, and everything
under a user's config/data directories. The full backup recipe, the restore-onto-fresh-install
steps, and the exact config/data paths have moved to their own page:
**[Backup and Restore](backup-restore.md)**.

---

## Updating a device or a fleet

Upgrading safely means freezing the current package set before you touch anything, so you can
roll back with `--force-reinstall` if the upgrade misbehaves. The single-device recipe, the
fleet canary pattern, and how to detect a partially-failed rollback have moved to their own
page: **[Staged Upgrades and Rollback](staged-upgrades.md)**.

!!! warning "Check the breaking-change reference before any version jump"
    An upgrade that crosses release eras can hit renamed config keys, changed skill
    APIs, and removed bus topics. Before upgrading, go straight to
    [For Device & Fleet Operators](updating-deployers.md), the deployer page of the
    [Updating from Older OVOS](updating-from-older-ovos.md) hub, and read forward from
    your current era. If you maintain custom skills or plugins, see
    [Version-Compatible Skills & Plugins](version-compat-guide.md).

---

## One config for many devices: the system config layer

OVOS reads configuration from several layered files, [merged in order](config.md) so that a
more specific file overrides a more general one. The layer meant for fleet-wide, admin-managed
settings is the **system config**, at a fixed path:

```text
/etc/mycroft/mycroft.conf
```

This file sits below each user's own `~/.config/mycroft/mycroft.conf`, so per-device
overrides still win, but anything you don't override there comes from the system file. This
is the layer to drop settings into via configuration management (Ansible, a Debian package
postinst, a golden image) rather than hand-editing every device's user config. For example,
pinning the same wake word, STT/TTS servers, or `ready_settings` across an entire fleet.

---

## Thin clients + a shared speech backend

Several low-power devices, each running a full `ovos-core`, all pointed at one shared
machine doing the heavy STT/TTS inference over HTTP: see
[Satellites: Thin clients + a shared speech backend](satellites.md#thin-clients-a-shared-speech-backend)
for the compose files, the config keys, and the container networking caveats.

---

## Security hardening

Which ports OVOS binds by default, what has auth, what needs a firewall rule before it
leaves localhost, and the HiveMind alternative to opening the bus directly: see
[Production Hardening](production-hardening.md).

---

## Observability

OVOS has no built-in metrics endpoint or dashboard. Day-to-day debugging leans on `ovos-busmon`
(a live bus monitor) and the logs described above. Fleet-wide alerting is something you build
yourself on top of the readiness probe. The full picture, including a ready-to-adapt
`systemd` timer for polling the readiness probe, has moved to its own page:
**[Observability](observability.md)**.

---
**Read next:** [Privacy & Security](privacy-security.md)
**Related:** [Backup and Restore](backup-restore.md) · [Staged Upgrades and Rollback](staged-upgrades.md) · [Observability](observability.md) · [STT Server](stt-server.md) · [Updating from Older OVOS](updating-from-older-ovos.md) · [HiveMind](hivemind-agents.md) · [Release Channels](release-channels.md)
