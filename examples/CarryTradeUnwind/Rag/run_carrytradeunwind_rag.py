#!/usr/bin/env python
"""CarryTradeUnwind Rag Simulation Runner

Carry trade unwind with RAG-augmented LLM agents — historical carry crisis
documents retrieved at each round to inform decisions.

Usage:
    python examples/CarryTradeUnwind/Rag/run_carrytradeunwind_rag.py \\
        -c configs/CarryTradeUnwind/Rag/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run CarryTradeUnwind Rag Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/CarryTradeUnwind/Rag/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("CarryTradeUnwind Simulation - Rag Agents")
    print("=" * 70)
    print("Phenomenon: Leveraged carry trades unwind when funding currency appreciates")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 70 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
