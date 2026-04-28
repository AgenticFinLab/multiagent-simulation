#!/usr/bin/env python
"""Batch Simulation Runner — tmux-based parallel orchestrator.

Launches simulation scenarios in parallel tmux windows.  Within each window
the selected variants (Rule -> LLM -> RuleLLM -> Rag) are executed
sequentially:  run_*.py  ->  analysis.py  ->  (next variant) ...

Run commands are extracted automatically from the ``Usage:`` section in each
script's module docstring, so no manual command construction is needed.

Quick-start
-----------
  # Run two scenarios with default settings (Rule + LLM + RuleLLM, 2 parallel)
  python examples/run/script.py --scenarios AnchoringEffect AssetBubble

  # Run all scenarios, 4 at a time, including Rag variant
  python examples/run/script.py --all --max-parallel 4 --variants Rule LLM RuleLLM Rag

  # Preview commands without executing
  python examples/run/script.py --all --dry-run

  # List available scenarios and their variants
  python examples/run/script.py --list

Tip: run this script itself inside tmux so it survives SSH disconnects:

  tmux new -s orchestrator 'python examples/run/script.py --all --max-parallel 4'

tmux cheat-sheet while running:
  Attach:   tmux attach -t masim
  Windows:  Ctrl-b n / Ctrl-b p  (next / prev)
  Detach:   Ctrl-b d
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
POLL_INTERVAL_S = 10


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
        # Join backslash-continuation lines and collapse whitespace.
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
    """Construct a command from convention when docstring parsing fails."""
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
    n = len(commands)

    lines = [
        "#!/usr/bin/env bash",
        f"# Auto-generated runner — {scenario}",
        "",
        "# ── conda activation ──",
        'eval "$(conda shell.bash hook)"',
        f"conda activate {CONDA_ENV}",
        f'cd "{PROJECT_ROOT}"',
        "",
        "# ── duplicate stdout+stderr to log file ──",
        f'exec > >(tee -a "{log}") 2>&1',
        "",
        "echo ''",
        f'echo "================================================================"',
        f'echo "  {scenario}  ({n} steps)"',
        f'echo "  Started: $(date)"',
        f'echo "================================================================"',
    ]

    for i, (label, cmd) in enumerate(commands, 1):
        lines += [
            "",
            f'echo ""',
            f'echo ">> [{i}/{n}] {label}"',
            f'echo "   {cmd}"',
            f'echo ""',
            f"if ! {cmd}; then",
            f'    echo ""',
            f'    echo "!! FAILED at step {i}/{n}: {label}"',
            f'    echo "{label}" > "{fail}"',
            f"    exit 1",
            f"fi",
            f'echo "<< [{i}/{n}] {label} ok"',
        ]

    lines += [
        "",
        f'echo ""',
        f'echo "================================================================"',
        f'echo "  {scenario} — ALL {n} STEPS COMPLETED"',
        f'echo "  Finished: $(date)"',
        f'echo "================================================================"',
        f'touch "{done}"',
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    return path


# ── tmux helpers ───────────────────────────────────────────────────────────


def _tmux(*args: str, check: bool = True):
    return subprocess.run(
        ["tmux", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _ensure_session(session: str):
    """Create the tmux session if it does not already exist."""
    exists = _tmux("has-session", "-t", session, check=False).returncode == 0
    if not exists:
        _tmux("new-session", "-d", "-s", session, "-n", "_control")
    # Keep finished panes visible so the user can scroll back.
    _tmux(
        "set-option",
        "-t",
        session,
        "remain-on-exit",
        "on",
        check=False,
    )


def _launch(session: str, scenario: str, script: Path):
    """Open a new tmux window that runs *script*."""
    _tmux("kill-window", "-t", f"{session}:{scenario}", check=False)
    _tmux("new-window", "-t", session, "-n", scenario, f'bash "{script}"')


def _is_done(scenario: str) -> bool:
    return (MARKER_DIR / f"{scenario}.done").exists()


def _is_failed(scenario: str) -> bool:
    return (MARKER_DIR / f"{scenario}.fail").exists()


def _clean_markers():
    """Remove marker/log files from previous runs."""
    if MARKER_DIR.exists():
        for f in MARKER_DIR.iterdir():
            f.unlink()


# ── CLI ────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Batch simulation runner with tmux-based parallelism.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            examples:
              %(prog)s --scenarios AnchoringEffect AssetBubble
              %(prog)s --all --max-parallel 4
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
        "--max-parallel",
        type=int,
        default=2,
        metavar="N",
        help="Maximum scenarios running at the same time (default: 2)",
    )
    p.add_argument(
        "--variants",
        nargs="+",
        default=DEFAULT_VARIANTS,
        choices=ALL_VARIANTS,
        metavar="V",
        help=(
            "Variants to execute per scenario, in order "
            f"(default: {' '.join(DEFAULT_VARIANTS)})"
        ),
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the execution plan without launching anything",
    )
    p.add_argument(
        "--session",
        default="masim",
        metavar="NAME",
        help="tmux session name (default: masim)",
    )
    return p


# ── entry-point ────────────────────────────────────────────────────────────


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
        print(
            f"\nDRY RUN — {len(plan)} scenarios, "
            f"{total_steps} steps, "
            f"max-parallel={args.max_parallel}"
        )
        print(f"Variants: {' -> '.join(args.variants)}\n")
        for s, cmds in plan.items():
            print(f"  {s}")
            for i, (label, cmd) in enumerate(cmds, 1):
                print(f"    {i}. [{label}]  {cmd}")
            print()
        return

    # ── prerequisites ──────────────────────────────────────────────────────
    for tool in ("tmux", "conda"):
        if not shutil.which(tool):
            print(f"ERROR: '{tool}' not found in PATH.")
            sys.exit(1)

    # ── generate bash scripts ──────────────────────────────────────────────
    _clean_markers()
    scripts: Dict[str, Path] = {}
    for s, cmds in plan.items():
        scripts[s] = _generate_script(s, cmds)

    # ── tmux session ───────────────────────────────────────────────────────
    session = args.session
    _ensure_session(session)

    # ── orchestration loop ─────────────────────────────────────────────────
    pending = list(plan.keys())
    running: Dict[str, float] = {}
    completed: List[Tuple[str, float]] = []
    failed: List[Tuple[str, float, str]] = []

    print(f"\n{'=' * 64}")
    print(f"  Batch Runner")
    print(f"  Scenarios : {len(pending)}")
    print(f"  Steps     : {total_steps}")
    print(f"  Variants  : {' -> '.join(args.variants)}")
    print(f"  Parallel  : {args.max_parallel}")
    print(f"  Session   : {session}")
    print(f"  Attach    : tmux attach -t {session}")
    print(f"{'=' * 64}\n")

    t0 = time.time()

    while pending or running:
        # Fill available slots.
        while pending and len(running) < args.max_parallel:
            s = pending.pop(0)
            _launch(session, s, scripts[s])
            running[s] = time.time()
            n_steps = len(plan[s])
            print(
                f"  >> LAUNCH  {s:<35s}  "
                f"({n_steps} steps, "
                f"{len(running)}/{args.max_parallel} slots)"
            )

        # Poll for completion.
        for s in list(running):
            if _is_done(s):
                elapsed = time.time() - running.pop(s)
                completed.append((s, elapsed))
                print(f"  << DONE    {s:<35s}  " f"({elapsed / 60:.1f} min)")
            elif _is_failed(s):
                elapsed = time.time() - running.pop(s)
                label = (MARKER_DIR / f"{s}.fail").read_text().strip()
                failed.append((s, elapsed, label))
                print(
                    f"  !! FAIL    {s:<35s}  " f"at {label}  ({elapsed / 60:.1f} min)"
                )

        if running:
            time.sleep(POLL_INTERVAL_S)

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
    print(f"  tmux       : tmux attach -t {session}")
    print()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
