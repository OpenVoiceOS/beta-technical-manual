# OVOS Release Channels & Installation Options

!!! abstract "In a nutshell"
    OVOS is built from many small swappable pieces. This page explains the different ways to install them and how to pick how new (or how stable) your version is. A "release channel" is like choosing between a tested, stable edition or an early-preview edition with the newest features but more rough edges. Most people should ignore the details and just use the guided [`ovos-installer`](ovos-installer.md). The manual steps here are for tinkerers who want precise control (see the [Glossary](glossary.md) for terms).

!!! tip "Just want it working? Use the installer."
    Most people should install OVOS with the **[`ovos-installer`](ovos-installer.md)**, a guided
    wizard that handles everything. The manual `pip` commands and version bounds below are for
    people who want fine-grained control (custom/headless setups). A few terms used on this page:
    **extras** = optional add-on bundles you list in brackets, e.g. `ovos-core[mycroft]`.
    **constraints file** = a version "filter" that bounds which package versions may be installed.
    **headless** = a device with no monitor/keyboard (e.g. a Raspberry Pi you SSH into).

Open Voice OS (OVOS) is a **modular voice assistant platform** that lets you install only the components you need. You might build a lightweight voice interface or a full-featured smart assistant. Either way, OVOS gives you flexibility through modular packages and optional feature sets called **extras**.

---

## Installation Methods

Depending on your experience level and goals, you can choose one of the following methods:

### 1. [The `ovos-installer`](ovos-installer.md) (Recommended)
The easiest way for most users. A guided TUI (Text User Interface) script that handles dependencies, environment setup, and service configuration for you.

