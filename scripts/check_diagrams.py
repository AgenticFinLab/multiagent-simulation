#!/usr/bin/env python3
"""Lint hand-authored SVG diagrams for the two defects that matter most.

1. **Overlapping text** — two `<text>` elements whose estimated bounding boxes
   intersect. This is the single most common way a diagram silently becomes
   unreadable, and it is invisible in the SVG source.
2. **Text outside the canvas** — a label whose estimated box starts before 0 or
   ends past the viewBox width.

Why the estimate: the SVG has no text metrics, and rasterising to find out is
slow and needs a renderer. Character-count estimates (CJK/fullwidth 1.0 em,
Latin 0.55 em) are accurate enough to catch real collisions; treat the reported
overlap ratio as a signal to look at the file, not as ground truth.

Usage:
    python scripts/check_diagrams.py docs/design/diagrams
    python scripts/check_diagrams.py docs/design/diagrams --min-overlap 0.05

Exit code 1 when any defect is found.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, NamedTuple, Tuple

SVG_NS = "{http://www.w3.org/2000/svg}"


class Box(NamedTuple):
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    size: float


def _char_width(ch: str, size: float) -> float:
    """Estimated advance width of one character in user units."""
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return size * 1.0
    if ch in "iljI.,:;'|!":
        return size * 0.28
    if ch in "mwMW":
        return size * 0.85
    return size * 0.55


def _text_box(el: ET.Element) -> Box | None:
    content = "".join(el.itertext())
    if not content.strip():
        return None
    try:
        x = float(el.get("x", "0"))
        y = float(el.get("y", "0"))
        size = float(el.get("font-size", "12"))
    except ValueError:
        return None

    width = sum(_char_width(ch, size) for ch in content)
    anchor = el.get("text-anchor", "start")
    if anchor == "middle":
        x0 = x - width / 2
    elif anchor == "end":
        x0 = x - width
    else:
        x0 = x
    # Ascender/descender approximation for the em box actually occupied.
    return Box(content, x0, y - size * 0.80, x0 + width, y + size * 0.25, size)


def _overlap(a: Box, b: Box) -> float:
    """Intersection area divided by the smaller box's area."""
    ix = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    iy = max(0.0, min(a.y1, b.y1) - max(a.y0, b.y0))
    inter = ix * iy
    if inter <= 0:
        return 0.0
    smaller = min((a.x1 - a.x0) * (a.y1 - a.y0), (b.x1 - b.x0) * (b.y1 - b.y0))
    return inter / smaller if smaller > 0 else 0.0


def check_svg(path: Path, min_overlap: float) -> List[str]:
    problems: List[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]

    try:
        vb = [float(v) for v in root.get("viewBox", "").split()]
    except ValueError:
        vb = []
    canvas_w = vb[2] if len(vb) == 4 else float(root.get("width", "0") or 0)

    boxes = [b for b in (_text_box(el) for el in root.iter(f"{SVG_NS}text")) if b]

    for index, box in enumerate(boxes):
        for other in boxes[index + 1:]:
            ratio = _overlap(box, other)
            if ratio >= min_overlap:
                problems.append(
                    f"overlapping text ({ratio:.0%} of the smaller box): "
                    f"{box.text[:42]!r} <-> {other.text[:42]!r}"
                )

    if canvas_w:
        for box in boxes:
            if box.x0 < -1:
                problems.append(f"text starts left of the canvas: {box.text[:50]!r}")
            if box.x1 > canvas_w + 1:
                problems.append(
                    f"text past the right edge ({box.x1:.0f} > {canvas_w:.0f}): "
                    f"{box.text[:50]!r}"
                )
    return problems


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("directory", nargs="?", default="docs/design/diagrams")
    parser.add_argument(
        "--min-overlap",
        type=float,
        default=0.12,
        help="Report when the intersection covers this fraction of the smaller text box",
    )
    args = parser.parse_args(argv)

    root = Path(args.directory)
    files = sorted(root.rglob("*.svg"))
    if not files:
        print(f"no .svg files under {root}")
        return 1

    failed = 0
    for path in files:
        problems = check_svg(path, args.min_overlap)
        status = "FAIL" if problems else "ok  "
        print(f"[{status}] {path}")
        for problem in problems[:12]:
            print(f"        - {problem}")
        if len(problems) > 12:
            print(f"        ... and {len(problems) - 12} more")
        if problems:
            failed += 1

    print(f"\n{len(files) - failed}/{len(files)} diagram(s) clean")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
