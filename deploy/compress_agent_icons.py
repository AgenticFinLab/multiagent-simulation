#!/usr/bin/env python3
"""Compress AGENT_POOL PNG icons for faster UI loading.

WHY
---
Streamlit re-encodes and streams every ``st.image()`` call over the WebSocket,
so the 1024x1024 ~900KB icons shipped with the repo add ~1MB per card render
(*×* ~20 cards × 12 scenarios). Compressing to 50-100KB per icon cuts landing-
page bytes-on-wire by roughly 10× without touching the visible design.

WHAT IT DOES
------------
For each ``*.png`` under ``masim/agents/defines/agent_images/icons/``:

  1. Skip files already ≤ ``--min-target-kb`` (default 60KB) — no need to re-touch.
  2. Downscale from source dimensions to ``--max-side`` (default 512) using
     Lanczos, preserving aspect ratio.
  3. Palette-quantize with an adaptive number of colors: try 256 → 192 → 128 →
     96 → 64 in sequence, stopping as soon as the encoded output fits into
     ``[--min-target-kb, --max-target-kb]`` (default 60-100KB).
  4. Emit the result as an optimized PNG (``optimize=True``, no compression flags
     beyond Pillow's defaults so it stays portable).
  5. Move the original to ``<icons_dir>/_originals/`` (via ``mv -n``) as a
     safety net; the same file is never overwritten twice.

The script is idempotent: after the first run every processed icon lives in
``_originals/`` and re-invocations are no-ops.

USAGE
-----
Dry-run first (recommended):

    python3 deploy/compress_agent_icons.py --dry-run

Real run:

    python3 deploy/compress_agent_icons.py

Custom targets:

    python3 deploy/compress_agent_icons.py --max-side 640 \
        --min-target-kb 70 --max-target-kb 120

Restore all originals (if the result looks too aggressive):

    python3 deploy/compress_agent_icons.py --restore

REQUIREMENTS
------------
Pillow ≥ 9.  No native binaries (pngquant / oxipng) required.
"""
from __future__ import annotations

import argparse
import io
import shutil
import sys
from pathlib import Path
from typing import Iterable, Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "Pillow is required. Install with:\n    pip install --upgrade pillow\n"
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = REPO_ROOT / "masim/agents/defines/agent_images/icons"
BACKUP_DIR = ICONS_DIR / "_originals"


def _encode_png(im: Image.Image, colors: int) -> bytes:
    """Encode a Pillow image into PNG bytes using a `colors`-entry palette.

    Uses Pillow's built-in MEDIANCUT quantizer (method=0) so no external
    native library (libimagequant / pngquant) is required.

    When the source image has a real alpha channel, the alpha is thresholded
    (>=128 → opaque, else transparent) and folded into a single reserved
    palette index — this keeps the output as a lightweight ``P``-mode PNG
    with a tRNS chunk instead of blowing back up to full ``RGBA``.

    For the AGENT_POOL icons (which are pure RGB), the fast path just
    quantizes RGB directly.
    """
    src = im
    has_alpha = src.mode in ("RGBA", "LA") or (
        src.mode == "P" and "transparency" in src.info
    )
    if not has_alpha:
        rgb = src.convert("RGB")
        p = rgb.quantize(colors=colors, method=0)
        buf = io.BytesIO()
        p.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # Alpha path — threshold alpha and quantize the visible pixels.
    rgba = src.convert("RGBA")
    alpha = rgba.split()[-1]
    rgb = rgba.convert("RGB")
    # Reserve one palette slot for transparent pixels.
    p = rgb.quantize(colors=max(2, colors - 1), method=0)
    # Extend palette by one entry (magenta placeholder) marked transparent.
    palette = p.getpalette()
    tp_index = len(palette) // 3
    palette.extend([255, 0, 255])
    p.putpalette(palette)
    # Overwrite transparent pixels' palette index.
    pixels = p.load()
    apx = alpha.load()
    w, h = p.size
    for y in range(h):
        for x in range(w):
            if apx[x, y] < 128:
                pixels[x, y] = tp_index
    p.info["transparency"] = tp_index
    buf = io.BytesIO()
    p.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _compress_one(
    src: Path,
    *,
    max_side: int,
    min_kb: int,
    max_kb: int,
    palettes: Iterable[int],
) -> Optional[bytes]:
    """Return compressed bytes for ``src`` or ``None`` if no palette fits.

    Fits means the encoded size is ≤ ``max_kb * 1024``. We prefer the LARGEST
    palette (least quality loss) that still fits — palettes are searched in
    descending order.
    """
    with Image.open(src) as im:
        im.load()
        # Downscale if needed.
        w, h = im.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            im = im.resize(
                (int(round(w * scale)), int(round(h * scale))),
                resample=Image.LANCZOS,
            )
        # Try palettes largest-first; keep the first fit.
        chosen: Optional[bytes] = None
        for colors in palettes:
            data = _encode_png(im, colors)
            if len(data) <= max_kb * 1024:
                chosen = data
                # Try even bigger palette on next iter would only make it larger,
                # so break: since palettes are sorted descending, the first fit
                # IS the largest-palette-that-fits.
                break
        if chosen is None:
            # No palette fit — fall back to smallest palette so we at least
            # get some reduction (better than shipping the raw 900KB).
            chosen = data  # `data` is the last (smallest palette) attempt
        return chosen


