
# Reusable Workflow Reference: Quality Workflows

!!! abstract "In a nutshell"
    This page is an index. It points to the shared workflows for code quality and housekeeping: coverage reporting, dependency security scanning, lint, type-checking, docs presence, and Matrix chat notifications, plus the shared PR-comment pattern and Python scripts. For version-bump and release workflows, see [Release Workflows](gh-automations-release-workflows.md). For the PR-gate checks (build tests, plugin detection, skill checks), see [PR Workflows](gh-automations-pr-workflows.md). Start with the [gh-automations overview](gh-automations-overview.md) for the big picture, or the full [Workflow Reference index](gh-automations-workflows.md).

All reusable workflows are in `.github/workflows/` and are called via:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

> **Ref:** Always use `@dev`.

| Workflow / topic | What it does | Page |
|---|---|---|
| `coverage.yml` | Runs `pytest --cov`, posts a coverage report, and optionally deploys HTML to `gh-pages`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#coverageyml) |
| `coverage-pages.yml` *(deprecated)* | Legacy coverage-to-`gh-pages` deployment, replaced by `coverage.yml`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#coverage-pagesyml-deprecated) |
| `pip-audit.yml` | Scans dependencies for known CVEs and optionally uploads a SARIF report. | [Coverage and Security Workflows](gh-automations-coverage-security.md#pip-audityml) |
| `downstream-check.yml` | Reports which packages depend on a given package, using `pipdeptree`. | [Coverage and Security Workflows](gh-automations-coverage-security.md#downstream-checkyml) |
| `lint.yml` | Runs `ruff` and/or `pre-commit`. | [Lint and Docs Workflows](gh-automations-lint-docs.md#lintyml) |
| `type-check.yml` | Runs `mypy`, informational only unless `fail_on_errors: true`. | [Lint and Docs Workflows](gh-automations-lint-docs.md#type-checkyml) |
| `docs-check.yml` | Verifies required documentation files exist and optionally lints Markdown. | [Lint and Docs Workflows](gh-automations-lint-docs.md#docs-checkyml) |
| `notify-matrix.yml` | Sends a message to the OVOS Matrix channel. | [Lint and Docs Workflows](gh-automations-lint-docs.md#notify-matrixyml) |
| PR Checks Comment Pattern | How workflows post a named section into the single shared OVOS PR Checks comment. | [PR Comment Pattern and Scripts](gh-automations-pr-comment-scripts.md#pr-checks-comment-pattern) |
| Scripts Reference | The Python scripts every workflow above checks out at run time. | [PR Comment Pattern and Scripts](gh-automations-pr-comment-scripts.md#scripts-reference) |

---
**Read next:** [gh-automations Coverage and Security Workflows](gh-automations-coverage-security.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [PR Comment Pattern and Scripts](gh-automations-pr-comment-scripts.md) · [Workflow Reference](gh-automations-workflows.md) · [PR Check Workflows](gh-automations-pr-workflows.md) · [Release Workflows](gh-automations-release-workflows.md)
