#!/usr/bin/env python3
"""Rename YAML identity keys across all configs to enforce the invariant:

    identity = {variant_prefix}_{archetype_snake_case}

Derivation rule (per identity block):
  1. Read top-level YAML key `ident` and its `class: "...:ClassName"` line.
  2. Skip reserved keys: `market`, `knowledge`.
  3. Strip variant prefix from ClassName (Rule='', LLM='LLM', RuleLLM='RuleLLM',
     Rag='RagLLM').
  4. Snake_case the remainder, merging consecutive uppercase acronyms
     (VolETNManager -> vol_etn_manager, LTCMTrader -> ltcm_trader).
  5. New identity = {rule_|llm_|rulellm_|ragllm_}{snake_case}.

Updates in every touched block:
  - Top-level key `old_ident:` -> `new_ident:`
  - `identity: "old_ident"` -> `identity: "new_ident"`

Updates in the paired topology.yml (same variant folder):
  - Top-level connection keys `old_ident:` -> `new_ident:`
  - List items `  - old_ident` -> `  - new_ident`
  - Header comment lines echoing the name (best-effort word-boundary replace)

Usage:
    python scripts/rename_identities.py --dry-run   # show planned changes
    python scripts/rename_identities.py             # apply
    python scripts/rename_identities.py --scenario SouthSeaBubble  # single scen
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Project root = repo root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"

VARIANTS = ("Rule", "LLM", "RuleLLM", "Rag")
VARIANT_PREFIX: Dict[str, str] = {
    "Rule": "rule_",
    "LLM": "llm_",
    "RuleLLM": "rulellm_",
    "Rag": "ragllm_",
}
CLASS_PREFIX: Dict[str, str] = {
    "Rule": "",
    "LLM": "LLM",
    "RuleLLM": "RuleLLM",
    "Rag": "RagLLM",
}
RESERVED = {"market", "knowledge"}

# Scenarios that were already normalized by hand in the pilot phase.
PILOT_DONE = {"AsianFinancialCrisis", "AnchoringEffect", "DispositionEffect"}
# Non-scenario config dirs to skip entirely.
SKIP_DIRS = {"CUSTOMIZED_SIMULATION", "Demo", "TEMPLATES", "MYTest"}


# ---------------------------------------------------------------------------
# Snake-case with acronym merging.
# ---------------------------------------------------------------------------
def to_snake(camel: str) -> str:
    """Convert CamelCase to snake_case, merging consecutive uppercase acronyms.

    VolETNManager -> vol_etn_manager
    LTCMTrader -> ltcm_trader
    InsiderAdvantaged -> insider_advantaged
    NoiseTrader -> noise_trader
    """
    # Split at boundary between "one-or-more capitals" and "capital-then-lower"
    # so ETNManager -> ETN_Manager
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", camel)
    # Split at boundary between lowercase/digit and capital
    # so InsiderAdvantaged -> Insider_Advantaged
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def strip_trailing_numeric(ident: str) -> str:
    """Strip trailing `_<digits>` suffixes (Volmageddon legacy)."""
    return re.sub(r"(_\d+)+$", "", ident)


# ---------------------------------------------------------------------------
# Identity extraction.
# ---------------------------------------------------------------------------
BLOCK_RE = re.compile(
    r"^([a-z_][a-z_0-9]*):\s*\n(?:[^\n]*\n){0,6}?\s+class:\s*\"[^\"]*:([A-Za-z0-9_]+)\"",
    re.MULTILINE,
)


def build_rename_map(
    text: str, variant: str
) -> Tuple[Dict[str, str], List[str]]:
    """Return (rename_map, warnings) for a players.yml file.

    rename_map: {old_ident: new_ident}, only for identities that actually change
    warnings: human-readable notes about skipped/reserved/edge cases
    """
    rename_map: Dict[str, str] = {}
    warnings: List[str] = []
    for match in BLOCK_RE.finditer(text):
        ident, class_name = match.group(1), match.group(2)
        if ident in RESERVED:
            continue
        cprefix = CLASS_PREFIX[variant]
        if cprefix and class_name.startswith(cprefix):
            archetype_camel = class_name[len(cprefix):]
        else:
            archetype_camel = class_name
        archetype_snake = to_snake(archetype_camel)
        expected = VARIANT_PREFIX[variant] + archetype_snake
        if not archetype_snake:
            warnings.append(f"empty archetype for {ident} (class={class_name})")
            continue
        if ident != expected:
            if ident in rename_map and rename_map[ident] != expected:
                warnings.append(
                    f"duplicate block for {ident} with divergent target"
                )
            rename_map[ident] = expected
    return rename_map, warnings


# ---------------------------------------------------------------------------
# Anchored replacement helpers (avoid substring collisions).
# ---------------------------------------------------------------------------
def apply_rename_players(text: str, rmap: Dict[str, str]) -> str:
    """Apply rename_map to a players.yml text buffer."""
    # Process longest keys first so a shorter key never eats into a longer one.
    # (Not strictly necessary given anchored regex, but adds a safety layer.)
    for old in sorted(rmap.keys(), key=len, reverse=True):
        new = rmap[old]
        # Top-level YAML key
        text = re.sub(
            rf"^{re.escape(old)}:$", f"{new}:", text, flags=re.MULTILINE
        )
        # identity: "old" (double-quoted)
        text = re.sub(
            rf'identity:\s*"{re.escape(old)}"',
            f'identity: "{new}"',
            text,
        )
        # identity: 'old' (single-quoted)
        text = re.sub(
            rf"identity:\s*'{re.escape(old)}'",
            f"identity: '{new}'",
            text,
        )
        # identity: old (unquoted)
        text = re.sub(
            rf"(identity:\s+){re.escape(old)}(\s*(?:#|$))",
            rf"\1{new}\2",
            text,
            flags=re.MULTILINE,
        )
    return text


def apply_rename_topology(text: str, rmap: Dict[str, str]) -> str:
    """Apply rename_map to a topology.yml text buffer."""
    for old in sorted(rmap.keys(), key=len, reverse=True):
        new = rmap[old]
        # Top-level connection key (e.g. "portfolio_insurer:")
        text = re.sub(
            rf"^{re.escape(old)}:$", f"{new}:", text, flags=re.MULTILINE
        )
        # List item ("  - portfolio_insurer") with any indent, tolerating
        # trailing whitespace/comments
        text = re.sub(
            rf"^(\s+-\s+){re.escape(old)}(\s*(?:#[^\n]*)?)$",
            rf"\1{new}\2",
            text,
            flags=re.MULTILINE,
        )
        # Header comment word-boundary occurrence
        # (safe because `old` values are unique-enough tokens)
        text = re.sub(
            rf"\b{re.escape(old)}\b",
            new,
            text,
        )
    return text


# ---------------------------------------------------------------------------
# Special pass: Volmageddon numeric-suffix stripping.
# ---------------------------------------------------------------------------
def volmageddon_prepass(rename_map: Dict[str, str], text: str, variant: str) -> Dict[str, str]:
    """Add renames for identities whose top-level key has a numeric suffix.

    e.g. `short_vol_trader_1:` (class=ShortVolTrader, num_instances=2) is a legacy
    artifact; the runtime auto-appends indices. Rename to `{variant}_short_vol_trader`.
    Only invoked for Volmageddon (or any scenario with the trailing-digit pattern).
    """
    # We already added block-level renames via build_rename_map. But those match
    # against BLOCK_RE which extracts the identity as-is. For Volmageddon the
    # identity string retains the `_1`, `_5` suffix and the derivation uses the
    # class name (which has no suffix). So build_rename_map already computes
    # e.g. short_vol_trader_1 -> rule_short_vol_trader. Nothing extra needed.
    # This function is a placeholder for future edge cases.
    return rename_map


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------
def list_target_scenarios(only: str | None) -> List[str]:
    scenarios = sorted(d.name for d in CONFIGS.iterdir() if d.is_dir())
    result = []
    for s in scenarios:
        if s in PILOT_DONE or s in SKIP_DIRS:
            continue
        if only and s != only:
            continue
        result.append(s)
    return result


def process_scenario(
    scenario: str, dry_run: bool, verbose: bool
) -> Tuple[int, int, List[str]]:
    """Return (total_renames, files_changed, warnings) for one scenario."""
    total = 0
    files_changed = 0
    warnings: List[str] = []
    for variant in VARIANTS:
        players_path = CONFIGS / scenario / variant / "players.yml"
        topology_path = CONFIGS / scenario / variant / "topology.yml"
        if not players_path.exists():
            continue
        text = players_path.read_text(encoding="utf-8")
        rmap, warns = build_rename_map(text, variant)
        warnings.extend(f"[{scenario}/{variant}] {w}" for w in warns)
        if not rmap:
            continue
        # Collision check
        for old, new in rmap.items():
            # If new key already exists as a distinct block and is not itself
            # scheduled to be renamed away, fail loudly.
            if new == old:
                continue
            if re.search(rf"^{re.escape(new)}:$", text, flags=re.MULTILINE) \
                    and new not in rmap:
                warnings.append(
                    f"[{scenario}/{variant}] COLLISION: target {new} already "
                    f"exists (source: {old})"
                )
        # Show renames
        if verbose:
            for old, new in sorted(rmap.items()):
                print(f"  [{scenario}/{variant}] {old} -> {new}")
        total += len(rmap)
        # Apply players
        new_players = apply_rename_players(text, rmap)
        if new_players != text:
            files_changed += 1
            if not dry_run:
                players_path.write_text(new_players, encoding="utf-8")
        # Apply topology (if present)
        if topology_path.exists():
            topo_text = topology_path.read_text(encoding="utf-8")
            new_topo = apply_rename_topology(topo_text, rmap)
            if new_topo != topo_text:
                files_changed += 1
                if not dry_run:
                    topology_path.write_text(new_topo, encoding="utf-8")
    return total, files_changed, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print changes without writing")
    ap.add_argument("--scenario", help="restrict to one scenario")
    ap.add_argument("--verbose", "-v", action="store_true", help="print every rename")
    args = ap.parse_args()

    scenarios = list_target_scenarios(args.scenario)
    grand_renames = 0
    grand_files = 0
    all_warnings: List[str] = []
    per_scen_counts = []
    for s in scenarios:
        t, f, w = process_scenario(s, args.dry_run, args.verbose)
        per_scen_counts.append((s, t, f))
        grand_renames += t
        grand_files += f
        all_warnings.extend(w)

    # Summary
    print("=" * 72)
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"{mode}: {grand_renames} renames across {grand_files} files "
          f"in {len(scenarios)} scenarios")
    print("=" * 72)
    for s, t, f in per_scen_counts:
        if t or f:
            print(f"  {s:<24} renames={t:<4} files={f}")

    if all_warnings:
        print("\nWarnings/Collisions:")
        for w in all_warnings:
            print(f"  ! {w}")
        # Fail on collision (contains 'COLLISION')
        if any("COLLISION" in w for w in all_warnings):
            print("\nAborting due to collisions.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
