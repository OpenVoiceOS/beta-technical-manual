
# Reusable Workflow Reference: PR Workflows

!!! abstract "In a nutshell"
    This page is an index. It points to the shared workflows that gate a pull request: build/install/test matrices, plugin (OPM) detection, license and repo-health checks, ovoscope skill tests, and the language-specific skill, locale, spec, intent-case, and TTS-intelligibility checks. Most post a section to the shared OVOS PR Checks comment (see the [PR Checks Comment Pattern](gh-automations-pr-comment-scripts.md#pr-checks-comment-pattern)). For version-bump and release workflows, see [Release Workflows](gh-automations-release-workflows.md). For lint, coverage, security scans, and notifications, see [Quality Workflows](gh-automations-quality-workflows.md). Start with the [gh-automations overview](gh-automations-overview.md) for the big picture, or the full [Workflow Reference index](gh-automations-workflows.md).

All reusable workflows are in `.github/workflows/` and are called via:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

> **Ref:** Always use `@dev`.

The individual workflows are listed once, in the
[Workflow Reference index](gh-automations-workflows.md). The PR-gate ones are
specified in detail on four topic pages:

- [Build Checks](gh-automations-build-checks.md): `build-tests.yml`, `channel-compat.yml`, and the deprecated `python-support.yml`.
- [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md): `opm-check.yml`, `license-check.yml`, `repo-health.yml`.
- [Skill and Locale Checks](gh-automations-repo-skill-checks.md): `skill-check.yml`, `locale-check.yml`, `spec-lint.yml`.
- [Skill Test Workflows](gh-automations-skill-test-workflows.md): `ovoscope.yml`, `intent-case-tests.yml`, `tts-intelligibility.yml`.

---
**Read next:** [Build Checks](gh-automations-build-checks.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md) · [Skill and Locale Checks](gh-automations-repo-skill-checks.md) · [Skill Test Workflows](gh-automations-skill-test-workflows.md) · [Workflow Reference](gh-automations-workflows.md) · [Quality Workflows](gh-automations-quality-workflows.md) · [Release Workflows](gh-automations-release-workflows.md)
