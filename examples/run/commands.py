#!/usr/bin/env python
"""Single-Scenario Parallel-Variant Runner.

Runs ONE scenario at a time, but launches all selected variants
(Rule, LLM, RuleLLM, Rag) **in parallel** — each in its own subprocess.
Within each variant the run_*.py and analysis.py still execute sequentially.

Usage:
    python examples/run/commands.py --scenario EchoChamber
    python examples/run/commands.py --scenario AnchoringEffect --variants Rule LLM RuleLLM Rag
    python examples/run/commands.py --scenario AssetBubble --dry-run
    python examples/run/commands.py --list
"""

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── constants ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
RUN_DIR = PROJECT_ROOT / "examples" / "run"
MARKER_DIR = RUN_DIR / ".status"
SCRIPT_DIR = RUN_DIR / ".generated"

CONDA_ENV = "LMSim"
DEFAULT_VARIANTS = ["Rule", "LLM", "RuleLLM"]
ALL_VARIANTS = ["Rule", "LLM", "RuleLLM", "Rag"]
EXCLUDE_DIRS = frozenset({"Test", "run", "__pycache__", "document-sources", "Demo"})


# ── scenario / command discovery ───────────────────────────────────────────


def discover_scenarios() -> List[str]:
    """Return sorted scenario directory names under ``examples/``."""
    return sorted(
        d.name
        for d in EXAMPLES_DIR.iterdir()
        if d.is_dir()
        and d.name not in EXCLUDE_DIRS
        and not d.name.startswith(".")
        and not d.name.startswith("_")
    )


