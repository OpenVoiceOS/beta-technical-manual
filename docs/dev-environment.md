# Development Environment

!!! abstract "In a nutshell"
    This page covers the workflow for fixing a bug in `ovos-core` or another core repository:
    cloning the repo, installing it editable in an isolated environment, running the service
    you are changing against the rest of an installed stack, reloading a skill while you edit
    it, attaching a debugger, and running the repo's own test suite. For the day-to-day
    commands OVOS ships once installed, see [Command-line Tools](cli-tools.md). For the
    release pipeline a change goes through after it leaves your machine, see
    [Contributing](contributing.md).

## Clone and install editable

Fork the repo you want to fix on GitHub first. You need the fork to push your branch, since
only maintainers can push to [`ovos-core`](https://github.com/OpenVoiceOS/ovos-core) itself.
Then clone your fork and create an isolated virtual environment for it. `uv` is faster than
plain `venv`/`pip` and works the same way:

```bash
git clone https://github.com/<your-user>/ovos-core.git
cd ovos-core
git remote add upstream https://github.com/OpenVoiceOS/ovos-core.git
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

An editable install (`-e .`) links the package to your checkout, so a change to a `.py` file
in the repo takes effect the next time that module is imported, without reinstalling.

`ovos-core`'s `pyproject.toml` declares these optional-dependency groups
(`[project.optional-dependencies]`):

| Extra | What it installs |
|---|---|
| `mycroft` | The rest of a runnable stack: `ovos_PHAL[extras]`, `ovos-audio[extras]`, `ovos-gui`, `ovos-messagebus`, `ovos-dinkum-listener[extras]`. |
| `plugins` | A default set of pipeline/utterance plugins (adapt, OCP, persona, number/date parsers, and others). |
| `skills-essential` / `skills-extra` | Default skills bundles. |
| `padatious` | `ovos_padatious`. Apache-2.0. The old name for this extra was `lgpl`, which still works as an alias. |
| `test` | `pytest` and the fixtures the repo's own test suite needs (see [Running tests](#running-tests)). |

Install the combination you need. To hack on `ovos-core` itself with a full local stack:

```bash
uv pip install -e ".[mycroft,plugins,skills-essential]"
```

Other core repos follow the same pattern but define their own extras. `ovos-dinkum-listener`
(the listener service) declares `extras` (STT/VAD/microphone/wake-word plugins), a Linux-only
`linux` extra (ALSA), and a `tests` extra. `ovos-audio` declares `extras` and `test`.
`ovos-messagebus` declares `webrockets`, `benchmark`, and `test`. Check the repo's own
`pyproject.toml` for the exact extra name and its dependency versions before assuming it
matches another repo.

## Running the services from a checkout

Every core service is a console script defined under `[project.scripts]` in its own
`pyproject.toml`:

| Repo | Console script | Entry point |
|---|---|---|
| `ovos-core` | `ovos-core` | `ovos_core.__main__:main` |
| `ovos-core` | `ovos-intent-service` | `ovos_core.intent_services.service:launch_standalone` |
| `ovos-core` | `ovos-skill-installer` | `ovos_core.skill_installer:launch_standalone` |
| `ovos-messagebus` | `ovos-messagebus` | `ovos_messagebus.__main__:main` |
| `ovos-dinkum-listener` | `ovos-dinkum-listener` | `ovos_dinkum_listener.__main__:main` |
| `ovos-audio` | `ovos-audio` | `ovos_audio.__main__:main` |

When one of these is installed editable in your active virtual environment, running its
console script runs your checkout's code, not a package from PyPI.

The normal boot order is: messagebus first (everything else connects to it), then the other
services in any order, since they wait for the bus and for each other over bus messages:

```bash
ovos-messagebus &
ovos-dinkum-listener &
ovos-audio &
ovos-core &
```

To hack on just one piece, install only that repo editable and install the rest of the stack
normally (from PyPI, in the same virtual environment or a separate one that shares the same
messagebus host/port). Point every service at the same messagebus by giving them the same
[configuration](config.md); the bus address is not hardcoded. For example, to debug a skill
loading problem, run a normal `ovos-messagebus`, `ovos-audio`, and `ovos-dinkum-listener` from
PyPI, and only `ovos-core` from your editable checkout.

## Hot-reloading a skill while you edit it

How reload behaves depends on how the skill is loaded, per `ovos_workshop/skill_launcher.py`
in the [`ovos-workshop`](https://github.com/OpenVoiceOS/OVOS-workshop) repo:

- **Skills loaded as installed plugins** (the normal path inside a running `ovos-core`,
  driven by `SkillManager.load_plugin_skills` in `ovos_core/skill_manager.py`) use
  `PluginSkillLoader`, whose `_load()` does **not** start a file watcher. Editing the skill's
  source while `ovos-core` is running does not reload it, because Python has already imported
  the module. Restart `ovos-core` to pick up the change; it is fast, and `ovos-core` reloads
  every plugin skill on the next startup scan.
- **A single skill run standalone** with the `ovos-skill-launcher` console script (from
  `ovos-workshop`, entry point `ovos_workshop.skill_launcher:_launch_script`) does get real
  hot reload. When you pass a skill directory explicitly, it uses the base `SkillLoader`,
  which starts a recursive `FileWatcher` (`ovos_utils.file_utils.FileWatcher`) on the skill
  directory and calls `reload()` on any file change:

  ```bash
  ovos-skill-launcher my-skill.example ./path/to/my-skill
  ```

  This connects to whatever `ovos-messagebus` is already running, waits for `ovos-core` to
  report ready, and loads the skill under its own container. Editing and saving a file under
  that directory triggers `_handle_filechange`, which reloads the skill in place, as long as
  the skill instance has `self.reload_skill` left at its default of `True`
  (`ovos_workshop/skills/ovos.py`). This is the workflow to use while actively iterating on a
  single skill's code.

- `ovos-core`'s own `SkillManager` also runs a `FileWatcher`, but only over each skill's
  **settings** files (`_init_filewatcher` in `ovos_core/skill_manager.py`), not its source. It
  does not give code hot reload.

## Attaching a debugger

Every service's `main()` runs in the foreground when you call its console script directly
(none of them daemonize), so `pdb` and `debugpy` both work without extra setup:

```bash
python -m pdb -c continue $(command -v ovos-core)
```

For `debugpy`, start the service under it and attach from your editor:

```bash
python -m debugpy --listen 5678 --wait-for-client $(command -v ovos-core)
```

To see what a service is doing without stepping through code, raise its log level. Per
`ovos_utils/log.py`, log configuration lives under a `logging` section in
[configuration](config.md):

```json
{
    "logging": {
        "log_level": "DEBUG",
        "skills": {
            "log_level": "DEBUG"
        }
    }
}
```

A per-service block (`bus`, `skills`, `audio`, `voice`, and so on) overrides the default
`log_level` just for that service. `LOG.set_level()` also takes effect immediately: OVOS
watches the configuration file and applies a new level to a running process without a
restart. The `OVOS_DEFAULT_LOG_LEVEL` and `OVOS_DEFAULT_LOG_NAME` environment variables set
the logger's default before any configuration is loaded.

Once a service is emitting the log level you want, read it back with
[`ovos-logs`](cli-tools.md#reading-the-logs-ovos-logs) (shipped by `ovos-utils`):

```bash
ovos-logs show -l skills
ovos-logs list --debug
```

## Running tests

Install the repo's `test` extra (check the exact name; some repos use `tests`, see above) and
run `pytest`:

```bash
uv pip install -e ".[test]"
pytest
```

Test layout is consistent across the core repos: a top-level `test/` directory (not `tests/`)
with a `unittests/` subdirectory, and `end2end/` for repos that ship end-to-end suites
(`ovos-core`, `ovos-audio`). `ovos-dinkum-listener` configures `[tool.pytest.ini_options]` in
its own `pyproject.toml`; check that section if `pytest` does not pick up its tests
automatically. `ovoscope` (installed as part of most `test` extras) is the same in-process
end-to-end tool used for skill and plugin testing; see [Test Your Skill](testing-your-skill.md)
for how it works.

---
**Read next:** [Contributing](contributing.md)
**Related:** [CLI Tools](cli-tools.md) · [Architecture Overview](architecture-overview.md) · [Test Your Skill](testing-your-skill.md)
