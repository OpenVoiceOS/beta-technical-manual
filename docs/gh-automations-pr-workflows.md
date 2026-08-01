
# Reusable Workflow Reference: PR Workflows

!!! abstract "In a nutshell"
    This page is an index. It points to the shared workflows that gate a pull request: build/install/test matrices, plugin (OPM) detection, license and repo-health checks, ovoscope skill tests, and the language-specific skill, locale, spec, intent-case, and TTS-intelligibility checks. Most post a section to the shared OVOS PR Checks comment (see the [PR Checks Comment Pattern](gh-automations-pr-comment-scripts.md#pr-checks-comment-pattern)). For version-bump and release workflows, see [Release Workflows](gh-automations-release-workflows.md). For lint, coverage, security scans, and notifications, see [Quality Workflows](gh-automations-quality-workflows.md). Start with the [gh-automations overview](gh-automations-overview.md) for the big picture, or the full [Workflow Reference index](gh-automations-workflows.md).

All reusable workflows are in `.github/workflows/` and are called via:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

> **Ref:** Always use `@dev`.

| Workflow / topic | What it does | Page |
|---|---|---|
| `build-tests.yml` | Build, install, and optionally test across a Python version matrix. | [Build Checks](gh-automations-build-checks.md#build-testsyml) |
| `python-support.yml` *(deprecated)* | Legacy install matrix across Python versions and install modes. | [Build Checks](gh-automations-build-checks.md#python-supportyml-deprecated) |
| `opm-check.yml` | OPM (OVOS Plugin Manager) plugin detection, interface validation, and import timing. | [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md#opm-checkyml) |
| `license-check.yml` | Scans dependencies for licenses incompatible with the OVOS universal donor policy. | [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md#license-checkyml) |
| `repo-health.yml` | Checks for required repo files and greets first-time contributors. | [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md#repo-healthyml) |
| `skill-check.yml` | Locale structure, language coverage, and `skill.json` validity for OVOS skills. | [Skill and Locale Checks](gh-automations-repo-skill-checks.md#skill-checkyml) |
| `locale-check.yml` | Verifies locale folders are correctly included in the package build. | [Skill and Locale Checks](gh-automations-repo-skill-checks.md#locale-checkyml) |
| `spec-lint.yml` | Runs `ovos-spec-lint` against a skill's locale folder (OVOS-INTENT-1 / OVOS-INTENT-2). | [Skill and Locale Checks](gh-automations-repo-skill-checks.md#spec-lintyml) |
| `ovoscope.yml` | Runs [ovoscope](ovoscope-overview.md) end-to-end skill tests. | [Skill Test Workflows](gh-automations-skill-test-workflows.md#ovoscopeyml) |
| `intent-case-tests.yml` | Runs the file-based ovoscope intent-routing accuracy matrix, sharded by language. | [Skill Test Workflows](gh-automations-skill-test-workflows.md#intent-case-testsyml) |
| `tts-intelligibility.yml` | Synthesises speech, transcribes it back with reference STT, and scores WER/CER. | [Skill Test Workflows](gh-automations-skill-test-workflows.md#tts-intelligibilityyml) |

---
**Read next:** [Build Checks](gh-automations-build-checks.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [Plugin, License, and Repo Checks](gh-automations-plugin-repo-checks.md) · [Skill and Locale Checks](gh-automations-repo-skill-checks.md) · [Skill Test Workflows](gh-automations-skill-test-workflows.md) · [Workflow Reference](gh-automations-workflows.md) · [Quality Workflows](gh-automations-quality-workflows.md) · [Release Workflows](gh-automations-release-workflows.md)