def _parse_usage(filepath: Path) -> Optional[str]:
    """Extract the ``Usage:`` command from a Python file's module docstring."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        ds = ast.get_docstring(tree)
        if not ds:
            return None
        m = re.search(r"Usage:\s*\n(.*?)(?:\n\s*\n|\n[A-Z]|\Z)", ds, re.DOTALL)
        if not m:
            return None
        raw = m.group(1).strip()
        joined = re.sub(r"\\\s*\n\s*", " ", raw)
        return re.sub(r"\s{2,}", " ", joined).strip()
    except Exception:
        return None


def _find_run_script(scenario: str, variant: str) -> Optional[Path]:
    d = EXAMPLES_DIR / scenario / variant
    if not d.is_dir():
        return None
    hits = list(d.glob("run_*.py"))
    return hits[0] if hits else None


def _find_analysis(scenario: str, variant: str) -> Optional[Path]:
    p = EXAMPLES_DIR / scenario / variant / "analysis.py"
    return p if p.exists() else None


def _fallback_cmd(script: Path, scenario: str, variant: str) -> str:
    rel = script.relative_to(PROJECT_ROOT)
    return f"python {rel} -c configs/{scenario}/{variant}/simulation.yml"


def build_variant_commands(
    scenario: str,
    variant: str,
) -> List[Tuple[str, str]]:
    """Return ordered ``(label, command)`` pairs for one variant of a scenario."""
    cmds: List[Tuple[str, str]] = []
    run_path = _find_run_script(scenario, variant)
    if run_path:
        cmd = _parse_usage(run_path) or _fallback_cmd(run_path, scenario, variant)
        cmds.append((f"{variant}/run", cmd))
    ana_path = _find_analysis(scenario, variant)
    if ana_path:
        cmd = _parse_usage(ana_path) or _fallback_cmd(ana_path, scenario, variant)
        cmds.append((f"{variant}/analysis", cmd))
    return cmds


# ── per-variant bash script generation ────────────────────────────────────


def _generate_variant_script(
    scenario: str,
    variant: str,
    commands: List[Tuple[str, str]],
) -> Path:
    """Write a per-variant bash runner and return its path.

    Marker files use ``{scenario}-{variant}`` as the key so multiple
    variants can run concurrently without colliding.
    """
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_DIR.mkdir(parents=True, exist_ok=True)

    key = f"{scenario}-{variant}"
    path = SCRIPT_DIR / f"{key}.sh"
    done = MARKER_DIR / f"{key}.done"
    fail = MARKER_DIR / f"{key}.fail"
    log = MARKER_DIR / f"{key}.log"
    step = MARKER_DIR / f"{key}.step"
    n = len(commands)

    lines = [
        "#!/usr/bin/env bash",
        f"# Auto-generated runner — {scenario} / {variant}",
        "",
        'eval "$(conda shell.bash hook)"',
        f"conda activate {CONDA_ENV}",
        f'cd "{PROJECT_ROOT}"',
        "",
        f'exec > >(tee -a "{log}") 2>&1',
        "",
        f'printf "\\033]0;{scenario} — {variant}\\007"',
        f'echo "================================================================"',
        f'echo "  {scenario} / {variant}  ({n} steps)"',
        f'echo "  Started: $(date)"',
        f'echo "================================================================"',
    ]

    for i, (label, cmd) in enumerate(commands, 1):
        lines += [
            "",
            f'echo "{i}/{n} {label}" > "{step}"',
            f'echo ""',
            f'echo ">> [{i}/{n}] {label}"',
            f'echo "   {cmd}"',
            f'echo ""',
            f"if ! {cmd}; then",
            f'    echo "!! FAILED at step {i}/{n}: {label}"',
            f'    echo "{label}" > "{fail}"',
            f"    exit 1",
            f"fi",
            f'echo "<< [{i}/{n}] {label} ok"',
        ]

    lines += [
        "",
        f'echo "================================================================"',
        f'echo "  {scenario} / {variant} — ALL {n} STEPS COMPLETED"',
        f'echo "  Finished: $(date)"',
        f'echo "================================================================"',
        f'touch "{done}"',
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    return path


# ── marker helpers ─────────────────────────────────────────────────────────


def _marker_key(scenario: str, variant: str) -> str:
    return f"{scenario}-{variant}"


def _is_done(scenario: str, variant: str) -> bool:
    return (MARKER_DIR / f"{_marker_key(scenario, variant)}.done").exists()


def _is_failed(scenario: str, variant: str) -> bool:
    return (MARKER_DIR / f"{_marker_key(scenario, variant)}.fail").exists()


def _read_step(scenario: str, variant: str) -> str:
    try:
        return (
            (MARKER_DIR / f"{_marker_key(scenario, variant)}.step").read_text().strip()
        )
    except FileNotFoundError:
        return ""


def _read_fail_label(scenario: str, variant: str) -> str:
    try:
        return (
            (MARKER_DIR / f"{_marker_key(scenario, variant)}.fail").read_text().strip()
        )
    except FileNotFoundError:
        return "unknown"


def _clean_markers(scenario: str, variants: List[str]):
    """Remove marker files for the given scenario/variants."""
    if not MARKER_DIR.exists():
        return
    for v in variants:
        key = _marker_key(scenario, v)
        for suffix in (".done", ".fail", ".log", ".step"):
            p = MARKER_DIR / f"{key}{suffix}"
            if p.exists():
                p.unlink()


# ── launch helpers ─────────────────────────────────────────────────────────


def _launch_terminals(variant_scripts: Dict[str, Path], scenario: str):
    """Open one Terminal.app window per variant via osascript (macOS)."""
    cmd = ["osascript"]
    cmd += ["-e", 'tell application "Terminal"']
    for _variant, script in variant_scripts.items():
        cmd += ["-e", f'do script "bash \\"{script}\\""']
    cmd += ["-e", "activate"]
    cmd += ["-e", "end tell"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARNING: osascript failed (rc={result.returncode})")
        if result.stderr:
            print(f"           {result.stderr.strip()}")


def _launch_subprocesses(variant_scripts: Dict[str, Path]):
    """Launch each variant as a background subprocess (Linux fallback)."""
    for _variant, script in variant_scripts.items():
        subprocess.Popen(
            ["bash", str(script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


# ── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Single-scenario runner with parallel variants.  "
            "Runs ONE scenario, with Rule / LLM / RuleLLM executing "
            "simultaneously in separate processes."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            examples:
              %(prog)s --scenario EchoChamber
              %(prog)s --scenario AnchoringEffect --variants Rule LLM RuleLLM Rag
              %(prog)s --scenario AssetBubble --dry-run
              %(prog)s --list
        """
        ),
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--scenario",
        metavar="NAME",
        help="Scenario name to run (single scenario)",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios and exit",
    )
    p.add_argument(
        "--variants",
        nargs="+",
        default=DEFAULT_VARIANTS,
        choices=ALL_VARIANTS,
        metavar="V",
        help=f"Variants to execute in parallel (default: {' '.join(DEFAULT_VARIANTS)})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without running anything",
    )
    return p


