#!/usr/bin/env python3
"""Tests for tools/alpha_only.py. Stdlib only: `python3 tools/test_alpha_only.py`.

Each test states the defect it holds shut. A test of a defect fails against the
version of the script that carries it, which is what makes it a test and not a
restatement. The rest are controls, and pass on both versions.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import alpha_only  # noqa: E402


@contextlib.contextmanager
def manual(pages: dict[str, str]):
    """A throwaway manual: {page name: text}, with the script pointed at it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        for name, text in pages.items():
            (root / "docs" / name).write_text(text)
        cwd = os.getcwd()
        os.chdir(root)
        try:
            yield root
        finally:
            os.chdir(cwd)


def run(command, **kwargs) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = command(argparse.Namespace(**kwargs))
    return code, out.getvalue()


MARKED = '!!! warning "Alpha channel only"\n    Only the prerelease has this.\n'


class StripKeepsNoContradiction(unittest.TestCase):
    """A stable copy must not ask for a flag its commands no longer carry."""

    PAGE = (
        "# Persona server\n"
        "\n"
        "Use `--pre` and a floor pin:\n"
        "\n"
        "```bash\n"
        "pip install --pre ovos-persona-server\n"
        "```\n"
    )

    def test_strip_fails_and_names_the_surviving_mention(self):
        with manual({"persona-server.md": self.PAGE}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
        self.assertEqual(code, 1, out)
        self.assertIn("docs/persona-server.md:3", out)
        self.assertIn("surviving mention(s) of --pre", out)

    def test_a_page_whose_prose_does_not_name_the_flag_passes(self):
        page = self.PAGE.replace("Use `--pre` and a floor pin:", "Install it:")
        with manual({"persona-server.md": page}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/persona-server.md").read_text()
        self.assertEqual(code, 0, out)
        self.assertIn("pip install ovos-persona-server", text)


class StripLeavesOneSpace(unittest.TestCase):
    """Removing the flag must not leave the space that was in front of it."""

    def test_no_double_space_in_the_command(self):
        page = "# Page\n\n```bash\npip install --pre ovos-example\n```\n"
        with manual({"page.md": page}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/page.md").read_text()
        self.assertEqual(code, 0, out)
        self.assertIn("pip install ovos-example", text)
        self.assertNotIn("install  ", text)

    def test_a_flag_inside_a_longer_word_is_left_alone(self):
        page = "# Page\n\n```bash\nuv pip install --prerelease=allow ovos-example\n```\n"
        with manual({"page.md": page}):
            run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/page.md").read_text()
        self.assertIn("--prerelease=allow", text)


class OneMarkerPredicate(unittest.TestCase):
    """check, census and strip must agree on what the marker is."""

    NOTE_MARKER = (
        "# Page\n"
        "\n"
        '!!! note "Alpha channel only"\n'
        "    Only the prerelease has this.\n"
    )

    def test_check_reports_the_canonical_title_on_another_admonition(self):
        with manual({"page.md": self.NOTE_MARKER}):
            code, out = run(alpha_only.cmd_check)
        self.assertEqual(code, 1, out)
        self.assertIn("the canonical title on `!!! note`", out)

    def test_census_does_not_count_it(self):
        with manual({"page.md": self.NOTE_MARKER}):
            _code, out = run(alpha_only.cmd_census)
        self.assertIn("pages with the canonical admonition: 0", out)

    def test_strip_does_not_delete_it(self):
        with manual({"page.md": self.NOTE_MARKER}):
            run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/page.md").read_text()
        self.assertIn('!!! note "Alpha channel only"', text)

    def test_the_marker_itself_is_counted_and_removed(self):
        with manual({"page.md": "# Page\n\n" + MARKED}):
            code, check_out = run(alpha_only.cmd_check)
            _c, census_out = run(alpha_only.cmd_census)
            run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/page.md").read_text()
        self.assertEqual(code, 0, check_out)
        self.assertIn("pages with the canonical admonition: 1", census_out)
        self.assertNotIn("Alpha channel only", text)


class FlagRegexesAgree(unittest.TestCase):
    """The counting regex and the cutting regex must see the same flags."""

    def test_same_count(self):
        text = "pip install --pre a\nuv pip install --pre b --pre c\n--prerelease x\n"
        self.assertEqual(
            len(alpha_only.PRE_FLAG_RE.findall(text)),
            len(alpha_only.PRE_FLAG_CUT_RE.findall(text)),
        )


class StripFailsOnEveryRun(unittest.TestCase):
    """An already stripped manual must fail the same way the first run did."""

    STRIPPED = (
        "# Persona server\n"
        "\n"
        "Use `--pre` and a floor pin:\n"
        "\n"
        "```bash\n"
        "pip install ovos-persona-server\n"
        "```\n"
    )

    def test_a_page_the_strip_does_not_change_is_still_scanned(self):
        with manual({"persona-server.md": self.STRIPPED}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
        self.assertEqual(code, 1, out)
        self.assertIn("docs/persona-server.md:3", out)
        self.assertIn("0 page(s)", out)

    def test_the_second_run_fails_like_the_first(self):
        page = self.STRIPPED.replace(
            "pip install ovos-persona-server", "pip install --pre ovos-persona-server")
        with manual({"persona-server.md": page}):
            first, first_out = run(alpha_only.cmd_strip, dry_run=False)
            second, second_out = run(alpha_only.cmd_strip, dry_run=False)
        self.assertEqual(first, 1, first_out)
        self.assertEqual(second, 1, second_out)
        self.assertIn("docs/persona-server.md:3", second_out)


class AllowedAdmonitionsAreNotReported(unittest.TestCase):
    """A block strip keeps by policy must not be a mention strip reports."""

    ALLOWED = (
        "# Release channels\n"
        "\n"
        '!!! warning "`--pre` is not scoped to OVOS"\n'
        "    `--pre` tells pip to allow pre-release versions of every dependency.\n"
    )

    def test_the_title_and_the_body_pass(self):
        # The page also carries a flag to cut, so the strip changes it and a
        # scan of the changed page alone would still read the allowed block.
        page = self.ALLOWED + "\n```bash\npip install --pre ovos-core\n```\n"
        with manual({"release-channels.md": page}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
            text = Path("docs/release-channels.md").read_text()
        self.assertEqual(code, 0, out)
        self.assertNotIn("surviving mention(s)", out)
        self.assertIn("pip install ovos-core", text)
        self.assertIn("`--pre` is not scoped to OVOS", text)

    def test_an_ordinary_admonition_body_is_still_reported(self):
        page = self.ALLOWED.replace("`--pre` is not scoped to OVOS", "Read this first")
        with manual({"release-channels.md": page}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
        self.assertEqual(code, 1, out)
        self.assertIn("docs/release-channels.md:4", out)

    def test_prose_outside_the_allowed_block_is_still_reported(self):
        page = self.ALLOWED + "\n- Using `--pre` installs pre-releases everywhere.\n"
        with manual({"release-channels.md": page}):
            code, out = run(alpha_only.cmd_strip, dry_run=False)
        self.assertEqual(code, 1, out)
        self.assertIn("docs/release-channels.md:6", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
