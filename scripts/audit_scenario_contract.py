"""Scenario contract audit — flag players.py that bypass framework guarantees.

The `decide → act → on_fill` contract in ``masim/agents/_base.py`` gives
scenario code three guarantees that only hold if variants **never**
override ``act()`` or ``decide()`` on the canonical bases
(``CanonicalRulePlayer``, ``CanonicalLLMPlayer``,
``CanonicalRagPlayer``, ``CanonicalMarketCoordinator``):

1. Wire-format keys (``action``, ``quantity``, ``bid_price``) are
   present and typed correctly.
2. ``bid_price > 0`` on BUY/SELL — enforced by
   ``masim.format.finalize.require_positive_bid_price``. No silent
   substitution of ``market_data["price"]``.
3. Cash and position mutation happens exactly once, atomically.
4. Post-fill anchor updates go through ``on_fill(action, quantity,
   bid_price)`` — never through a shadow ``act()``.

This script walks every ``examples/*/{Rule,LLM,RuleLLM,Rag}/players.py``
file and reports:

* **STRUCT-ACT**    — class inheriting a canonical base overrides
                       ``act`` (or ``async def act``).
* **STRUCT-DECIDE** — class inheriting a canonical base overrides
                       ``decide`` (or ``async def decide``).
* **SEM-SILENT-FILL** — file textually contains a silent-fill pattern
                        that assigns / substitutes a fallback bid_price
                        from ``market_data``, ``state.price``, ``price``
                        etc. Note: the defensive divide-by-zero form
                        (``cash / bid_price if bid_price > 0 else 0``)
                        is explicitly filtered out — that guards
                        arithmetic, not the wire value.
* **SEM-CASH-MUT**  — file textually mutates ``self.state.custom_state
                       ["cash"]`` outside an ``__init__`` /
                       ``init_extras`` / ``on_fill`` block, indicating
                       likely double-mutation that shadows the base's
                       ``_apply_fill_and_emit_action``.
* **LEGACY-BASE**   — file uses ``GeneralPlayer`` (pre-canonical
                       framework); we only note this without flagging
                       overrides, since these scenarios pre-date the
                       contract. Silent-fill and cash-mutation checks
                       still run.

Usage::

    # Text report, exit 0 on clean, exit 1 on findings.
    PYTHONPATH=. python3 scripts/audit_scenario_contract.py

    # Machine-readable JSON.
    PYTHONPATH=. python3 scripts/audit_scenario_contract.py --json

    # Limit to specific scenarios.
    PYTHONPATH=. python3 scripts/audit_scenario_contract.py --scenario AnchoringEffect DispositionEffect

    # Suppress LEGACY-BASE informational rows.
    PYTHONPATH=. python3 scripts/audit_scenario_contract.py --no-legacy-info

Contract reference: ``examples/AnchoringEffect/simulation-bases.md §7.1``.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"

CANONICAL_BASES = {
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
    "CanonicalRagPlayer",
    "CanonicalMarketCoordinator",
}

LEGACY_BASES = {"GeneralPlayer"}

VARIANT_DIRS = {"Rule", "LLM", "RuleLLM", "Rag"}

# ---------------------------------------------------------------------------
# Finding model
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    severity: str  # CRITICAL / HIGH / MEDIUM / INFO
    kind: str  # STRUCT-ACT / STRUCT-DECIDE / SEM-SILENT-FILL / SEM-CASH-MUT / LEGACY-BASE
    path: str  # relative to repo root
    line: int
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "kind": self.kind,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
        }


# ---------------------------------------------------------------------------
# Silent-fill regex patterns (compiled once)
# ---------------------------------------------------------------------------

# Fallback assignment: `bid_price = market_data["price"]` or `.get("price")`
# or `bid_price = self.state.custom_state["market_data"]["price"]` etc.
SILENT_FILL_ASSIGN = re.compile(
    r"""
    (?:^|\W)
    bid_price\s*=\s*
    (?!                                # NOT a legit float / int literal
        [-+]?\d
    )
    (?:                                # ... but IS a fallback source:
        market_data
      | market_state
      | state\.price
      | state\.custom_state
      | self\.state
      | mkt
      | md
      | price
    )
    """,
    re.VERBOSE,
)

# Ternary silent-fill: `... if bid_price > 0 else market_data["price"]`
# (Defensive `... else 0` is fine — filtered by requiring a source name after
# the else, not a numeric literal.)
SILENT_FILL_TERNARY = re.compile(
    r"""
    bid_price\s*>\s*0\s*else\s*
    (?!
        [-+]?\d                        # else 0  → defensive guard, skip
      | None\b
      | hold\b
    )
    (?:
        market_data
      | market_state
      | state\.price
      | state\.custom_state
      | self\.state
      | mkt
      | md
      | \bprice\b
    )
    """,
    re.VERBOSE,
)

# `if not bid_price: bid_price = <fallback>` two-line pattern
SILENT_FILL_IFNOT = re.compile(
    r"if\s+not\s+bid_price[^\n]*\n[ \t]*bid_price\s*=\s*(?!"
    r"[-+]?\d|None\b)"
    r"(?:market_data|market_state|state\.price|state\.custom_state|self\.state|mkt|md|price)"
)

# Cash mutation on custom_state — flag any of these:
#   self.state.custom_state["cash"] -= ...
#   self.state.custom_state["cash"] +=
#   self.state.custom_state["cash"] = ...
# We DO allow init sites (guarded by AST-level context check below).
CASH_MUT = re.compile(
    r"""self\.state\.custom_state\[\s*['"]cash['"]\s*\]\s*[-+]?="""
)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _base_names(cls: ast.ClassDef) -> List[str]:
    names: List[str] = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            # e.g. masim.agents._base.CanonicalRulePlayer  -> Attribute chain
            names.append(base.attr)
    return names


def _defs_named(node: ast.AST, name: str) -> List[ast.FunctionDef | ast.AsyncFunctionDef]:
    out: List[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == name:
            out.append(child)
    return out


def _enclosing_function(tree: ast.Module, target_line: int) -> Optional[str]:
    """Return the name of the deepest FunctionDef whose body contains
    ``target_line``, or ``None`` if no function contains it (module scope)."""
    hit: List[Tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", None) or start
            if start <= target_line <= end:
                # depth ≈ line-span (smaller span means more deeply nested)
                hit.append((end - start, node.name))
    if not hit:
        return None
    hit.sort()
    return hit[0][1]


# ---------------------------------------------------------------------------
# Per-file audit
# ---------------------------------------------------------------------------


def _classify_bases(bases: Iterable[str]) -> str:
    bset = set(bases)
    if bset & CANONICAL_BASES:
        return "canonical"
    if bset & LEGACY_BASES:
        return "legacy"
    return "unknown"


def audit_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        findings.append(
            Finding(
                "HIGH",
                "READ-ERROR",
                str(path.relative_to(REPO_ROOT)),
                0,
                f"cannot read: {type(e).__name__}: {e}",
            )
        )
        return findings

    rel = str(path.relative_to(REPO_ROOT))

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as e:
        findings.append(
            Finding(
                "HIGH",
                "PARSE-ERROR",
                rel,
                e.lineno or 0,
                f"SyntaxError: {e.msg}",
            )
        )
        return findings

    # -- Track base-class classification per class ------------------------
    file_uses_canonical = False
    file_uses_legacy = False

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node)
        kind = _classify_bases(bases)
        if kind == "canonical":
            file_uses_canonical = True
        elif kind == "legacy":
            file_uses_legacy = True

        # STRUCT-ACT / STRUCT-DECIDE only apply to canonical subclasses.
        if kind != "canonical":
            continue

        for method_name, tag, note in (
            (
                "act",
                "STRUCT-ACT",
                "overrides framework act(); bypasses wire-format validation "
                "(require_positive_bid_price) and atomic cash/position mutation "
                "in _apply_fill_and_emit_action. Move post-fill logic to on_fill().",
            ),
            (
                "decide",
                "STRUCT-DECIDE",
                "overrides framework decide() wiring; scenarios should return "
                "an InvestorOrder from decide_order() (Rule) or a parsed schema "
                "from LLM response — never emit a raw payload dict with silent "
                "fallback bid_price.",
            ),
        ):
            for defn in _defs_named(node, method_name):
                # A method defined *directly on this class body* is the
                # override. (_defs_named walks the class node so any nested
                # function with this name would also match; those are rare
                # in scenario code and worth flagging anyway.)
                findings.append(
                    Finding(
                        severity="CRITICAL",
                        kind=tag,
                        path=rel,
                        line=defn.lineno,
                        detail=f"class {node.name}({', '.join(bases)}).{method_name} — {note}",
                    )
                )

    if file_uses_legacy and not file_uses_canonical:
        # Informational only — legacy scenarios pre-date the contract.
        findings.append(
            Finding(
                severity="INFO",
                kind="LEGACY-BASE",
                path=rel,
                line=1,
                detail="file uses GeneralPlayer; predates canonical framework contract",
            )
        )

    # -- Silent-fill regex sweep (line-oriented, so we can report line #) --
    lines = text.splitlines()

    def _find_matches(regex: re.Pattern[str]) -> List[int]:
        hits: List[int] = []
        for idx, line in enumerate(lines, start=1):
            if regex.search(line):
                hits.append(idx)
        return hits

    # Multiline SILENT_FILL_IFNOT — scan whole text for span, then map to line.
    for m in SILENT_FILL_IFNOT.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                severity="HIGH",
                kind="SEM-SILENT-FILL",
                path=rel,
                line=line_no,
                detail=f"two-line silent-fill pattern (if not bid_price / bid_price = <market_data|price|…>): {lines[line_no-1].strip()!r}",
            )
        )

    for line_no in _find_matches(SILENT_FILL_ASSIGN):
        # Skip lines that also contain a numeric literal after `=` on the same
        # line (i.e. `bid_price = 100.0` is fine).
        snippet = lines[line_no - 1].strip()
        if re.search(r"bid_price\s*=\s*[-+]?[0-9.]+\s*$", snippet):
            continue
        findings.append(
            Finding(
                severity="HIGH",
                kind="SEM-SILENT-FILL",
                path=rel,
                line=line_no,
                detail=f"fallback assignment to bid_price from non-literal source: {snippet!r}",
            )
        )

    for line_no in _find_matches(SILENT_FILL_TERNARY):
        snippet = lines[line_no - 1].strip()
        findings.append(
            Finding(
                severity="HIGH",
                kind="SEM-SILENT-FILL",
                path=rel,
                line=line_no,
                detail=f"ternary silent-fill (`bid_price > 0 else <price|market_data|…>`): {snippet!r}",
            )
        )

    # -- Cash mutation outside init/on_fill ---------------------------------
    for line_no in _find_matches(CASH_MUT):
        fn = _enclosing_function(tree, line_no)
        # Legit sites: __init__, init_extras, on_fill, _initialize_state,
        # _seed_state, seed_cash, and Market.perceive (Market coordinator
        # mutates its own cash bookkeeping).
        ALLOWED = {
            "__init__",
            "init_extras",
            "on_fill",
            "_initialize_state",
            "_seed_state",
            "seed_cash",
        }
        if fn in ALLOWED:
            continue
        # If the enclosing function is a Market coordinator method (e.g.
        # 'perceive', 'decide', 'act' on Market class) we still flag — but
        # scenarios frequently mutate cash inside investor act()/decide()
        # which IS the anti-pattern. We keep a plain HIGH severity and let
        # the user disambiguate; the file/line pointer is precise.
        snippet = lines[line_no - 1].strip()
        findings.append(
            Finding(
                severity="HIGH" if fn in {"act", "decide"} else "MEDIUM",
                kind="SEM-CASH-MUT",
                path=rel,
                line=line_no,
                detail=f"cash mutation inside {fn!r}: {snippet!r} (framework already mutates cash in _apply_fill_and_emit_action)",
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Directory walk
# ---------------------------------------------------------------------------


def iter_players_files(scenario_filter: Optional[List[str]]) -> Iterable[Path]:
    if not EXAMPLES_DIR.is_dir():
        return
    for scenario_dir in sorted(EXAMPLES_DIR.iterdir()):
        if not scenario_dir.is_dir():
            continue
        if scenario_filter and scenario_dir.name not in scenario_filter:
            continue
        for variant_dir in sorted(scenario_dir.iterdir()):
            if not variant_dir.is_dir():
                continue
            if variant_dir.name not in VARIANT_DIRS:
                # Skip _run.py, configs/, docs, __pycache__, etc.
                continue
            candidate = variant_dir / "players.py"
            if candidate.is_file():
                yield candidate


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


def render_text(findings: List[Finding], no_legacy_info: bool) -> Tuple[str, int]:
    filtered = [
        f for f in findings if not (no_legacy_info and f.kind == "LEGACY-BASE")
    ]
    filtered.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.path, f.line))

    by_kind: Counter[str] = Counter(f.kind for f in filtered)
    by_severity: Counter[str] = Counter(f.severity for f in filtered)

    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("SCENARIO CONTRACT AUDIT")
    lines.append(
        f"Contract ref: examples/AnchoringEffect/simulation-bases.md §7.1"
    )
    lines.append("=" * 100)
    lines.append("")
    lines.append("Summary:")
    for kind in ("STRUCT-ACT", "STRUCT-DECIDE", "SEM-SILENT-FILL", "SEM-CASH-MUT", "LEGACY-BASE", "PARSE-ERROR", "READ-ERROR"):
        n = by_kind.get(kind, 0)
        if n:
            lines.append(f"  {kind:<20s} {n}")
    lines.append("")
    lines.append("By severity:")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "INFO"):
        n = by_severity.get(sev, 0)
        if n:
            lines.append(f"  {sev:<10s} {n}")
    lines.append("")

    if not filtered:
        lines.append("[CLEAN] No findings.")
        return "\n".join(lines), 0

    lines.append("-" * 100)
    lines.append("Findings:")
    lines.append("-" * 100)
    cur_path = None
    for f in filtered:
        if f.path != cur_path:
            lines.append("")
            lines.append(f"● {f.path}")
            cur_path = f.path
        lines.append(f"  [{f.severity:<8s}] {f.kind:<16s} L{f.line:<5d} {f.detail}")

    # Exit code = 1 if any CRITICAL/HIGH finding.
    exit_code = 1 if any(
        f.severity in ("CRITICAL", "HIGH") for f in filtered
    ) else 0
    return "\n".join(lines), exit_code


def render_json(findings: List[Finding]) -> Tuple[str, int]:
    payload = {
        "findings": [f.to_dict() for f in findings],
        "counts": {
            "by_kind": dict(Counter(f.kind for f in findings)),
            "by_severity": dict(Counter(f.severity for f in findings)),
            "total": len(findings),
        },
    }
    exit_code = 1 if any(
        f.severity in ("CRITICAL", "HIGH") for f in findings
    ) else 0
    return json.dumps(payload, indent=2, ensure_ascii=False), exit_code


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument(
        "--scenario",
        nargs="*",
        default=None,
        help="Restrict scan to these scenario directory names",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output findings as JSON instead of a text report",
    )
    p.add_argument(
        "--no-legacy-info",
        action="store_true",
        help="Suppress LEGACY-BASE informational rows in text report",
    )
    args = p.parse_args(argv)

    all_findings: List[Finding] = []
    for path in iter_players_files(args.scenario):
        all_findings.extend(audit_file(path))

    if args.json:
        report, code = render_json(all_findings)
    else:
        report, code = render_text(all_findings, args.no_legacy_info)
    print(report)
    return code


if __name__ == "__main__":
    sys.exit(main())