# ── entry-point ────────────────────────────────────────────────────────────


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def main() -> None:
    args = _build_parser().parse_args()
    all_scenarios = discover_scenarios()

    # ── --list ─────────────────────────────────────────────────────────────
    if args.list:
        print(f"\nAvailable scenarios ({len(all_scenarios)}):\n")
        for s in all_scenarios:
            variants = [v for v in ALL_VARIANTS if _find_run_script(s, v)]
            print(f"  {s:<40s} [{', '.join(variants)}]")
        print()
        return

    # ── resolve scenario ───────────────────────────────────────────────────
    if not args.scenario:
        _build_parser().print_help()
        sys.exit(1)

    scenario = args.scenario
    if scenario not in all_scenarios:
        print(f"ERROR: unknown scenario '{scenario}'")
        print("  Use --list to see available names.")
        sys.exit(1)

    # ── build per-variant command lists ────────────────────────────────────
    variant_plan: Dict[str, List[Tuple[str, str]]] = {}
    for v in args.variants:
        cmds = build_variant_commands(scenario, v)
        if cmds:
            variant_plan[v] = cmds
        else:
            print(f"  SKIP  {v} — no scripts found for {scenario}/{v}")

    if not variant_plan:
        print("Nothing to run.")
        sys.exit(0)

    total_steps = sum(len(c) for c in variant_plan.values())

    # ── dry run ────────────────────────────────────────────────────────────
    if args.dry_run:
        print(f"\nDRY RUN — {scenario}")
        print(f"Variants (parallel): {', '.join(variant_plan.keys())}")
        print(f"Total steps: {total_steps}\n")
        for v, cmds in variant_plan.items():
            print(f"  {v}")
            for i, (label, cmd) in enumerate(cmds, 1):
                print(f"    {i}. [{label}]  {cmd}")
            print()
        return

    # ── prerequisites ──────────────────────────────────────────────────────
    if not shutil.which("conda"):
        print("ERROR: 'conda' not found in PATH.")
        sys.exit(1)

    # ── generate bash scripts (one per variant) ───────────────────────────
    _clean_markers(scenario, list(variant_plan.keys()))
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_DIR.mkdir(parents=True, exist_ok=True)

    scripts: Dict[str, Path] = {}
    for v, cmds in variant_plan.items():
        scripts[v] = _generate_variant_script(scenario, v, cmds)

    # ── header ─────────────────────────────────────────────────────────────
    print(f"\n{'=' * 64}")
    print(f"  Parallel-Variant Runner  ({_ts()})")
    print(f"  Scenario  : {scenario}")
    print(f"  Variants  : {' | '.join(variant_plan.keys())}  (parallel)")
    print(f"  Steps     : {total_steps}")
    print(f"  Logs      : {MARKER_DIR}/")
    print(f"{'=' * 64}\n")

    # ── launch all variants in parallel ───────────────────────────────────
    is_mac = sys.platform == "darwin"
    t0 = time.time()

    if is_mac:
        _launch_terminals(scripts, scenario)
    else:
        _launch_subprocesses(scripts)

    where = "Terminal.app" if is_mac else "subprocess"
    running: Dict[str, float] = {}
    prev_steps: Dict[str, str] = {}
    completed: List[Tuple[str, float]] = []
    failed: List[Tuple[str, float, str]] = []

    for v in variant_plan:
        running[v] = time.time()
        labels = " -> ".join(lbl for lbl, _ in variant_plan[v])
        print(f"  [{_ts()}] >> {v:<15s}  ({where})")
        print(f"             {labels}")

    # ── monitor until all variants finish ──────────────────────────────────
    while running:
        for v in list(running):
            start = running[v]

            if _is_done(scenario, v):
                elapsed = time.time() - start
                del running[v]
                prev_steps.pop(v, None)
                completed.append((v, elapsed))
                print(f"  [{_ts()}] << {v:<15s}  DONE  ({elapsed / 60:.1f} min)")
                continue

            if _is_failed(scenario, v):
                elapsed = time.time() - start
                del running[v]
                prev_steps.pop(v, None)
                label = _read_fail_label(scenario, v)
                failed.append((v, elapsed, label))
                key = _marker_key(scenario, v)
                print(
                    f"  [{_ts()}] !! {v:<15s}  FAIL at {label}  "
                    f"({elapsed / 60:.1f} min)"
                )
                print(f"             log: {MARKER_DIR / f'{key}.log'}")
                continue

            cur = _read_step(scenario, v)
            if cur and cur != prev_steps.get(v):
                prev_steps[v] = cur
                print(f"  [{_ts()}]    {v:<15s}  {cur}")

        if running:
            time.sleep(2)

    wall = time.time() - t0

    # ── summary ────────────────────────────────────────────────────────────
    print(f"\n{'=' * 64}")
    print(f"  {scenario} — SUMMARY")
    print(f"{'=' * 64}")
    if completed:
        print(f"\n  Succeeded ({len(completed)}):")
        for v, t in completed:
            print(f"    + {v:<20s}  {t / 60:.1f} min")
    if failed:
        print(f"\n  Failed ({len(failed)}):")
        for v, t, label in failed:
            print(f"    - {v:<20s}  at {label}  ({t / 60:.1f} min)")
    print(f"\n  Wall clock : {wall / 60:.1f} min")
    print(f"  Logs       : {MARKER_DIR}/")
    print()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
