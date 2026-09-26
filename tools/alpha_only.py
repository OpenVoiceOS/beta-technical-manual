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
every `--pre` flag, which is what a stable-channel copy of the manual needs. It
then refuses to call that copy finished while a line still asks for a prerelease:
a sentence that names the flag, or an install whose requirement floor is a
prerelease version, which the stable channel cannot resolve.
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
ADMONITION_RE = re.compile(r'^(?P<indent>\s*)(?:!!!|\?\?\?\+?)\s+(?P<kind>\S+)(?:\s+"(?P<title>[^"]*)")?\s*$')
# The flag as a word, for counting and for detection.
PRE_FLAG_RE = re.compile(r"(?<=\s)--pre(?=\s)")
# The same flag with the one space or tab before it, so removing it leaves no
# double space behind.
PRE_FLAG_CUT_RE = re.compile(r"[ \t]--pre(?=\s)")
# Any mention of the flag, the backticked one in prose included. A stable copy
# must hold none of these: a sentence that asks for the flag, beside a command
# that no longer carries it, contradicts itself. A body under a title in
# ALLOWED_TITLES is the exception, because such a title keeps its block on every
# channel and its subject is the flag itself.
PRE_MENTION_RE = re.compile(r"--pre\b")

# An install command whose requirement floor is a prerelease version. The flag
# and the floor say the same thing twice: `pip install --pre "name>=1.2.3a1"`
# keeps asking for a prerelease after the strip has taken the flag away, and the
# stable channel has nothing that satisfies the floor, so pip resolves nothing
# and the command fails. Only a line that installs is read: a page that names
# such a pin to describe a channel file (`ovos-audio>=2.1.1a1` in the
# constraints tables) is correct on every channel.
INSTALL_RE = re.compile(r"\b(?:pip[0-9]?|pipx|uv pip)\s+install\b")
PRERELEASE_REQ_RE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._-]*"          # distribution name
    r"(?:\[[^\]]*\])?"                     # optional extras
    r"\s*(?:==|>=|~=|>)\s*"
    r"\d+(?:\.\d+)*(?:a|b|rc|\.dev)\d*"    # a floor no stable release meets
)

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

CANON_KIND = "warning"


def is_marker(kind: str | None, title: str | None) -> bool:
    """The one test for the canonical marker. check, census and strip share it.

    Both halves count. A canonical title on another admonition type is not the
    marker: `check` reports it, `census` does not count it, and `strip` leaves
    it in place, so no content disappears through a spelling `check` accepts.
    """
    return kind == CANON_KIND and title == CANON_TITLE


def pages() -> list[Path]:
    return sorted(p for p in DOCS_DIR.rglob("*.md") if p.parts[1] != "snippets")


def blocks(lines: list[str]) -> list[tuple[int, int, str, str | None]]:
    """Every admonition, as (first line, line after the last, kind, title)."""
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
        found.append((i, j, m.group("kind"), m.group("title")))
        i = j
    return found


def cmd_check(argv: argparse.Namespace) -> int:
    bad = []
    for p in pages():
        lines = p.read_text().split("\n")
        for start, _end, kind, title in blocks(lines):
            if title is None or is_marker(kind, title):
                continue
            if title == CANON_TITLE:
                bad.append((p, start + 1, title,
                            f"the canonical title on `!!! {kind}`; the marker is `!!! {CANON_KIND}`"))
                continue
            if not FLAGGING_RE.search(title) or title in ALLOWED_TITLES:
                continue
            bad.append((p, start + 1, title,
                        "another spelling of the marker"))
    for p, ln, title, why in bad:
        print(f'{p}:{ln}: {why}: "{title}"')
        print(f"    use {CANON_LINE}, or add the title to ALLOWED_TITLES with a reason")
    print(f"alpha-marker check: {len(bad)} non-canonical marker(s)")
    return 1 if bad else 0


def cmd_census(argv: argparse.Namespace) -> int:
    marked = includes = pre_pages = pre_hits = 0
    for p in pages():
        text = p.read_text()
        lines = text.split("\n")
        if any(is_marker(kind, title) for _s, _e, kind, title in blocks(lines)):
            marked += 1
        if any(INCLUDE_RE.match(line) for line in lines):
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


def strip_text(text: str) -> str:
    """The stable-channel form of one page: no marked block, no include, no flag."""
    lines = text.split("\n")
    drop: set[int] = set()
    for start, end, kind, title in blocks(lines):
        if is_marker(kind, title):
            drop.update(range(start, end))
    for i, line in enumerate(lines):
        if INCLUDE_RE.match(line):
            drop.add(i)
    if not drop and not PRE_FLAG_RE.search(text):
        # Nothing of the prerelease channel here. Do not reflow the page.
        return text
    kept = [line for i, line in enumerate(lines) if i not in drop]
    new = PRE_FLAG_CUT_RE.sub("", "\n".join(kept))
    new = re.sub(r"[ \t]+\n", "\n", new)
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new


def prerelease_floor(line: str) -> bool:
    """True when this line installs something the stable channel cannot resolve."""
    return bool(INSTALL_RE.search(line) and PRERELEASE_REQ_RE.search(line))


def surviving_mentions(path: Path, text: str) -> list[tuple[Path, int, str]]:
    """Every line of one stable-channel page that still asks for a prerelease.

    Two ways a line asks. It names the flag, which a sentence beside a stripped
    command does when the command has lost it. Or it installs a requirement whose
    floor version is a prerelease, which the flag used to say out loud and the
    floor still says: the stable channel holds nothing that satisfies it.

    An admonition whose title is in ALLOWED_TITLES is exempt, title line and
    body. `strip` keeps such a block, so reporting it would leave the page with
    no honest way to clear: the two blocks on the release-channels page teach
    the flag, which a stable-channel reader needs as much as an alpha one.
    """
    lines = text.split("\n")
    exempt: set[int] = set()
    for start, end, _kind, title in blocks(lines):
        if title in ALLOWED_TITLES:
            exempt.update(range(start, end))
    return [(path, i + 1, line.strip())
            for i, line in enumerate(lines)
            if i not in exempt
            and (PRE_MENTION_RE.search(line) or prerelease_floor(line))]


def cmd_strip(argv: argparse.Namespace) -> int:
    changed = 0
    survivors: list[tuple[Path, int, str]] = []
    for p in pages():
        text = p.read_text()
        new = strip_text(text)
        if new != text:
            changed += 1
            marked = len(text.split("\n")) - len(new.split("\n"))
            flags = len(PRE_FLAG_RE.findall(text))
            print(f"{p}: {marked} line(s) removed, {flags} --pre flag(s)")
            if not argv.dry_run:
                p.write_text(new)
        # Every page, and not the changed ones alone. A page the strip has
        # nothing left to remove can still hold a sentence that asks for the
        # flag, so a run over an already stripped manual must fail the same way
        # the first run did.
        survivors.extend(surviving_mentions(p, new))
    print(f"alpha-only strip: {changed} page(s)" + (" (dry run)" if argv.dry_run else ""))
    if survivors:
        print()
        print("the flag is gone from the commands and these lines still ask for a "
              "prerelease, by naming the flag or by pinning a prerelease floor:")
        for p, ln, line in survivors:
            print(f"  {p}:{ln}: {line}")
        print(f"alpha-only strip: {len(survivors)} surviving prerelease "
              f"reference(s) on {len({p for p, _l, _t in survivors})} page(s). "
              "Rewrite the prose, or mark it with the canonical admonition so the "
              "strip removes it too.")
        return 1
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
