#!/usr/bin/env python3
"""Import every MASim module and report module-scope import failures.

Why this exists
---------------
``python -m compileall`` only checks *syntax*. A missing name in a runtime
annotation — e.g. ``def f(x: Optional[int])`` in a module that never imported
``Optional`` — compiles cleanly and then raises ``NameError`` the first time
anything imports it. That exact bug shipped into the tree once and was only
caught by manually importing the package.

This script performs the import for real, so module-scope errors (NameError,
ImportError, circular imports, bad decorators) surface in CI.

Usage
-----
    python scripts/check_module_imports.py            # core packages only
    python scripts/check_module_imports.py --all      # + interface/knowledge/
                                                      #   evaluation (needs the
                                                      #   full requirements.txt)

Exit code is 1 when any module fails to import.
"""

from __future__ import annotations

import argparse
import importlib
import pkgutil
import sys
import traceback
from pathlib import Path
from typing import List, Tuple

# Make the script runnable from anywhere (and from CI) without PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Packages whose module-scope imports are covered by requirements-test.txt.
CORE_PREFIXES = (
    "masim.agents",
    "masim.communication",
    "masim.format",
    "masim.persona",
    "masim.platform",
    "masim.player",
    "masim.proxy",
    "masim.simulator",
    "masim.utils",
)

# Packages that additionally need streamlit / llama-index (requirements.txt).
OPTIONAL_PREFIXES = (
    "evaluation",
    "app",
    "masim.knowledge",
)


def discover(include_optional: bool) -> List[str]:
    """Return the module names to import, in deterministic order."""
    import masim

    prefixes = CORE_PREFIXES + (OPTIONAL_PREFIXES if include_optional else ())
    names = []
    for module in pkgutil.walk_packages(masim.__path__, prefix="masim."):
        if module.name.startswith(prefixes):
            names.append(module.name)
    return sorted(set(names))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Also import evaluation / app / masim.knowledge; "
            "requires the full runtime environment (streamlit, llama-index)."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failures and the final summary line.",
    )
    args = parser.parse_args(argv)

    names = discover(args.all)
    failures: List[Tuple[str, str]] = []
    for name in names:
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 - report every failure kind
            failures.append((name, f"{type(exc).__name__}: {exc}"))
            if not args.quiet:
                print(f"FAIL {name}")
                traceback.print_exc()

    print(
        f"imported {len(names) - len(failures)}/{len(names)} module(s)"
        f"{' (core + optional)' if args.all else ' (core)'}"
    )
    if failures:
        print("module-scope import failures:")
        for name, err in failures:
            print(f"  {name}: {err}")
        return 1
    print("OK — no module-scope import failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
