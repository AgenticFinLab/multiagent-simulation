#!/usr/bin/env python
"""SorosPound LLM Simulation Runner

1992 Black Wednesday GBP attack: LLM agents with speculative pressure tracking

Usage:
    python examples/SorosPound/LLM/run_sorospound_llm.py \
        -c configs/SorosPound/LLM/simulation.yml
"""

import argparse
import asyncio

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(description="Run SorosPound LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/SorosPound/LLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("SorosPound Simulation - LLM Agents")
    print("=" * 70)
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
