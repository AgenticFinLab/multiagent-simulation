#!/usr/bin/env python
"""RepresentativenessBias Rule-Based Simulation Runner

Representativeness bias: rule-based agents with pattern matching vs. base rates

Usage:
    python examples/RepresentativenessBias/Rule/run_representativenessbias.py \
        -c configs/RepresentativenessBias/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run RepresentativenessBias Rule-Based Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/RepresentativenessBias/Rule/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("RepresentativenessBias Simulation - Rule-Based Agents")
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
