"""Simulation worker process — run via ``python -m masim.interface.simulation_worker``.

This module is spawned as a child process by the Streamlit UI (app.py).
It communicates progress back to the parent via structured lines on stdout:

    MASIM_EVENT {"type": "setup", "message": "..."}
    MASIM_EVENT {"type": "running", "total_rounds": N, "current_round": M}
    MASIM_EVENT {"type": "done"}
    MASIM_EVENT {"type": "error", "error": "..."}

The parent reads these events to update the live progress display.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import traceback
from pathlib import Path


def _emit(event: dict) -> None:
    """Print a structured event line that the parent process can parse."""
    print(f"MASIM_EVENT {json.dumps(event, ensure_ascii=False)}", flush=True)


async def _run(config_path: str) -> None:
    from masim.interface.simulation_runner import SimulationRunner

    runner = SimulationRunner(config_path)

    # --- Setup ---
    _emit({"type": "setup", "message": "Loading configuration and initializing agents…"})
    runner.clear_records()
    success = await runner.setup()
    if not success:
        _emit({"type": "error", "error": runner.status.error or "Setup failed"})
        return

    total_rounds = runner.status.total_rounds or 0
    _emit({
        "type": "running",
        "total_rounds": total_rounds,
        "current_round": 0,
        "message": f"Setup complete — starting {total_rounds} rounds",
    })

    # --- Run rounds ---
    def on_progress(status):
        _emit({
            "type": "running",
            "total_rounds": status.total_rounds,
            "current_round": status.current_round,
            "message": status.message,
        })

    async for _update in runner.run(progress_callback=on_progress):
        pass  # progress_callback already emits events

    # --- Shutdown ---
    await runner.shutdown()

    if runner.status.state == "error":
        _emit({"type": "error", "error": runner.status.error or "Simulation failed"})
    else:
        _emit({"type": "done"})


def main():
    # --- Load .env and rotate numbered API keys BEFORE any scenario code runs ---
    # Scenario players.py files call LangChainAPIInference() directly, which
    # expects e.g. ARK_API_KEY. Users configure ARK_API_KEY_1, ARK_API_KEY_2, etc.
    # for load-balancing. We pick one randomly and set the canonical key here,
    # at the process entry point, so every downstream consumer finds it.
    import os
    import random

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    # Rotate numbered keys for all known providers
    for provider in ("ARK", "DEEPSEEK", "OPENAI", "ZHIPU"):
        key_var = f"{provider}_API_KEY"
        if os.environ.get(key_var):
            continue  # canonical key already set, no rotation needed
        candidates = [
            v for k, v in os.environ.items()
            if k.startswith(f"{key_var}_") and k[len(key_var) + 1:].isdigit() and v
        ]
        if candidates:
            os.environ[key_var] = random.choice(candidates)

    parser = argparse.ArgumentParser(description="MASIM simulation worker")
    parser.add_argument("--config", required=True, help="Path to simulation.yml")
    args = parser.parse_args()

    config_path = str(Path(args.config).resolve())
    if not Path(config_path).exists():
        _emit({"type": "error", "error": f"Config file not found: {config_path}"})
        sys.exit(1)

    try:
        asyncio.run(_run(config_path))
    except Exception as exc:
        tb = traceback.format_exc()
        _emit({"type": "error", "error": f"{exc}\n{tb}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
