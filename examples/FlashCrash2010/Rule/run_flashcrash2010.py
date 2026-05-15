#!/usr/bin/env python
"""FlashCrash2010 Rule-Based Simulation Runner

Run the 2010 Flash Crash simulation with rule-based agents.

This simulation models the May 6, 2010 flash crash using agents based on
Kirilenko et al. (2017) findings about HFT behavior during the event.

Usage:
    python examples/FlashCrash2010/Rule/run_flashcrash2010.py \
        -c configs/FlashCrash2010/Rule/simulation.yml

Expected Runtime: ~2-3 minutes for 200 rounds
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run FlashCrash2010 Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/Rule/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("FlashCrash2010 Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: 2010 Flash Crash (May 6, 2010)")
    print("Theory:     Kirilenko et al. (2017) - HFT Liquidity Dynamics")
    print("Agents:     HFT Market Makers, Momentum Chasers,")
    print("            Fundamental Traders, Stop-Loss Traders, Noise Traders")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 70 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 70)
        print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
