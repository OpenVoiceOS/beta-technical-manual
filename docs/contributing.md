# Contributing & Project Status

!!! abstract "In a nutshell"
    OVOS is built from many small, independent repositories rather than one monolith. This
    page is a map for anyone who wants to send in a fix: how a change actually gets from your
    laptop into a released package, where the code lives, how "does this actually follow the
    spec" gets checked, and where to ask if you get stuck.

## How a change reaches a release

Every OVOS repository publishes through the same shared pipeline, described in full on the
[gh-automations](gh-automations-overview.md) page:

1. **Branch**: work happens on a feature branch, not directly on `dev`.
2. **Pull request into `dev`**: opening a PR against `dev` triggers the shared **OVOS PR
   Checks**: build/install/test, license and dependency scanning, plugin-manifest detection
   (for plugin repos), coverage, and a version-bump preview. These checks post their results
   as a single comment on the PR. A PR merges once they pass.
3. **Merge to `dev`**: a merged PR triggers an automatic alpha release to PyPI, so the change
   is installable (as a pre-release) right away.
4. **Promotion to stable**: periodically, a release PR rolls accumulated `dev` changes into
   `master`. Merging it tags and publishes the stable release.

See [Release Flow](gh-automations-release.md) and [Workflow Reference](gh-automations-workflows.md)
for the full mechanics, including how versions are bumped from conventional-commit prefixes.

## Finding the code

OVOS is split across many small repositories: one per plugin, one per core service, one per
skill. The [OVOS Repository Index](ecosystem-index.md) is the map of every public repository in
the project. The [Plugin Ecosystem](plugins-index.md) page is the narrower view of installable
plugins by category (STT, TTS, wake word, and so on). Start there rather than guessing a repo
name.

## How "spec-correct" is checked

Core subsystems (the messagebus, the audio pipeline, OCP, and others) are backed by written
**architecture specs**. See the [spec index](architecture-specs.md). Conformance to those specs
isn't just asserted in prose. [`ovos-test-harness`](https://github.com/OpenVoiceOS/ovos-test-harness)
is an executable conformance suite that exercises a running OVOS instance against the spec's
observable behavior. See [Specs & Tooling](spec-tooling.md) for how the specs, the harness, and
the message-spec definitions fit together.

## Testing your change locally

The shared **OVOS PR Checks** above catch a broken change, but waiting for CI to tell you is the
slow way to find out. Run the same kind of check locally first:

- **Skills and plugins**: use [`ovoscope`](ovoscope-overview.md), the official end-to-end test
  tool. It runs a small in-process pretend assistant, so you can confirm a request is understood
  and answered correctly without real hardware or a full install. Every official OVOS skill must
  pass `ovoscope` E2E tests, so writing one for your change also writes the test
  the PR check will run.
- **Core repositories** (`ovos-core`, `ovos-bus-client`, `ovos-utils`, and the other libraries
  under [the repository index](ecosystem-index.md)): run that repo's own `pytest` suite from a
  checkout before opening the PR: `pip install -e .[test]` (or the extra the repo's
  `pyproject.toml` names for tests), then `pytest`.

Either way, the goal is the same. Catch a failure on your own machine, where you can iterate on
it in seconds, instead of finding out from a CI comment minutes later.

## Writing a skill or plugin

If you're contributing a new ability rather than a core fix, start with
[Your first skill](first-skill.md) for the step-by-step tutorial, or
[Anatomy of a Skill](skill-structure.md) for the reference structure. For plugins (a new STT
engine, TTS voice, wake word, and so on), browse the [Plugin Ecosystem](plugins-index.md) page for the
category you're extending, and use an existing plugin in that category as a template. The plugin
base classes referenced throughout this manual (for example, the [TTS plugin template](tts-plugins.md#plugin-template))
are the contract your plugin's entry point needs to satisfy.

## Where to ask

- **[Skills channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org)**: quick
  questions while writing a skill.
- **[Open Conversational AI forum](https://community.openconversational.ai/)**: longer
  questions, design discussion, or anything that needs more than a chat message.

See [Skill Dev FAQ](skill-dev-faq.md) for answers to the questions that come up most, and
[Troubleshooting](troubleshooting.md#where-to-ask-for-help) for what to include when you ask
for help (a log excerpt or `ovos-busmon` export for the stage where things went wrong).