### 2. [raspOVOS](install-raspovos.md): pre-built Raspberry Pi image
A pre-built flash-and-boot image for the Raspberry Pi. The images are in a maintenance
pause and a refreshed release is on the roadmap, so check the
[raspOVOS repository](https://github.com/OpenVoiceOS/raspOVOS) status before choosing
this path. The installer above is the recommended route on the Pi.

### 3. Manual Installation (Advanced)
Install individual components via `pip` or `uv`. Best for developers or custom integration (e.g., headless nodes, Docker containers).

---

## Checking what you have installed

Before touching anything, find out what's actually on the machine:

```bash
pip show ovos-core                  # version, location, and dependencies of one package
pip list | grep ovos                # every installed ovos-* package and its version
ovos-core --version                 # if the CLI entry point is available on this version
```

`pip show` also lists a package's declared `Requires:`, which is a quick way to check
whether a dependency bump you're considering is even compatible with what else is
installed. If `ovos-core --version` isn't recognized, fall back to `pip show ovos-core`.
Not every release exposes a `--version` flag on the CLI.

## Before you upgrade: see what changed

This manual intentionally never hardcodes a current version number. By the time you
read this page, any number here would already be stale. Before upgrading, check the
**source of truth** for what actually changed in the version you're moving to:

- Each repository's **GitHub Releases** page (e.g.
  [ovos-core/releases](https://github.com/OpenVoiceOS/ovos-core/releases)). Swap
  `ovos-core` for the package you're upgrading.
- Its `CHANGELOG.md`, where the repository keeps one (generated from conventional
  commits — see [Semantic Versioning](https://semver.org/)).

## Rolling back an upgrade

Freezing a known-good package set before an upgrade, rolling the whole stack back if it
misbehaves, and pinning or rolling back just one regressed package instead of the whole
environment: see [Rolling Back an OVOS Upgrade](release-rollback.md).

---

## Choosing a Release Channel

OVOS follows [**semantic versioning**](https://semver.org/) (SemVer) with a **rolling release model**. It supports three release channels: **stable**, **testing**, and **alpha**. Pick the right balance between newer features and system reliability.

These channels are managed via the [constraints files](https://pip.pypa.io/en/stable/user_guide/#constraints-files) hosted in the [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases) repository. **If unsure, choose Testing.** It gets bug fixes and new features without the instability of Alpha.

### 1. Stable Channel (Production-Ready)

- ✅ Bug fixes only
- 🚫 No new features or breaking changes
- ✅ Recommended for production or everyday use

!!! note "\"Production-ready\" means package-version stability, not a hardened default"
    This channel guarantees the *package versions* are stable and tested. It says nothing
    about the default plugin configuration. Out of the box, that config still ships cloud
    STT/TTS/translation and an unauthenticated bus. See
    [Privacy & Security](privacy-security.md) for the actual network surface and how to
    harden it.

!!! warning "Stable pins an older snapshot than Testing"
    Formal codename releases have not landed yet. `constraints-stable.txt` pins the versions
    from the last stable release (ovos-core `1.3.1`), an older, unmaintained snapshot.
    `constraints-testing.txt` tracks newer versions. Check
    [the constraints files themselves](https://github.com/OpenVoiceOS/ovos-releases) for the
    exact pins. Until the next codename release ships, use **Testing** as the recommended
    channel for most distros and users. This matches upstream guidance in
    [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases).

```bash
uv pip install ovos-core[mycroft] -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt

```

### 2. Testing Channel (Feature Updates)

- ✅ Bug fixes and new features
- ⚠️ Not as thoroughly tested as stable
- 🧪 Best for early adopters or development environments

```bash
uv pip install ovos-core[mycroft] -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-testing.txt

```

### 3. Alpha Channel (Bleeding Edge)

- 🔬 Experimental features
- ⚠️ May include breaking changes
- 🧪 Not suitable for production use

!!! warning "`--pre` is not scoped to OVOS"
    `--pre` tells `pip`/`uv` to allow pre-release versions of **every** dependency it
    resolves, not just the `ovos-*` packages. A transitive dependency you didn't expect
    can also jump to a pre-release. Use a dedicated virtual environment for alpha testing.

```bash
uv pip install ovos-core[mycroft] --pre -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-alpha.txt

```

---

!!! example "A minimal lab-ready manual install, start to finish"
    Everything below assumes a Python virtual environment is already active and gets you from
    nothing to a talking assistant on one machine, no installer wizard involved:

    ```bash
    # 1. Install the core services on the stable channel
    uv pip install "ovos-core[mycroft]" \
        -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt

    # 2. Launch each service (one terminal/tmux pane each, or use the systemd units
    #    in Production Operations for anything long-lived)
    ovos-messagebus &
    ovos_PHAL &
    ovos-dinkum-listener &
    ovos-audio &
    ovos-core &

    # 3. Confirm the bus is up and services are talking to each other
    ovos-busmon
    ```

    Say "Hey Mycroft, what time is it" once everything above has settled. If you get a spoken
    answer, the install is working end to end. See
    [Production Operations](production-operations.md#keep-services-running-systemd-units) to
    turn these into supervised systemd services instead of foreground processes.

---

## OVOS From Scratch: Custom Installation

Rather than using a full distro, you can manually pick which components to install:

- [`ovos-messagebus`](https://github.com/OpenVoiceOS/ovos-messagebus): internal messaging between services
- [`ovos-core`](https://github.com/OpenVoiceOS/ovos-core): skill handling
- [`ovos-audio`](https://github.com/OpenVoiceOS/ovos-audio): text-to-speech ([TTS](tts-plugins.md)), audio playback
- [`ovos-dinkum-listener`](https://github.com/OpenVoiceOS/ovos-dinkum-listener): wake word, voice activation
- [`ovos-gui`](https://github.com/OpenVoiceOS/ovos-gui): GUI integration (warning: the legacy [GUI](gui-service.md) is deprecated and not usable. A replacement is in progress, so you can omit this on most setups)
- [`ovos-PHAL`](https://github.com/OpenVoiceOS/ovos-PHAL): hardware abstraction layer

Media playback (music, podcasts, video) is a separate concern from the components above.
By default it is handled by a bundled backend inside `ovos-audio`
(`enable_old_audioservice: true`). See [ovos-media](ovos-media.md) for the upcoming
standalone player and how to opt into it.

This is useful if you are building something like a **Hivemind node** or **headless device**, where you might not need audio output or a GUI.

---

## What Are OVOS Extras?

OVOS uses Python extras (e.g., `[mycroft]`) to let you install predefined groups of components based on your use case.

| Extra Name           | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `mycroft`            | Core services for full voice assistant experience                      |
| `padatious`          | Adds the [Padatious](padatious-pipeline.md) intent pipeline. Apache-2.0, pure Python. The old name `lgpl` still works as an alias |
| `plugins`            | Includes various plugin interfaces                                     |
| `skills-essential`   | Must-have skills (like system control, clock, weather)                 |
| `skills-audio`       | Audio I/O-based skills                                                  |
| `skills-gui`         | GUI-dependent skills                                                    |
| `skills-internet`    | Skills that require an internet connection                             |
| `skills-media`       | [OCP](ocp-pipeline.md) (OpenVoiceOS [Common Play](ocp-pipeline.md)) media playback skills                    |
| `skills-desktop`     | Desktop environment integrations                                       |

Extras and a release channel are independent choices. Combine them in one command by
adding both the bracketed extras and a `-c` constraints file:

### Full Installation Example

```bash
uv pip install "ovos-core[mycroft,padatious,plugins,skills-essential,skills-audio,skills-gui,skills-internet,skills-media,skills-desktop]" \
    -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt
```

### Minimal Installation Example

```bash
uv pip install "ovos-core[mycroft,plugins,skills-essential]" \
    -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt
```


---

## Offline and mirrored installs

Every `-c https://...` command on this page fetches the constraints file over HTTPS at install
time. On an isolated or bandwidth-constrained network, keep local copies instead.

**1. Use a local constraints file.** Download the channel file once on a connected machine, copy
it across, and point `-c` at the path:

```bash
uv pip install "ovos-core[mycroft]" -c /srv/ovos/constraints-stable.txt
```

**2. Install from a local wheelhouse.** Populate a directory of wheels on a connected machine,
then install with the index disabled:

```bash
# connected machine (uv has no download subcommand, use pip here)
pip download "ovos-core[mycroft]" -c constraints-stable.txt -d ./wheels
# isolated machine
uv pip install --no-index --find-links ./wheels "ovos-core[mycroft]"
```

**3. Point the runtime skill installer at a local constraints file.** Set
`skills.installer.constraints` in `mycroft.conf` to a filesystem path so it does not try to
fetch the channel file on every operation:

```json
{
  "skills": {
    "installer": {
      "constraints": "/srv/ovos/constraints-stable.txt"
    }
  }
}
```

!!! note "The runtime skill installer still needs GitHub"
    Installing a skill *at runtime* over the bus resolves the skill repository through
    `api.github.com` and `raw.githubusercontent.com`. A local constraints file removes one
    network dependency, but runtime skill installation cannot work on a network where those
    endpoints are unreachable. Install skills as ordinary packages from your wheelhouse
    instead. See [Skill Installer](skill-installer.md).

---

## Technical Notes

- OVOS is **fully modularized**, with each major service in its own repository, so you install only what you need.
- All packages follow [Semantic Versioning (SemVer)](https://semver.org/), so you can rely on versioning to understand stability and compatibility.
- Constraints files hosted in [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases) are the current mechanism for bounding system versions across the channels. Formal codename releases are still pending. See the note under the Stable channel.
- Once **codename releases** begin, packagers should pin to the versioned (tagged) constraints file URL rather than the `main` branch. This way a package doesn't silently pick up constraint changes after its QA cycle is done.

!!! note "Channel constraints are ranges, not exact pins"
    Every entry in the published channel constraints files is a compatible **range**
    (`>=x,<y`), not an exact `==` pin. A channel therefore guarantees mutually compatible
    versions, not identical ones: installing the same channel on two machines, or on the same
    machine a month apart, can resolve to different versions.

    For a genuinely reproducible build, resolve once and install from your own frozen output:

    ```bash
    uv pip install "ovos-core[mycroft]" -c https://raw.githubusercontent.com/OpenVoiceOS/ovos-releases/refs/heads/main/constraints-stable.txt
    uv pip freeze > my-constraints.txt
    # every later install, on every machine:
    uv pip install "ovos-core[mycroft]" -c my-constraints.txt
    ```

## ⚠️ Tips & Caveats

- Using `--pre` installs pre-releases across all dependencies, not just OVOS-specific ones. Use it with caution.
- You can mix and match extras based on your hardware or use case, e.g., omit GUI skills on a headless server.
- A constraints file only bounds packages it lists. Anything absent resolves freely. If you need an exact, repeatable set of versions, install from your own `uv pip freeze` output rather than from a channel file.
- After installing you need to launch the individual ovos services, either manually or by creating a systemd service

---

**Read next:** [Make it yours](personalize.md)
**Related:** [Rolling Back an OVOS Upgrade](release-rollback.md) · [OVOS Releases repo](https://github.com/OpenVoiceOS/ovos-releases) · [Constraints files explanation (pip docs)](https://pip.pypa.io/en/stable/user_guide/#constraints-files) · [Semantic Versioning](https://semver.org/) · [ovos-installer](ovos-installer.md)