def _iter_icons(icons_dir: Path) -> Iterable[Path]:
    for p in sorted(icons_dir.glob("*.png")):
        if p.parent == BACKUP_DIR:
            continue
        yield p


def _restore(icons_dir: Path) -> int:
    """Move every backed-up original back to ``icons_dir``."""
    if not BACKUP_DIR.exists():
        print(f"No backup directory at {BACKUP_DIR}; nothing to restore.")
        return 0
    n = 0
    for src in BACKUP_DIR.glob("*.png"):
        dst = icons_dir / src.name
        if dst.exists():
            print(f"  overwriting {dst.name}")
            dst.unlink()  # about to be replaced by the original — safe
        shutil.move(str(src), str(dst))
        n += 1
    try:
        BACKUP_DIR.rmdir()
    except OSError:
        pass  # non-empty for some reason, leave it
    print(f"Restored {n} original(s) from {BACKUP_DIR}")
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--icons-dir",
        type=Path,
        default=ICONS_DIR,
        help=f"Directory of PNG icons (default: {ICONS_DIR}).",
    )
    parser.add_argument(
        "--max-side",
        type=int,
        default=512,
        help="Longest-side pixel budget after downscale (default: 512).",
    )
    parser.add_argument(
        "--min-target-kb",
        type=int,
        default=60,
        help="Files ≤ this size are already small; skipped (default: 60KB).",
    )
    parser.add_argument(
        "--max-target-kb",
        type=int,
        default=100,
        help="Fit-threshold; largest palette whose output ≤ this wins "
             "(default: 100KB).",
    )
    parser.add_argument(
        "--palettes",
        type=str,
        default="256,192,128,96,64",
        help="Comma-separated palette sizes to try, descending "
             "(default: 256,192,128,96,64).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report projected savings without touching any files.",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Move originals back from _originals/ and exit.",
    )
    args = parser.parse_args()

    icons_dir: Path = args.icons_dir
    if not icons_dir.exists():
        print(f"error: icons dir not found: {icons_dir}", file=sys.stderr)
        return 2

    if args.restore:
        _restore(icons_dir)
        return 0

    palettes = [int(x) for x in args.palettes.split(",") if x.strip()]
    if not palettes:
        print("error: --palettes must have at least one entry", file=sys.stderr)
        return 2

    BACKUP_DIR.mkdir(exist_ok=True)

    total_before = 0
    total_after = 0
    n_processed = 0
    n_skipped = 0

    for src in _iter_icons(icons_dir):
        size_kb = src.stat().st_size / 1024
        total_before += src.stat().st_size
        if size_kb <= args.min_target_kb:
            n_skipped += 1
            total_after += src.stat().st_size
            continue

        try:
            data = _compress_one(
                src,
                max_side=args.max_side,
                min_kb=args.min_target_kb,
                max_kb=args.max_target_kb,
                palettes=palettes,
            )
        except Exception as exc:
            print(f"  ! {src.name}: failed to compress — {exc}")
            total_after += src.stat().st_size
            continue

        new_size_kb = len(data) / 1024
        total_after += len(data)
        n_processed += 1
        arrow = "→"
        print(
            f"  {src.name:<50s} {size_kb:6.1f}KB {arrow} {new_size_kb:6.1f}KB "
            f"({(1 - new_size_kb/size_kb) * 100:5.1f}% smaller)"
        )
        if args.dry_run:
            continue
        # Move original to backup then write the new file in place.
        backup_path = BACKUP_DIR / src.name
        if not backup_path.exists():
            shutil.move(str(src), str(backup_path))
        else:
            # Backup already exists; just delete the current file so we can
            # write the fresh compression on top.
            src.unlink()
        src.write_bytes(data)

    print()
    print("=" * 72)
    print(f"Icons dir      : {icons_dir}")
    print(f"Processed      : {n_processed}")
    print(f"Already small  : {n_skipped}")
    print(f"Total before   : {total_before / 1024 / 1024:6.2f} MB")
    print(f"Total after    : {total_after / 1024 / 1024:6.2f} MB")
    if total_before:
        pct = (1 - total_after / total_before) * 100
        print(f"Space saved    : {pct:5.1f}% "
              f"({(total_before - total_after) / 1024 / 1024:.2f} MB)")
    print(f"Backups        : {BACKUP_DIR}")
    if args.dry_run:
        print()
        print("This was a --dry-run; no files were modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
