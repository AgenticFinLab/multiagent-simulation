#!/usr/bin/env python
"""Local Simulation Runner — each scenario opens in its own terminal window.

On macOS each scenario launches in a new Terminal.app window so you can
watch its live output.  On Linux it falls back to background subprocesses.
The orchestrator in the original terminal prints only step transitions.

Usage:
    python examples/run/local_script.py --scenarios AnchoringEffect AssetBubble
    python examples/run/local_script.py --all
    python examples/run/local_script.py --scenarios AnchoringEffect --dry-run
    python examples/run/local_script.py --list
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


def build_commands(
    scenario: str,
    variants: List[str],
) -> List[Tuple[str, str]]:
    """Return ordered ``(label, command)`` pairs for one scenario."""
    cmds: List[Tuple[str, str]] = []
    for v in variants:
        run_path = _find_run_script(scenario, v)
        if run_path:
            cmd = _parse_usage(run_path) or _fallback_cmd(run_path, scenario, v)
            cmds.append((f"{v}/run", cmd))
        ana_path = _find_analysis(scenario, v)
        if ana_path:
            cmd = _parse_usage(ana_path) or _fallback_cmd(ana_path, scenario, v)
            cmds.append((f"{v}/analysis", cmd))
    return cmds


# ── bash script generation ────────────────────────────────────────────────


def _generate_script(
    scenario: str,
    commands: List[Tuple[str, str]],
) -> Path:
    """Write a per-scenario bash runner and return its path."""
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_DIR.mkdir(parents=True, exist_ok=True)

    path = SCRIPT_DIR / f"{scenario}.sh"
    done = MARKER_DIR / f"{scenario}.done"
    fail = MARKER_DIR / f"{scenario}.fail"
    log = MARKER_DIR / f"{scenario}.log"
    step = MARKER_DIR / f"{scenario}.step"
    n = len(commands)

    lines = [
        "#!/usr/bin/env bash",
        f"# Auto-generated runner — {scenario}",
        "",
        'eval "$(conda shell.bash hook)"',
        f"conda activate {CONDA_ENV}",
        f'cd "{PROJECT_ROOT}"',
        "",
        f'exec > >(tee -a "{log}") 2>&1',
        "",
        f'printf "\\033]0;{scenario}\\007"',  # set terminal window title
        f'echo "================================================================"',
        f'echo "  {scenario}  ({n} steps)"',
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
        f'echo "  {scenario} — ALL {n} STEPS COMPLETED"',
        f'echo "  Finished: $(date)"',
        f'echo "================================================================"',
        f'touch "{done}"',
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    return path


# ── marker helpers ─────────────────────────────────────────────────────────


def _is_done(scenario: str) -> bool:
    return (MARKER_DIR / f"{scenario}.done").exists()


def _is_failed(scenario: str) -> bool:
    return (MARKER_DIR / f"{scenario}.fail").exists()


def _read_step(scenario: str) -> str:
    try:
        return (MARKER_DIR / f"{scenario}.step").read_text().strip()
    except FileNotFoundError:
        return ""


def _clean_markers():
    if MARKER_DIR.exists():
        for f in MARKER_DIR.iterdir():
            f.unlink()


def _launch_all_terminals(scenario_scripts: Dict[str, Path]):
    """Open one Terminal.app window per scenario via osascript.

    Each ``-e`` flag passes one line to osascript (as documented in
    ``man osascript``).  Using a single ``-e`` with embedded newlines
    is unreliable on some macOS versions.
    """
    cmd = ["osascript"]
    cmd += ["-e", 'tell application "Terminal"']
    for _scenario, script in scenario_scripts.items():
        cmd += ["-e", f'do script "bash \\"{script}\\""']
    cmd += ["-e", "activate"]
    cmd += ["-e", "end tell"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARNING: osascript failed (rc={result.returncode})")
        if result.stderr:
            print(f"           {result.stderr.strip()}")


# ── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Local simulation runner (subprocess-based, no tmux).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            examples:
              %(prog)s --scenarios AnchoringEffect AssetBubble
              %(prog)s --all
              %(prog)s --scenarios AnchoringEffect --variants Rule LLM RuleLLM Rag
              %(prog)s --all --dry-run
              %(prog)s --list
        """
        ),
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--scenarios",
        nargs="+",
        metavar="NAME",
        help="Scenario names to run",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run every discovered scenario",
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
        help=f"Variants to execute per scenario (default: {' '.join(DEFAULT_VARIANTS)})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without running anything",
    )
    return p


# ── entry-point ────────────────────────────────────────────────────────────


