#!/usr/bin/env python3
"""Comprehensive audit of agent identity naming, cross-variant parity,
agent_pool .md coverage, and icon PNG coverage.

Read-only. Prints a structured report. Exit code non-zero if issues found.

Invocation modes (backing the Contract Polish Hooks in
`masim/skills/implement-simulation-skill/06-step2-agent-design.md`,
`.../07-step3-config.md`, and `.../09-step5-to-10-review.md`):

    # Repo-wide sweep (Closeout hook in 09-step5-to-10-review.md)
    python scripts/audit_agent_naming.py

    # Scenario-scoped invocation (Step 2 Hook 6 + Step 3 Hooks 5–6–7)
    python scripts/audit_agent_naming.py --scenario AnchoringEffect

    # Restrict to a single check family
    python scripts/audit_agent_naming.py --check identity   # Step 3 Hooks 5–6
    python scripts/audit_agent_naming.py --check topology   # Step 3 Hook 7
    python scripts/audit_agent_naming.py --check parity     # Step 2 Hook 6
    python scripts/audit_agent_naming.py --check coverage   # .md + icon coverage
    python scripts/audit_agent_naming.py --check orphans    # Closeout orphans

Exit code = number of check-family buckets that failed (0 = green).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
FINANCE_MD = ROOT / "examples" / "AGENT_POOL" / "finance"
ICONS = ROOT / "examples" / "AGENT_POOL" / "agent_images" / "icons"

VARIANTS = ("Rule", "LLM", "RuleLLM", "Rag")
VARIANT_PREFIX = {
    "Rule": "rule_",
    "LLM": "llm_",
    "RuleLLM": "rulellm_",
    "Rag": "ragllm_",
}
SKIP_SCENARIOS = {"CUSTOMIZED_SIMULATION", "Demo", "TEMPLATES", "MYTest"}
RESERVED_KEYS = {"market", "knowledge"}

# Matches an identity block whose key/identity is a snake_case token.
# Numeric suffix like `_1`, `_23` at the very end is a violation (double-suffix bug).
NUMERIC_SUFFIX_RE = re.compile(r"_\d+$")

# Anchored identity block in players.yml: `identity_key:` at column 0
PLAYERS_KEY_RE = re.compile(r"^([a-z][a-z0-9_]*)\s*:\s*$", re.MULTILINE)
# Fallback: any top-level snake_case key followed by nested `class:` line
BLOCK_RE = re.compile(
    r"^([a-z][a-z0-9_]*)\s*:\s*\n(?:[^\n]*\n){0,8}?\s+class\s*:\s*[\"']?[^\n\"']+[\"']?",
    re.MULTILINE,
)


def load_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def extract_players_identities(path: Path) -> list[str]:
    """Extract top-level identity keys from a players.yml file.

    We use BLOCK_RE which requires a nested `class:` line, guaranteeing the
    key is a player identity and not a stray field.
    """
    text = load_text(path)
    ids = []
    for m in BLOCK_RE.finditer(text):
        key = m.group(1)
        if key in RESERVED_KEYS:
            continue
        ids.append(key)
    return ids


def extract_topology_identities(path: Path) -> set[str]:
    """Extract identities referenced in topology.yml (best-effort)."""
    text = load_text(path)
    ids: set[str] = set()
    # `key:` at line start or nested lists `- key:` or `- key`
    for m in re.finditer(r"(?m)^\s*-?\s*([a-z][a-z0-9_]*)\s*:", text):
        tok = m.group(1)
        if tok in RESERVED_KEYS:
            continue
        # Heuristic: only include tokens that look like variant-prefixed identities.
        if any(tok.startswith(p) for p in VARIANT_PREFIX.values()):
            ids.add(tok)
    return ids


def to_kebab(snake: str) -> str:
    return snake.replace("_", "-")


def canonical_archetype(identity: str) -> str:
    for p in VARIANT_PREFIX.values():
        if identity.startswith(p):
            return identity[len(p):]
    return identity


CHECK_FAMILIES = ("identity", "topology", "parity", "coverage", "orphans", "all")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit agent identity naming, cross-variant parity, agent_pool .md "
            "coverage, and icon PNG coverage. Backs the Contract Polish Hooks in "
            "implement-simulation-skill/{06,07,09}-*.md."
        )
    )
    parser.add_argument(
        "--scenario",
        default=None,
        help=(
            "Restrict the audit to one scenario folder under configs/. "
            "When omitted, sweeps every non-scratch scenario (Closeout mode)."
        ),
    )
    parser.add_argument(
        "--check",
        default="all",
        choices=CHECK_FAMILIES,
        help=(
            "Restrict the report and exit-code contribution to one check family. "
            "'orphans' is only meaningful in repo-wide mode (no --scenario)."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    all_scenarios = sorted(
        d.name for d in CONFIGS.iterdir()
        if d.is_dir() and d.name not in SKIP_SCENARIOS
    )
    if args.scenario:
        if args.scenario not in all_scenarios:
            print(
                f"ERROR: scenario '{args.scenario}' not found under configs/ "
                f"(or is in SKIP_SCENARIOS). Available: {', '.join(all_scenarios)}",
                file=sys.stderr,
            )
            return 2
        scenarios = [args.scenario]
        scoped = True
    else:
        scenarios = all_scenarios
        scoped = False

    check = args.check
    want = {c: (check in ("all", c)) for c in CHECK_FAMILIES if c != "all"}
    if scoped and want["orphans"] and check == "orphans":
        print(
            "WARNING: 'orphans' check is a repo-wide invariant; "
            "scenario-scoped orphan reports are meaningless. Ignoring --check.",
            file=sys.stderr,
        )
        want["orphans"] = False

    # Collect per-scenario, per-variant identities.
    # data[scenario][variant] = set(identities)
    data: dict[str, dict[str, set[str]]] = {}
    top_data: dict[str, dict[str, set[str]]] = {}
    # Issues buckets
    non_prefixed: list[tuple[str, str, str, str]] = []      # scenario, variant, file, ident
    numeric_suffix: list[tuple[str, str, str, str]] = []
    reserved_hit: list[tuple[str, str, str, str]] = []
    files_missing: list[tuple[str, str]] = []
    top_orphans: list[tuple[str, str, str]] = []            # scenario, variant, ident (in topology but not players)

    for scen in scenarios:
        data[scen] = {}
        top_data[scen] = {}
        for variant in VARIANTS:
            vdir = CONFIGS / scen / variant
            if not vdir.is_dir():
                data[scen][variant] = set()
                top_data[scen][variant] = set()
                continue
            players = vdir / "players.yml"
            topology = vdir / "topology.yml"
            if not players.is_file():
                files_missing.append((f"{scen}/{variant}", "players.yml"))
                data[scen][variant] = set()
                top_data[scen][variant] = set()
                continue
            if not topology.is_file():
                files_missing.append((f"{scen}/{variant}", "topology.yml"))

            ids = extract_players_identities(players)
            id_set: set[str] = set()
            for ident in ids:
                id_set.add(ident)
                expected_prefix = VARIANT_PREFIX[variant]
                if not ident.startswith(expected_prefix):
                    non_prefixed.append((scen, variant, "players.yml", ident))
                if NUMERIC_SUFFIX_RE.search(ident):
                    numeric_suffix.append((scen, variant, "players.yml", ident))
            data[scen][variant] = id_set

            top_ids = extract_topology_identities(topology) if topology.is_file() else set()
            for tid in top_ids:
                expected_prefix = VARIANT_PREFIX[variant]
                if not tid.startswith(expected_prefix):
                    non_prefixed.append((scen, variant, "topology.yml", tid))
                if NUMERIC_SUFFIX_RE.search(tid):
                    numeric_suffix.append((scen, variant, "topology.yml", tid))
                if tid not in id_set:
                    top_orphans.append((scen, variant, tid))
            top_data[scen][variant] = top_ids

    # Cross-variant parity: for each scenario, compare stripped archetypes across variants.
    parity_issues: list[tuple[str, str, dict[str, list[str]]]] = []
    for scen in scenarios:
        arch_by_variant: dict[str, set[str]] = {}
        for variant in VARIANTS:
            idents = data[scen][variant]
            if not idents:
                continue
            arch_by_variant[variant] = {canonical_archetype(i) for i in idents}
        if len(arch_by_variant) < 2:
            continue
        # Union of all archetypes, then compare
        all_arch = set().union(*arch_by_variant.values())
        for arch in all_arch:
            missing_in = [v for v in arch_by_variant if arch not in arch_by_variant[v]]
            if missing_in:
                parity_issues.append((scen, arch, {v: sorted(arch_by_variant[v]) for v in arch_by_variant}))
                break  # only need first-issue per scenario for report brevity

    # .md coverage
    existing_md = {p.stem for p in FINANCE_MD.glob("*.md")}
    existing_icons = {p.stem[len("finance-"):] for p in ICONS.glob("finance-*.png")}

    # All unique archetypes referenced across the codebase
    all_archetypes: set[str] = set()
    arch_to_scenarios: dict[str, set[str]] = defaultdict(set)
    for scen in scenarios:
        for variant in VARIANTS:
            for ident in data[scen][variant]:
                arch = canonical_archetype(ident)
                all_archetypes.add(arch)
                arch_to_scenarios[arch].add(scen)

    missing_md: list[str] = []
    missing_icons: list[str] = []
    for arch in sorted(all_archetypes):
        kebab = to_kebab(arch)
        if kebab not in existing_md:
            missing_md.append(arch)
        if kebab not in existing_icons:
            missing_icons.append(arch)

    # ==================== REPORT ====================
    print("=" * 78)
    print("AGENT NAMING & AGENT_POOL AUDIT")
    print("=" * 78)
    print(f"Scenarios scanned : {len(scenarios)}")
    print(f"Variants          : {', '.join(VARIANTS)}")
    print(f"Unique archetypes : {len(all_archetypes)}")
    print(f"Existing .md      : {len(existing_md)}")
    print(f"Existing icons    : {len(existing_icons)}")
    print()

    def _dump(header: str, rows: list) -> None:
        print(f"[{header}] count = {len(rows)}")
        for r in rows[:40]:
            print("   ", r)
        if len(rows) > 40:
            print(f"    ... and {len(rows) - 40} more")
        print()

    _dump("MISSING FILES", files_missing)
    if want["identity"]:
        _dump("NON-PREFIXED IDENTITIES", non_prefixed)
        _dump("NUMERIC-SUFFIX IDENTITIES", numeric_suffix)
    if want["topology"]:
        _dump("TOPOLOGY IDENTITIES NOT IN PLAYERS", top_orphans)

    if want["parity"]:
        print(f"[CROSS-VARIANT PARITY ISSUES] scenarios with mismatch = {len(parity_issues)}")
        for scen, arch, details in parity_issues[:20]:
            variants_have = sorted(v for v, arches in details.items() if arch in arches)
            variants_miss = sorted(v for v, arches in details.items() if arch not in arches)
            print(f"    {scen}: archetype '{arch}' present in {variants_have}, MISSING in {variants_miss}")
        if len(parity_issues) > 20:
            print(f"    ... and {len(parity_issues) - 20} more scenarios")
        print()

    if want["coverage"]:
        print(f"[MISSING .md FILES] count = {len(missing_md)}")
        for a in missing_md[:60]:
            print(f"    {to_kebab(a)}.md   (used in: {', '.join(sorted(arch_to_scenarios[a])[:5])}"
                  + (f", +{len(arch_to_scenarios[a]) - 5} more" if len(arch_to_scenarios[a]) > 5 else "") + ")")
        if len(missing_md) > 60:
            print(f"    ... and {len(missing_md) - 60} more")
        print()

        print(f"[MISSING icons] count = {len(missing_icons)}")
        for a in missing_icons[:60]:
            print(f"    finance-{to_kebab(a)}.png   (used in: {', '.join(sorted(arch_to_scenarios[a])[:3])}"
                  + (f", +{len(arch_to_scenarios[a]) - 3} more" if len(arch_to_scenarios[a]) > 3 else "") + ")")
        if len(missing_icons) > 60:
            print(f"    ... and {len(missing_icons) - 60} more")
        print()

    # Orphan detection is only meaningful in repo-wide mode.
    orphan_md: list[str] = []
    orphan_icons: list[str] = []
    if not scoped and want["orphans"]:
        orphan_md = sorted(set(existing_md) - {to_kebab(a) for a in all_archetypes})
        orphan_icons = sorted(set(existing_icons) - {to_kebab(a) for a in all_archetypes})
        print(f"[ORPHAN .md FILES] count = {len(orphan_md)}  (present but unused)")
        for a in orphan_md[:30]:
            print(f"    {a}.md")
        if len(orphan_md) > 30:
            print(f"    ... and {len(orphan_md) - 30} more")
        print()
        print(f"[ORPHAN icons] count = {len(orphan_icons)}  (present but unused)")
        for a in orphan_icons[:30]:
            print(f"    finance-{a}.png")
        if len(orphan_icons) > 30:
            print(f"    ... and {len(orphan_icons) - 30} more")
        print()

    # Exit-code accounting: only count buckets in the selected check family.
    counted = len(files_missing)
    if want["identity"]:
        counted += len(non_prefixed) + len(numeric_suffix)
    if want["topology"]:
        counted += len(top_orphans)
    if want["parity"]:
        counted += len(parity_issues)
    if want["coverage"]:
        counted += len(missing_md) + len(missing_icons)
    if not scoped and want["orphans"]:
        counted += len(orphan_md) + len(orphan_icons)

    print("=" * 78)
    print(
        f"TOTAL ISSUES (scope={'repo-wide' if not scoped else args.scenario}, "
        f"check={check}): {counted}"
    )
    print("=" * 78)
    return 0 if counted == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
