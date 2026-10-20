---
search:
  boost: 2
---

# Update or Uninstall OVOS

!!! abstract "In a nutshell"
    If you installed OVOS with the [ovos-installer](ovos-installer.md), you update it and
    you remove it the same way: run the installer again. The installer finds the existing
    install and asks two questions. This page covers both tasks. For a manual install, see
    [Release Channels](release-channels.md) instead.

## Before you update

1. Back up your settings. The file is `~/.config/mycroft/mycroft.conf` on a `virtualenv`
   install and `~/ovos/config/mycroft.conf` on a `containers` install. The
   [backup and restore recipe](backup-restore.md#backup-recipe) also covers skill settings.
2. Read what changed in the new version. See
   [Before you upgrade: see what changed](release-channels.md#before-you-upgrade-see-what-changed).
3. On a `virtualenv` install, freeze the package set that works today. If the update
   misbehaves, you can go back to it. See [Rolling Back an Upgrade](release-rollback.md).

## Update OVOS

1. Connect to the device and run the installer with the same command you used to install
   it. See [Run the OVOS Installer](ovos-installer.md#4-run-the-ovos-installer).
2. The installer finds the existing install and asks if you want to uninstall OVOS.
   Answer **No**.
3. The installer asks if you want to update OVOS to the latest version. Answer **Yes**.
4. Go through the remaining screens. The installation method, the release channel and the
   profile stay the same as in the existing install. You cannot change them in place.

To change the installation method, remove OVOS first, then install it again with the
other method.

## Remove OVOS

1. Run the installer with the same command you used to install it.
2. The installer asks if you want to uninstall OVOS. Answer **Yes**.

Before it removes anything, the installer writes a backup archive of the OVOS
configuration directories to `~/ovos-backup.tar.gz`. These directories include
`~/.config/mycroft/`, `~/ovos/` and `~/.config/hivemind/`.

The installer does not remove Docker or PipeWire, because the system or another program can
also use them. These packages stay installed:

- `docker-ce`, `docker-compose-plugin`, `docker-ce-rootless-extras`, `docker-buildx-plugin`
- `pipewire`, `pipewire-alsa`

To remove OVOS without the questions, for example from a script, set `uninstall: true` in a
scenario file. See [Non-interactive (scenario) install](ovos-installer.md#non-interactive-scenario-install).

---
**Read next:** [Rolling Back an Upgrade](release-rollback.md)
**Related:** [Install with ovos-installer](ovos-installer.md) · [Release Channels](release-channels.md) · [Backup and Restore](backup-restore.md)
