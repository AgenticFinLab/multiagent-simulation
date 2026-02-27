#!/usr/bin/env python
"""MomentumEffectLLM Simulation Runner

Usage:
    python examples/MomentumEffectLLM/run_momentum_llm.py -c configs/MomentumEffectLLM/simulation.yml
"""

import argparse
import asyncio
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run MomentumEffectLLM Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default="configs/MomentumEffectLLM/simulation.yml"
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set!")

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("MomentumEffectLLM Simulation")
    print("=" * 60)
    print("Phenomenon: Momentum Effect - Winners keep winning")
    print("Theory: Jegadeesh & Titman (1993)")
    print("Rounds: %s" % config.setting["total_rounds"])
    print("=" * 60 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 60)
        print("Simulation Complete! Rounds: %d" % len(results))
        print("=" * 60)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
