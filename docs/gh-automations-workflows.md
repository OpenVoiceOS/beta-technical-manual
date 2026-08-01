
# Reusable Workflow Reference

!!! abstract "In a nutshell"
    This page is the index to the detailed reference for every shared automation recipe ("workflow") that OVOS projects can plug in. The full specs live on three pages, split by lifecycle stage: [release](gh-automations-release-workflows.md) (publish, version bump), [PR](gh-automations-pr-workflows.md) (build, test, and check gates run on pull requests), and [quality](gh-automations-quality-workflows.md) (lint, coverage, security scans, notifications). This index is aimed at maintainers wiring up a project's testing and release machinery; if you just want the big picture of what these automations are for, start with the [gh-automations overview](gh-automations-overview.md). See also the [Glossary](glossary.md).

All reusable workflows are in `.github/workflows/` and are called via:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

> **Ref:** Always use `@dev`.

## Workflow index

| Workflow | Purpose | Documented on |
|----------|---------|---------------|
| `publish-alpha.yml` | Bumps the version on PR merge to `dev` and opens a release PR to `master`. | [Release Workflows](gh-automations-release-workflows.md#publish-alphayml) |
| `publish-stable.yml` | Removes the alpha suffix and tags a stable GitHub release on push to `master`. | [Release Workflows](gh-automations-release-workflows.md#publish-stableyml) |
| `release-preview.yml` | Predicts the next version from PR labels/title and posts a preview to the PR comment. | [Release Workflows](gh-automations-release-workflows.md#release-previewyml) |
| `build-tests.yml` | Runs build, install, and optional tests across a Python version matrix. | [PR Workflows](gh-automations-pr-workflows.md#build-testsyml) |
| `opm-check.yml` | Verifies the package is discoverable and valid as an OVOS plugin (OPM). | [PR Workflows](gh-automations-pr-workflows.md#opm-checkyml) |
| `ovoscope.yml` | Runs ovoscope end-to-end skill tests on a single Python version. | [PR Workflows](gh-automations-pr-workflows.md#ovoscopeyml) |
| `license-check.yml` | Checks installed dependencies against the OVOS universal donor license policy. | [PR Workflows](gh-automations-pr-workflows.md#license-checkyml) |
| `repo-health.yml` | Checks for required repo files and greets first-time contributors. | [PR Workflows](gh-automations-pr-workflows.md#repo-healthyml) |
| `skill-check.yml` | Analyses an OVOS skill repo for locale structure and `skill.json` validity. | [PR Workflows](gh-automations-pr-workflows.md#skill-checkyml) |
| `python-support.yml` *(deprecated)* | Legacy install matrix across Python versions and install modes. | [PR Workflows](gh-automations-pr-workflows.md#python-supportyml-deprecated) |
| `locale-check.yml` | Verifies locale folders are correctly included in the package build. | [PR Workflows](gh-automations-pr-workflows.md#locale-checkyml) |
| `spec-lint.yml` | Runs `ovos-spec-lint` against a skill's locale folder for OVOS-INTENT-1/2 conformance. | [PR Workflows](gh-automations-pr-workflows.md#spec-lintyml) |
| `intent-case-tests.yml` | Runs the file-based ovoscope intent-routing accuracy matrix, sharded by language. | [PR Workflows](gh-automations-pr-workflows.md#intent-case-testsyml) |
| `tts-intelligibility.yml` | Scores TTS output intelligibility via a synthesize-then-transcribe round trip. | [PR Workflows](gh-automations-pr-workflows.md#tts-intelligibilityyml) |
| `coverage.yml` | Runs `pytest --cov`, posts a coverage report, and optionally deploys HTML to `gh-pages`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#coverageyml) |
| `coverage-pages.yml` *(deprecated)* | Legacy coverage-to-`gh-pages` deployment, replaced by `coverage.yml`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#coverage-pagesyml-deprecated) |
| `pip-audit.yml` | Scans dependencies for known CVEs and optionally uploads a SARIF report. | [Coverage and Security Workflows](gh-automations-coverage-security.md#pip-audityml) |
| `downstream-check.yml` | Reports which packages depend on a given package, using `pipdeptree`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#downstream-checkyml) |
| `lint.yml` | Runs `ruff` and/or `pre-commit`. | [Lint and Docs Workflows](gh-automations-lint-docs.md#lintyml) |
| `type-check.yml` | Runs `mypy`, informational only unless `fail_on_errors: true`. | [Lint and Docs Workflows](gh-automations-lint-docs.md#type-checkyml) |
| `docs-check.yml` | Verifies required documentation files exist and optionally lints Markdown. | [Lint and Docs Workflows](gh-automations-lint-docs.md#docs-checkyml) |
| `notify-matrix.yml` | Sends a message to the OVOS Matrix channel. | [Lint and Docs Workflows](gh-automations-lint-docs.md#notify-matrixyml) |

The [PR Checks Comment Pattern](gh-automations-pr-comment-scripts.md#pr-checks-comment-pattern) and [Scripts Reference](gh-automations-pr-comment-scripts.md#scripts-reference) sections, describing the shared PR-comment mechanism and the Python scripts used across all of the above workflows, live on the PR Comment Pattern and Scripts page.

---

*Source code: [OpenVoiceOS/gh-automations](https://github.com/OpenVoiceOS/gh-automations).*

---
**Read next:** [PR Check Workflows](gh-automations-pr-workflows.md) · [Quality Workflows](gh-automations-quality-workflows.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [Release Workflows](gh-automations-release-workflows.md) · [Release Flow](gh-automations-release.md) · [Contributing](contributing.md)
