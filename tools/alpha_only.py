#!/usr/bin/env python3
"""Alpha-only content in the manual: one marker, and a script that strips it.

The manual documents the rolling prerelease channel beside the stable one. Two
things on a page belong to the prerelease channel alone:

* a block of prose that describes something no published stable release
  carries. It is marked with the canonical admonition, title and all:

      !!! warning "Alpha channel only"
          <what is prerelease-only here>

  A page that needs no page-specific wording includes the shared snippet
  instead, which renders the same admonition:

      --8<-- "snippets/alpha-only.md"

* an install command that needs the prerelease channel. The `--pre` flag is
  itself the marker: `pip install --pre <name>`.

`check` reports any other spelling of the first marker, so the set stays one
spelling. `strip` removes every marked block, every include of the snippet and
every `--pre` flag, which is what a stable-channel copy of the manual needs.
`census` prints the counts.

Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOCS_DIR = Path("docs")
SNIPPET = "snippets/alpha-only.md"
CANON_TITLE = "Alpha channel only"
CANON_LINE = f'!!! warning "{CANON_TITLE}"'
INCLUDE_RE = re.compile(r'^\s*--8<--\s+"snippets/alpha-only\.md"\s*$')
ADMONITION_RE = re.compile(r'^(?P<indent>\s*)(?:!!!|\?\?\?\+?)\s+\S+(?:\s+"(?P<title>[^"]*)")?\s*$')
PRE_FLAG_RE = re.compile(r"(?<=\s)--pre(?=\s)")

# An admonition whose title speaks about alpha, a prerelease or an unreleased
# state, yet does not mark alpha-only content. Each entry is a title and the
# reason it is not the canonical marker.
ALLOWED_TITLES = {
    "Alpha": "maturity of a named project, not content that only the prerelease carries",
    "Maturity: Alpha — most TTS plugins do not support SSML": "feature maturity, true on every channel",
    "Maturity: real streaming is pre-alpha": "feature maturity, true on every channel",
    "`--pre` is not scoped to OVOS": "teaches the flag itself, on the release-channels page",
    "Omitting `--pre` silently downgrades transitive dependencies": "teaches the flag itself",
}

FLAGGING_RE = re.compile(r"\balpha\b|\bpre-?release\b|\bunreleased\b|not yet published", re.I)


def pages() -> list[Path]:
    return sorted(p for p in DOCS_DIR.rglob("*.md") if p.parts[1] != "snippets")


def blocks(lines: list[str]) -> list[tuple[int, int, str | None]]:
    """Every admonition in the file, as (first line, line after the last, title)."""
    found = []
    i = 0
    while i < len(lines):
        m = ADMONITION_RE.match(lines[i])
        if not m:
            i += 1
            continue
        indent = len(m.group("indent"))
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if line.strip() == "":
                j += 1
                continue
            if len(line) - len(line.lstrip()) <= indent:
                break
            j += 1
        while j > i + 1 and lines[j - 1].strip() == "":
            j -= 1
        found.append((i, j, m.group("title")))
        i = j
    return found


def cmd_check(argv: argparse.Namespace) -> int:
    bad = []
    for p in pages():
        lines = p.read_text().split("\n")
        for start, _end, title in blocks(lines):
            if title is None or title == CANON_TITLE:
                continue
            if not FLAGGING_RE.search(title):
                continue
            if title in ALLOWED_TITLES:
                continue
            bad.append((p, start + 1, title))
    for p, ln, title in bad:
        print(f"{p}:{ln}: non-canonical alpha marker: \"{title}\"")
        print(f'    use {CANON_LINE}, or add the title to ALLOWED_TITLES with a reason')
    print(f"alpha-marker check: {len(bad)} non-canonical marker(s)")
    return 1 if bad else 0


def cmd_census(argv: argparse.Namespace) -> int:
    marked = includes = pre_pages = pre_hits = 0
    for p in pages():
        text = p.read_text()
        lines = text.split("\n")
        if CANON_LINE in text:
            marked += 1
        if any(INCLUDE_RE.match(l) for l in lines):
            includes += 1
        hits = len(PRE_FLAG_RE.findall(text))
        if hits:
            pre_pages += 1
            pre_hits += hits
    print(f"pages: {len(pages())}")
    print(f"pages with the canonical admonition: {marked}")
    print(f"pages including {SNIPPET}: {includes}")
    print(f"pages with a --pre command: {pre_pages} ({pre_hits} flags)")
    return 0


def cmd_strip(argv: argparse.Namespace) -> int:
    changed = 0
    for p in pages():
        lines = p.read_text().split("\n")
        drop: set[int] = set()
        for start, end, title in blocks(lines):
            if title == CANON_TITLE:
                drop.update(range(start, end))
        for i, line in enumerate(lines):
            if INCLUDE_RE.match(line):
                drop.add(i)
        text = p.read_text()
        pre_flags = len(PRE_FLAG_RE.findall(text))
        if not drop and not pre_flags:
            continue
        kept = [l for i, l in enumerate(lines) if i not in drop]
        new = PRE_FLAG_RE.sub("", "\n".join(kept))
        new = re.sub(r"[ \t]+\n", "\n", new)
        new = re.sub(r"\n{3,}", "\n\n", new)
        if new == text:
            continue
        changed += 1
        print(f"{p}: {len(drop)} marked line(s), {pre_flags} --pre flag(s)")
        if not argv.dry_run:
            p.write_text(new)
    print(f"alpha-only strip: {changed} page(s)" + (" (dry run)" if argv.dry_run else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="every alpha marker uses the canonical spelling")
    sub.add_parser("census", help="count the markers and the --pre commands")
    strip = sub.add_parser("strip", help="remove alpha-only content for a stable-channel copy")
    strip.add_argument("--dry-run", action="store_true", help="print, change nothing")
    args = ap.parse_args()
    if not DOCS_DIR.is_dir():
        print("run this from the repository root", file=sys.stderr)
        return 2
    return {"check": cmd_check, "census": cmd_census, "strip": cmd_strip}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