def _ts() -> str:
    """Short timestamp for log lines."""
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

    # ── resolve scenarios ──────────────────────────────────────────────────
    if args.all:
        scenarios = all_scenarios
    elif args.scenarios:
        bad = [s for s in args.scenarios if s not in all_scenarios]
        if bad:
            print(f"ERROR: unknown scenario(s): {', '.join(bad)}")
            print("  Use --list to see available names.")
            sys.exit(1)
        scenarios = args.scenarios
    else:
        _build_parser().print_help()
        sys.exit(1)

    # ── build execution plan ───────────────────────────────────────────────
    plan: Dict[str, List[Tuple[str, str]]] = {}
    for s in scenarios:
        cmds = build_commands(s, args.variants)
        if cmds:
            plan[s] = cmds
        else:
            print(f"  SKIP  {s} — no scripts for {args.variants}")

    if not plan:
        print("Nothing to run.")
        sys.exit(0)

    total_steps = sum(len(c) for c in plan.values())

    # ── dry run ────────────────────────────────────────────────────────────
    if args.dry_run:
        print(f"\nDRY RUN — {len(plan)} scenarios, " f"{total_steps} steps")
        print(f"Variants: {' -> '.join(args.variants)}\n")
        for s, cmds in plan.items():
            print(f"  {s}")
            for i, (label, cmd) in enumerate(cmds, 1):
                print(f"    {i}. [{label}]  {cmd}")
            print()
        return

    # ── prerequisites ──────────────────────────────────────────────────────
    if not shutil.which("conda"):
        print("ERROR: 'conda' not found in PATH.")
        sys.exit(1)

    # ── generate bash scripts ──────────────────────────────────────────────
    _clean_markers()
    scripts: Dict[str, Path] = {}
    for s, cmds in plan.items():
        scripts[s] = _generate_script(s, cmds)

    # ── header ─────────────────────────────────────────────────────────────
    print(f"\n{'=' * 64}")
    print(f"  Local Runner  ({_ts()})")
    print(f"  Scenarios : {len(plan)}")
    print(f"  Steps     : {total_steps}")
    print(f"  Variants  : {' -> '.join(args.variants)}")
    print(f"  Logs      : {MARKER_DIR}/")
    print(f"{'=' * 64}\n")

    # ── launch all scenarios ─────────────────────────────────────────────
    is_mac = sys.platform == "darwin"
    running: Dict[str, float] = {}  # scenario -> start_time
    prev_steps: Dict[str, str] = {}
    completed: List[Tuple[str, float]] = []
    failed: List[Tuple[str, float, str]] = []

    t0 = time.time()

    if is_mac:
        _launch_all_terminals(scripts)
    else:
        for s in scripts:
            subprocess.Popen(
                ["bash", str(scripts[s])],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    where = "Terminal.app" if is_mac else "subprocess"
    for s in plan:
        running[s] = time.time()
        labels = " -> ".join(lbl for lbl, _ in plan[s])
        print(f"  [{_ts()}] >> {s}  ({where})")
        print(f"             {labels}")

    # ── monitor until all finish ──────────────────────────────────────────
    while running:
        for s in list(running):
            start = running[s]

            if _is_done(s):
                elapsed = time.time() - start
                del running[s]
                prev_steps.pop(s, None)
                completed.append((s, elapsed))
                print(f"  [{_ts()}] << {s:<30s}  DONE  ({elapsed / 60:.1f} min)")
                continue

            if _is_failed(s):
                elapsed = time.time() - start
                del running[s]
                prev_steps.pop(s, None)
                label = (MARKER_DIR / f"{s}.fail").read_text().strip()
                failed.append((s, elapsed, label))
                print(
                    f"  [{_ts()}] !! {s:<30s}  FAIL at {label}  "
                    f"({elapsed / 60:.1f} min)"
                )
                print(f"             log: {MARKER_DIR / f'{s}.log'}")
                continue

            # Step transition — print only when the step label changes.
            cur = _read_step(s)
            if cur and cur != prev_steps.get(s):
                prev_steps[s] = cur
                print(f"  [{_ts()}]    {s:<30s}  {cur}")

        if running:
            time.sleep(2)

    wall = time.time() - t0

    # ── summary ────────────────────────────────────────────────────────────
    print(f"\n{'=' * 64}")
    print(f"  SUMMARY")
    print(f"{'=' * 64}")
    if completed:
        print(f"\n  Succeeded ({len(completed)}):")
        for s, t in completed:
            print(f"    + {s:<35s}  {t / 60:.1f} min")
    if failed:
        print(f"\n  Failed ({len(failed)}):")
        for s, t, label in failed:
            print(f"    - {s:<35s}  at {label}  ({t / 60:.1f} min)")
    print(f"\n  Wall clock : {wall / 60:.1f} min")
    print(f"  Logs       : {MARKER_DIR}/")
    print()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
