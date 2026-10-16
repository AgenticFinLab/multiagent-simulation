#!/usr/bin/env python3
"""Verify that internal re-exports actually exist.

Why this gate exists
--------------------
Scenarios deliberately share analysis code: ``examples/{X}/Rag/analysis.py`` and
``.../RuleLLM/analysis.py`` import helpers from ``.../Rule/analysis.py``, and the
Rule module in turn re-exports pieces of the evaluation library. Nothing checks
those names, so a rename on one side silently breaks the other — and because a
broken import is only visible when that module is imported, the damage hides.
That is exactly what happened here: 14 analysis modules failed to import because
they asked a sibling for ``_batch_to_rounds``, a name the sibling never defined.

What it checks
--------------
For every ``from <internal module> import <name>`` inside the scanned roots, the
target module must define ``<name>`` at top level (function, class, plain or
annotated assignment, or an import alias). Modules that define ``__getattr__``
are treated as opaque and skipped, since their surface is not statically knowable.

Exit code 0 when clean, 1 with a report otherwise.
"""

from __future__ import annotations

import argparse
import ast
import collections
import pathlib
import sys
from typing import Dict, Iterable, List, Set, Tuple

# Roots whose modules may import each other by absolute path.
DEFAULT_ROOTS = ("examples", "masim", "scripts")


class ModuleIndex:
    """Statically known top-level names per module."""

    def __init__(self, roots: Iterable[str]) -> None:
        self.roots = tuple(roots)
        self.files: Dict[str, pathlib.Path] = {}
        self.names: Dict[str, Set[str]] = {}
        self.opaque: Set[str] = set()
        self.trees: Dict[str, ast.Module] = {}
        self._build()

    def _module_name(self, path: pathlib.Path) -> str:
        rel = path.with_suffix("").as_posix()
        if rel.endswith("/__init__"):
            rel = rel[: -len("/__init__")]
        return rel.replace("/", ".")

    def _build(self) -> None:
        for root in self.roots:
            base = pathlib.Path(root)
            if not base.exists():
                continue
            for path in sorted(base.rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                module = self._module_name(path)
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8"))
                except SyntaxError:
                    continue
                self.files[module] = path
                self.trees[module] = tree
                self.names[module] = self._top_level_names(tree)

    @staticmethod
    def _top_level_names(tree: ast.Module) -> Set[str]:
        """Names a module exposes at import time.

        Descends into module-level ``try`` / ``if`` blocks (an optional
        dependency guard, or ``if TYPE_CHECKING:``) but never into function or
        class bodies, so a name that only exists locally cannot be mistaken for
        a public re-export.
        """
        names: Set[str] = set()

        def visit(body: List[ast.stmt]) -> None:
            for node in body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.add(node.name)
                    if node.name == "__getattr__":
                        names.add("__opaque__")
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            names.add(target.id)
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    names.add(node.target.id)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        names.add(alias.asname or alias.name.split(".")[0])
                elif isinstance(node, ast.Try):
                    visit(node.body)
                    visit(node.orelse)
                    visit(node.finalbody)
                    for handler in node.handlers:
                        visit(handler.body)
                elif isinstance(node, ast.If):
                    visit(node.body)
                    visit(node.orelse)

        visit(tree.body)
        return names

    def is_opaque(self, module: str) -> bool:
        return "__opaque__" in self.names.get(module, set())

    def is_internal(self, module: str) -> bool:
        return module in self.files


def find_broken_reexports(index: ModuleIndex) -> List[Tuple[str, str, str]]:
    """Return ``(target_module, name, importing_module)`` for each broken name."""
    broken: List[Tuple[str, str, str]] = []
    for module, tree in index.trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level:
                continue
            target = node.module
            if not target or not index.is_internal(target):
                continue
            if index.is_opaque(target):
                continue
            known = index.names[target]
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name not in known:
                    broken.append((target, alias.name, module))
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roots", nargs="*", default=list(DEFAULT_ROOTS))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    index = ModuleIndex(args.roots)
    broken = find_broken_reexports(index)

    grouped: Dict[Tuple[str, str], List[str]] = collections.defaultdict(list)
    for target, name, importer in broken:
        grouped[(target, name)].append(importer)

    if broken:
        print(f"FAIL — {len(grouped)} broken re-export(s):")
        for (target, name), users in sorted(grouped.items()):
            print(f"  {name} is not defined in {target} ({len(users)} importer(s))")
            for user in sorted(users)[:5]:
                print(f"      imported by {user}")
            if len(users) > 5:
                print(f"      … and {len(users) - 5} more")
        return 1

    if not args.quiet:
        print(
            f"OK — {len(index.files)} modules scanned, every internal re-export resolves"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
