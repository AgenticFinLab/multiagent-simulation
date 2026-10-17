#!/usr/bin/env python3
"""Verify that files locating the project root actually land on it.

Why this gate exists
--------------------
Moving a package up or down one directory level silently breaks every
derivation of the project root inside it: the code still imports, the tests
still pass (they rarely touch those constants), and the failure only surfaces
when someone opens the UI and every document lookup misses.

That is exactly what happened when ``masim/interface/`` became ``app/``: eleven
``parents[3]`` / ``parent.parent.parent`` expressions then pointed at the
*parent of the repository*, and one had already been corrected twice.

What it checks (static, no imports)
-----------------------------------
Two shapes are resolved and compared against the repository root:

1. **inline** --- a derivation joined immediately onto a top-level directory,
   including the parenthesised multi-line form;
2. **via a variable** --- ``ROOT = Path(__file__)...parents[N]`` followed by
   ``ROOT / "<top-level>"`` anywhere in the same file.

Only joins onto a known top-level directory are checked, so a ``.parent`` used
for something unrelated (a log directory, a sibling artefact) is left alone.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Dict, Iterator, List, Tuple

# Names that only exist at the repository root.
TOP_LEVEL = (
    "masim",
    "agent_library",
    "app",
    "evaluation",
    "examples",
    "configs",
    "scripts",
    "tests",
    "docs",
    "deploy",
    "setup.py",
    "requirements.txt",
)

_DERIVATION = (
    r"Path\(\s*__file__\s*\)"
    r"(?:\.resolve\(\))?"
    r"((?:\.parents\[\s*\d+\s*\])|(?:\.parent)+)"
)

# 1) inline join, possibly split across lines inside parentheses
_INLINE = re.compile(_DERIVATION + r"\s*/\s*[\"']([A-Za-z_][\w.]*)[\"']", re.S)

# 2) NAME = Path(__file__)...parents[N]  (may span lines)
_ASSIGN = re.compile(
    r"(?m)^[ \t]*([A-Za-z_][\w]*)[ \t]*(?::[^=\n]+)?=[ \t\r\n]*"
    + _DERIVATION
    + r"[ \t\r\n]*(?:#[^\n]*)?$",
    re.S,
)


def resolve(file: pathlib.Path, suffix: str) -> pathlib.Path | None:
    """Apply a ``.parents[N]`` / ``.parent`` chain to ``file``."""
    if suffix.startswith(".parents"):
        match = re.search(r"\d+", suffix)
        return file.parents[int(match.group())] if match else None
    count = suffix.count(".parent")
    if count == 0:
        return None
    return file.parents[count - 1]


def scan(path: pathlib.Path) -> Iterator[Tuple[str, str, pathlib.Path]]:
    """Yield ``(where, joined_name, resolved_dir)`` for each checkable join."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    if "__file__" not in text:
        return
    absolute = path.resolve()

    for match in _INLINE.finditer(text):
        joined = match.group(2)
        if joined in TOP_LEVEL:
            directory = resolve(absolute, match.group(1))
            if directory is not None:
                line = text[: match.start()].count("\n") + 1
                yield f"{path}:{line}", joined, directory

    roots: Dict[str, pathlib.Path] = {}
    for match in _ASSIGN.finditer(text):
        directory = resolve(absolute, match.group(2))
        if directory is not None:
            roots[match.group(1)] = directory
    for name, directory in roots.items():
        joins = re.compile(
            rf"\b{re.escape(name)}\b[^\n]*?/\s*[\"']([A-Za-z_][\w.]*)[\"']"
        )
        for match in joins.finditer(text):
            joined = match.group(1)
            if joined in TOP_LEVEL:
                yield f"{path} ({name})", joined, directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roots",
        nargs="*",
        default=["masim", "agent_library", "app", "evaluation", "scripts", "tests"],
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    repo = pathlib.Path(".").resolve()
    problems: List[Tuple[str, str, pathlib.Path]] = []
    checked = 0

    for name in args.roots:
        root = pathlib.Path(name)
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for where, joined, directory in scan(path):
                checked += 1
                if directory != repo:
                    problems.append((where, joined, directory))

    if problems:
        print(f"FAIL — {len(problems)} project-root derivation(s) point elsewhere:")
        for where, joined, directory in problems:
            print(f"  {where}  joins {joined!r} but resolves to {directory}")
        print(f"  expected the repository root: {repo}")
        return 1

    if not args.quiet:
        print(f"OK — {checked} project-root derivation(s) resolve to the repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
