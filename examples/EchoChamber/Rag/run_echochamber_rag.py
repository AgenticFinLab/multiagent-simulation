#!/usr/bin/env python
"""EchoChamber RAG-LLM Simulation Runner

EchoChamber simulation

Usage:
    python examples/EchoChamber/Rag/run_echochamber_rag.py -c configs/EchoChamber/Rag/simulation.yml
"""

import argparse
import asyncio
import os
import sys
from contextlib import contextmanager

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


@contextmanager
def single_instance(record_path: str):
    """Prevent overlapping local Ray clusters from writing one experiment."""
    os.makedirs(record_path, exist_ok=True)
    lock_path = os.path.join(record_path, ".simulation.lock")
    lock_file = open(lock_path, "a+", encoding="utf-8")
    try:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            try:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError(
                    "Another EchoChamber RAG simulation is already using "
                    f"{record_path!r}. Stop it before starting a second run."
                ) from exc
        else:
            import fcntl

            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError(
                    "Another EchoChamber RAG simulation is already using "
                    f"{record_path!r}. Stop it before starting a second run."
                ) from exc
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        yield
    finally:
        lock_file.close()


async def main():
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(description="Run EchoChamber RAG-LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the Rag simulation.yml file.",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("EchoChamber Simulation - RAG-LLM Agents")
    print("=" * 70)
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 70 + "\n")

    with single_instance(config.setting["record_path"]):
        simulator = GeneralSimulator(config)

        try:
            await simulator.setup()
            await simulator.run()
            print("\n" + "=" * 70)
            print("Simulation Complete!")
            print("=" * 70)
        finally:
            await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
