
# Reusable Workflow Reference: PR Comment Pattern and Scripts

!!! abstract "In a nutshell"
    This page documents machinery shared across every reusable workflow: the pattern that lets many workflows post their result as a named section in a single shared PR comment, and the Python scripts each workflow checks out at run time to do its work. For the coverage and security workflows, see [Coverage and Security Workflows](gh-automations-coverage-security.md). For lint, type-check, docs, and notification workflows, see [Lint and Docs Workflows](gh-automations-lint-docs.md). Start with the [gh-automations overview](gh-automations-overview.md) for the big picture, or the full [Workflow Reference index](gh-automations-workflows.md).

The bot prefixes every PR-comment section title with an emoji tag. This page names those titles in backticks without the emoji, except in the one raw example under [PR Checks Comment Pattern](#pr-checks-comment-pattern).

---
## PR Checks Comment Pattern

The following workflows post their results as named sections in a **single shared PR comment** rather than separate bot comments. The bot prefixes every section title with an emoji tag. The tables below give the title text and name that tag in words.

| Workflow | Section title | Tag emoji |
|----------|---------------|-----------|
| `repo-health.yml` | `Repo Health` (+ `Welcome` for first-time contributors) | clipboard (+ waving hand) |
| `release-preview.yml` | `Release Preview` | label |
| `pip-audit.yml` | `Security (pip-audit)` | lock |
| `license-check.yml` | `License Check` | balance scale |
| `build-tests.yml` | `Build Tests` | hammer |
| `opm-check.yml` | `Plugin Detection` | plug |

| Workflow | Section title | Tag emoji |
|----------|---------------|-----------|
| `ovoscope.yml` | `Skill Tests (ovoscope)` (+ `Bus Coverage`) | plug (+ bus) |
| `intent-case-tests.yml` | `Intent-Case Accuracy` | target |
| `tts-intelligibility.yml` | `TTS Intelligibility` | speaking head |
| `coverage.yml` | `Coverage` | bar chart |
| `skill-check.yml` | `Skill` | microphone |
| `type-check.yml` | `Type Check` | magnifying glass |
| `docs-check.yml` | `Docs` | books |
| `lint.yml` | lint results | none |
| `python-support.yml` *(deprecated)* | `Python Support` | snake |

The HTML marker `<!-- ovos-pr-checks -->` identifies the comment in its body. Each workflow manages its own section:

```text
<!-- ovos-pr-checks -->

## OVOS PR Checks

<!-- section:health -->

### 📋 Repo Health
✅ All required files present.
...
<!-- /section:health -->

<!-- section:build -->

### 🔨 Build Tests
✅ All versions pass
...
<!-- /section:build -->

<!-- section:opm -->

### 🔌 Plugin Detection
✅ Plugin Status: PASS
...
<!-- /section:opm -->

<!-- section:ovoscope -->

### 🔌 Skill Tests (ovoscope)
✅ 9/9 passed
...
<!-- /section:ovoscope -->

<!-- section:coverage -->

### 📊 Coverage
✅ **87.3%** total coverage
...
<!-- /section:coverage -->

<!-- section:license -->

### ⚖️ License Check
✅ No license violations found (42 packages).
...
<!-- /section:license -->

<!-- section:security -->

### 🔒 Security (pip-audit)
✅ No known vulnerabilities found.
...
<!-- /section:security -->

<!-- section:release -->

### 🏷️ Release Preview
**Current:** `0.0.1a4` → **Next:** `0.0.2a1`
...
<!-- /section:release -->

```

Sections appear as each workflow completes. Reruns update only the relevant section without touching others.

The aggregation logic lives in `scripts/update_pr_comment.py`, see the [Scripts Reference](#scripts-reference) below.

### Adding a new section

To add a new check type to the aggregated comment from any workflow:

1. Generate the section content as a markdown file (e.g. `/tmp/my-section.md`).


2. Check out gh-automations and call the script:

```yaml

- name: Checkout gh-automations scripts
  if: github.event_name == 'pull_request'
  uses: actions/checkout@v7
  with:
    repository: OpenVoiceOS/gh-automations
    ref: dev
    path: _gh_automations/

- name: Post section to PR comment
  if: github.event_name == 'pull_request'
  run: |
    python3 _gh_automations/scripts/update_pr_comment.py \
      --repo "${{ github.repository }}" \
      --pr "${{ github.event.pull_request.number }}" \
      --section-id "my-check" \
      --title "🔍 My Check" \
      --content-file /tmp/my-section.md
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

The `permissions: pull-requests: write` must be declared on the calling job.

---

## Scripts Reference

The following Python scripts are checked out from this repo at workflow run time and are not installed as a Python package.

### `scripts/_version_utils.py`

Shared version-block parsing utilities imported by all other scripts.

**Key functions:**

- `read_version(version_file: str) -> tuple[int, int, int, int]`, parses `START_VERSION_BLOCK/END_VERSION_BLOCK`, returns `(major, minor, build, alpha)`


- `format_version(major, minor, build, alpha) -> str`, formats PEP 440 string


- `write_version_block(version_file, major, minor, build, alpha)`, rewrites only the block, preserving all surrounding content

### `scripts/update_version.py`

Bumps the version in a `version.py` file.

**Key function:** `update_version(part: str, version_file: str) -> str`

```text
usage: update_version.py <part> --version-file <path>

part: major | minor | build | alpha

```

Bump rules:

| Part | Effect |
|------|--------|
| `major` | `MAJOR += 1`, `MINOR = 0`, `BUILD = 0`, `ALPHA = 1` |
| `minor` | `MINOR += 1`, `BUILD = 0`, `ALPHA = 1` |
| `build` | `BUILD += 1`, `ALPHA = 1` |

| Part | Effect |
|------|--------|
| `alpha` | `ALPHA += 1`. If currently stable (`ALPHA == 0`), `BUILD += 1` first |

### `scripts/remove_alpha.py`

Sets `VERSION_ALPHA = 0` in a `version.py` file (declares stable).

**Key function:** `update_alpha(version_file: str)`

```text
usage: remove_alpha.py --version-file <path>

```

### `scripts/get_version.py`

Reads and prints the version string from a `version.py` file. Works without installing the package.

**Key function:** `get_version(version_file: str) -> str`

```text
usage: get_version.py --version-file <path>

```

Output example: `1.2.3a4` or `1.2.3`

### `scripts/check_downstream.py`

Reports which installed packages depend on a given package, using `pipdeptree`. Output is sorted deterministically and uploaded as a workflow artifact. The older commit-to-repo behavior is gone. The `commit_branch` input is deprecated and ignored.

**Key function:** `get_downstream(package_name: str) -> str`

**Helper:** `sort_pipdeptree_output(text: str) -> str`

```text
usage: check_downstream.py --package <name> --output <file>

```

Requires `pipdeptree` to be installed in the environment before calling.

### `scripts/check_opm.py`

Detects and validates OVOS plugins via OPM. Supports multi-plugin-type repos. Outputs a structured JSON report.

**Key functions:**

- `auto_detect_plugin_types()`, scans `[project.entry-points."opm.*"]` in `pyproject.toml` or `setup.py`


- `validate_plugin_import(module_path, class_name)`, imports the class, measures time in ms, detects missing dependencies


- `check_plugin_interface(plugin_cls, short_type)`, verifies `issubclass()` against the correct abstract base (~30 types, including the `agents.*` family, `vc`, and `wake_word.verifier`)


- `extract_metadata()`, reads name, version, authors, description, homepage, requires_python


- `extract_system_deps()`, reads `[tool.ovos.build] system-dependencies`


- `validate_config_docs(repo_root)`, searches for `settingsmeta.json`


- `collect_issues(result)`, aggregates issues list


- `compute_status(issues)`, returns `pass`, `warning`, or `fail`


- `check_opm(plugin_type, entry_point, output_json, ...)`, main entry point

```text
usage: check_opm.py \
    [--plugin-type auto|skill|tts|stt|wake_word|vad|phal|pipeline|utterance_transformer|tts_transformer|g2p] \
    [--entry-point <id>] \
    [--output-json <path>] \
    [--validate-interface | --no-validate-interface] \
    [--test-import | --no-test-import] \
    [--perf-threshold-ms <ms>]

```

### `scripts/check_skill.py`

Analyses a checked-out OVOS skill repository. Outputs a JSON report. Stdlib only.

**Key functions:**

- `is_skill_repo(repo_root)`


- `find_locale_dir(repo_root, override="")`


- `check_translation_completeness(locale_dir, en_us_files)`


- `run_checks(repo_root, locale_dir_override="")`

```text
usage: check_skill.py [--repo-root .] [--locale-dir ""] [--output-json /tmp/skill-report.json]

```

### `scripts/check_release.py`

Reads `version.py`, predicts next version from PR labels/title. Stdlib only.

**Key functions:**

- `detect_bump_part(labels, pr_title)`


- `compute_next_version(major, minor, build, alpha, part)`


- `run_checks(version_file, pr_labels_json, pr_title)`

```text
usage: check_release.py --version-file version.py \
    [--pr-labels-json "[]"] \
    [--pr-title ""] \
    [--output-json /tmp/release-report.json]

env vars (override CLI): PR_LABELS_JSON, PR_TITLE

```

### `scripts/update_pr_comment.py`

Manages the shared **OVOS PR Checks** comment on a pull request. Finds the comment by the invisible HTML marker `<!-- ovos-pr-checks -->`, then replaces or appends the named section. Creates the comment if it doesn't exist yet.

Uses only Python stdlib (`urllib`, `json`, `re`), no extra dependencies.

**Key logic:**

- `find_ovos_comments(repo, pr_number)`, paginates the PR comments API and returns the list of comments carrying the marker


- `insert_or_replace_section(body, section_id, title, content)`, regex replace within `<!-- section:X --> … <!-- /section:X -->` delimiters

```text
usage: update_pr_comment.py \
    --repo owner/repo \
    --pr 123 \
    --section-id coverage \
    --title "📊 Coverage" \
    --content-file /tmp/section.md

environment: GITHUB_TOKEN   (required)

```

---

*Source code: [OpenVoiceOS/gh-automations](https://github.com/OpenVoiceOS/gh-automations).*

---
**Read next:** [gh-automations Quality Workflows](gh-automations-quality-workflows.md)
**Related:** [gh-automations Overview](gh-automations-overview.md) · [Coverage and Security Workflows](gh-automations-coverage-security.md) · [Lint and Docs Workflows](gh-automations-lint-docs.md) · [Workflow Reference](gh-automations-workflows.md)
