#!/usr/bin/env python
"""SorosPound Rule-Based Simulation Runner

1992 Black Wednesday GBP attack: rule-based agents with speculative pressure tracking

Usage:
    python examples/SorosPound/Rule/run_sorospound.py \
        -c configs/SorosPound/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run SorosPound Rule-Based Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/SorosPound/Rule/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("SorosPound Simulation - Rule-Based Agents")
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
