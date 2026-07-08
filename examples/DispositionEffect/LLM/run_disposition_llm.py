#!/usr/bin/env python
"""DispositionEffectLLM Simulation Runner

Usage:
    python examples/DispositionEffect/LLM/run_disposition_llm.py -c configs/DispositionEffect/LLM/simulation.yml
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
import torch  # Load native DLLs before MASim/NumPy on Windows.

project_root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)
sys.path.insert(0, project_root)

from masim.interface.simulation_runner import SimulationRunner
from masim.utils.config import setup_logging


def format_duration(seconds):
    if seconds is None:
        return "--:--:--"
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def render_progress(status):
    width = 30
    completed = min(width, int(width * status.progress_pct / 100))
    bar = "#" * completed + "-" * (width - completed)
    return (
        f"[{bar}] {status.progress_pct:6.2f}% "
        f"| round {status.current_round:>3}/{status.total_rounds} "
        f"| elapsed {format_duration(status.elapsed_seconds)} "
        f"| ETA {format_duration(status.eta_seconds)}"
    )


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run DispositionEffectLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/DispositionEffect/LLM/simulation.yml",
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    parser.add_argument(
        "--output-dir",
        help="Fresh output directory; defaults to a timestamped run directory",
    )
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set!")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = args.output_dir or os.path.join(
        project_root, "EXPERIMENT", "DispositionEffect", "LLM", "runs", timestamp
    )
    records_path = Path(output_dir) / "records"
    if records_path.is_dir() and any(records_path.iterdir()):
        raise FileExistsError(
            f"Refusing unsafe resume from non-empty records: {records_path}. "
            "Choose a new --output-dir."
        )
    os.environ["DISPOSITION_LLM_OUTPUT_DIR"] = output_dir

    runner = SimulationRunner(args.config)
    if not await runner.setup():
        raise RuntimeError(runner.status.error or "Simulation setup failed")
    if args.rounds is not None:
        runner.config.setting["total_rounds"] = args.rounds
        runner.status.total_rounds = args.rounds

    print("\n" + "=" * 60)
    print("DispositionEffectLLM Simulation")
    print("=" * 60)
    print("Phenomenon: Sell winners too early, hold losers too long")
    print("Theory: Prospect Theory (Kahneman & Tversky 1979)")
    print("Rounds: %s" % runner.config.setting["total_rounds"])
    print("Fresh output: %s" % output_dir)
    print("=" * 60 + "\n")

    try:
        async for _ in runner.run():
            print(f"\r{render_progress(runner.status)}", end="", flush=True)
        print()
        if runner.status.state == "error":
            raise RuntimeError(runner.status.error or runner.status.message)
        print("\n" + "=" * 60)
        print(
            "Simulation Complete! Rounds: %d"
            % runner.config.setting["total_rounds"]
        )
        print("Results saved to: %s" % output_dir)
        print("=" * 60)
    finally:
        await runner.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped; Ray resources were released.")
