# Rolling Back an OVOS Upgrade

!!! abstract "In a nutshell"
    A [release channel](release-channels.md) bounds versions going forward. It does not
    remember what you actually had installed before an upgrade. This page covers freezing a
    known-good package set before you upgrade, rolling the whole stack back if an upgrade
    misbehaves, and pinning or rolling back just one package instead of the whole environment.

!!! warning "Installed with `ovos-installer`? Know your method first"
    The `pip`/`uv pip` commands here apply to the **`virtualenv`** install method, run inside
    that venv (activate it first — `systemctl --user cat ovos-core.service` reveals its path
    from that unit's `ExecStart`; the umbrella `ovos.service` is a no-op meta unit). On a **`containers`** install, roll back by pinning the previous
    image tag and re-running `docker compose up -d`, or
    [re-run the installer](ovos-installer-scenarios.md) — it detects the existing install and
    offers only your current method.

---

## Pinning or rolling back a single package

The [freeze/force-reinstall pattern](#rolling-back) below rolls back your *entire*
environment. If only one package regressed, you don't need the sledgehammer. Pin
just that package instead:

```bash
uv pip install "ovos-stt-plugin-whisper==<old-version>"
```

That pin lives only in the installed environment. The next reinstall from a constraints
file overwrites it with whatever range the channel allows. If you use a local constraints
file (see [Release Channels: Offline and mirrored
installs](release-channels.md#offline-and-mirrored-installs)), record the pin there in the
same step, so it survives:

```bash
echo "ovos-stt-plugin-whisper==<old-version>" >> ~/ovos-constraints.txt
uv pip install -c ~/ovos-constraints.txt "ovos-stt-plugin-whisper==<old-version>"
```

Either way, you need to know what the old, working version was. Get it from your frozen
snapshot with `grep ovos-stt-plugin-whisper /etc/ovos/known-good-<date>.txt` (see [Rolling
Back](#rolling-back) below), or, if you didn't freeze one, from `uv pip show
ovos-stt-plugin-whisper` run *before* you upgraded.

Pinning the package alone isn't enough. The process that already loaded the old, broken
version keeps running it in memory until it restarts. Restart whichever service loads that
package (e.g. `systemctl --user restart ovos-dinkum-listener.service` for an STT plugin)
before you consider the rollback complete.

!!! note "A release channel isn't a maturity guarantee"
    Picking the `stable` channel bounds *versions*, not the maturity of every plugin that
    channel resolves. See [Maturity Scale: a release channel is not a maturity
    guarantee](maturity.md) for what "stable
    channel" does and doesn't promise.

---

## Rolling Back

Constraints files bound a channel's versions, but they don't record what *you* actually had
installed before an upgrade. Before upgrading anything you care about, freeze what's currently working:

```bash
sudo install -d -o "$USER" /etc/ovos          # once per device
uv pip freeze > /etc/ovos/known-good-$(date +%F).txt
```

One dated file per freeze, at one absolute path, on every device — the same convention
[Staged Upgrades and Rollback](staged-upgrades.md#staged-upgrades-and-rollback) uses for a
fleet. Keep it out of your home directory: a rollback is often needed exactly when the
account, the venv, or the whole home directory is what went wrong.

If an upgrade misbehaves, `pip`/`uv` won't downgrade a package on their own just because a
newer constraints file changed. An ordinary `install` call treats an already-satisfied
requirement as nothing to do. Force the reinstall of the exact frozen versions instead:

```bash
uv pip install --force-reinstall -r /etc/ovos/known-good-<date>.txt
```

See [Staged Upgrades and Rollback](staged-upgrades.md#staged-upgrades-and-rollback)
for the same pattern applied across a fleet of devices rather than one machine. If the
rollback needs more than package versions, for example your device's `mycroft.conf` or a
skill's `settings.json` was also damaged, see the [backup and restore
recipe](backup-restore.md#backup-recipe) instead.

!!! tip "Moving to a newer OS image"
    Flashing a fresh OS image (a new raspOVOS release, a new Raspberry Pi OS build) wipes
    the disk. Back up `mycroft.conf` and each skill's `settings.json` first, following the
    [backup and restore recipe](backup-restore.md#backup-recipe), then restore them
    onto the new image the same way.

---
**Read next:** [Release Channels](release-channels.md)
**Related:** [Production Operations](production-operations.md) · [Maturity Scale](maturity.md) · [Offline and mirrored installs](release-channels.md#offline-and-mirrored-installs)
