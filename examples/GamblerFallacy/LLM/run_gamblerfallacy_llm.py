#!/usr/bin/env python
"""GamblerFallacy LLM Simulation Runner

Gambler's Fallacy: LLM streak-reversal vs hot-hand vs rational agents

Usage:
    python examples/GamblerFallacy/LLM/run_gamblerfallacy_llm.py \
        -c configs/GamblerFallacy/LLM/simulation.yml
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

    parser = argparse.ArgumentParser(description="Run GamblerFallacy LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/GamblerFallacy/LLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("GamblerFallacy Simulation - LLM Agents")
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
