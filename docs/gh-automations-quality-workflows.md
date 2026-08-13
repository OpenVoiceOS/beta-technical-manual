
# Reusable Workflow Reference: Quality Workflows

!!! abstract "In a nutshell"
    This page is an index. It points to the shared workflows for code quality and housekeeping: coverage reporting, dependency security scanning, lint, type-checking, docs presence, and Matrix chat notifications, plus the shared PR-comment pattern and Python scripts. For version-bump and release workflows, see [Release Workflows](gh-automations-release-workflows.md). For the PR-gate checks (build tests, plugin detection, skill checks), see [PR Workflows](gh-automations-pr-workflows.md). Start with the [gh-automations overview](gh-automations-overview.md) for the big picture, or the full [Workflow Reference index](gh-automations-workflows.md).

All reusable workflows are in `.github/workflows/` and are called via:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

> **Ref:** Always use `@dev`.

The individual workflows are listed once, in the
[Workflow Reference index](gh-automations-workflows.md). The quality and
housekeeping ones are specified in detail on three topic pages:

- [Coverage and Security Workflows](gh-automations-coverage-security.md): `coverage.yml`, `pip-audit.yml`, `downstream-check.yml`, and the deprecated `coverage-pages.yml`.
- [Lint and Docs Workflows](gh-automations-lint-docs.md): `lint.yml`, `type-check.yml`, `docs-check.yml`, `notify-matrix.yml`.
- [PR Comment Pattern and Scripts](gh-automations-pr-comment-scripts.md): the shared OVOS PR Checks comment mechanism and the Python scripts the workflows check out at run time.

---
**Read next:** [gh-automations Coverage and Security Workflows](gh-automations-coverage-security.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [PR Comment Pattern and Scripts](gh-automations-pr-comment-scripts.md) · [Workflow Reference](gh-automations-workflows.md) · [PR Check Workflows](gh-automations-pr-workflows.md) · [Release Workflows](gh-automations-release-workflows.md)
