"""DispositionEffect Rag - RAG-augmented simulation runner."""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Keep third-party caches inside the writable experiment workspace.  This is
# especially important in managed/CI environments where the user profile is
# read-only.  Callers may override either location explicitly.
os.environ.setdefault(
    "MPLCONFIGDIR", str(project_root / "EXPERIMENT" / ".matplotlib")
)
os.environ.setdefault(
    "DISPOSITION_RAG_CACHE_DIR",
    str(project_root / "EXPERIMENT" / "DispositionEffect" / "Rag"),
)
os.environ.setdefault(
    "LLAMA_INDEX_CACHE_DIR",
    str(Path(os.environ["DISPOSITION_RAG_CACHE_DIR"]) / "model_cache"),
)

from masim.interface.simulation_runner import run_simulation_with_progress


def format_duration(seconds: float | None) -> str:
    """Format a duration as HH:MM:SS for progress display."""
    if seconds is None:
        return "--:--:--"
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def render_progress(status) -> str:
    """Render one compact progress bar from a real-round status update."""
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
    """Run DispositionEffect Rag simulation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c",
        "--config",
        default="configs/DispositionEffect/Rag/simulation.yml",
        help="Simulation YAML path",
    )
    parser.add_argument(
        "--output-dir",
        help="Fresh run directory; defaults to a timestamped directory",
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = args.output_dir or str(
        project_root / "EXPERIMENT" / "DispositionEffect" / "Rag" / "runs" / timestamp
    )
    output_path = Path(output_dir)
    records_path = output_path / "records"
    if records_path.is_dir() and any(records_path.iterdir()):
        raise FileExistsError(
            f"Refusing unsafe resume from non-empty records: {records_path}. "
            "Choose a new --output-dir; agent state is not restored by record resume."
        )
    os.environ["DISPOSITION_RAG_OUTPUT_DIR"] = output_dir
    config_path = args.config

    print("Starting DispositionEffect Rag simulation...")
    print(f"Config: {config_path}")
    print(f"Fresh output: {output_dir}")
    print("Initializing Ray actors and RAG indexes; the progress bar starts after setup.")
    print("-" * 50)

    final_status = None
    async for status in run_simulation_with_progress(config_path):
        final_status = status
        if status.state in {"running", "completed"}:
            end = "\n" if status.state == "completed" else ""
            print(f"\r{render_progress(status)}", end=end, flush=True)

    if final_status is None:
        raise RuntimeError("Simulation runner produced no status updates")
    if final_status.state == "error":
        print()
        raise RuntimeError(final_status.error or final_status.message)

    print("-" * 50)
    print("Simulation complete!")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped; Ray resources were released.")
