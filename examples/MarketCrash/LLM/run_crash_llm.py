#!/usr/bin/env python
"""MarketCrashLLM Simulation Runner

Run LLM-powered crash investor simulation.

Usage:
    python examples/MarketCrash/LLM/run_crash_llm.py -c configs/MarketCrash/LLM/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required)
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

    parser = argparse.ArgumentParser(description="Run MarketCrashLLM Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default="configs/MarketCrash/LLM/simulation.yml"
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set! LLM investors will not function.")

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("MarketCrashLLM Simulation")
    print("=" * 60)
    print("Phenomenon: Market Crash with Liquidity Spiral")
    print("Theory: Minsky Moment, Brunnermeier & Pedersen (2009)")
    print("Rounds: %s" % config.setting["total_rounds"])
    print("=" * 60 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 60)
        print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
        print("=" * 60)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
