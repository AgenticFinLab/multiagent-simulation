#!/usr/bin/env python
"""FramingEffect RuleLLM Simulation Runner

Framing Effect: rule-guided LLM agents with quantitative framing susceptibility rules

Usage:
    python examples/FramingEffect/RuleLLM/run_framingeffect_rulellm.py \
        -c configs/FramingEffect/RuleLLM/simulation.yml
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

    parser = argparse.ArgumentParser(description="Run FramingEffect RuleLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FramingEffect/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("FramingEffect Simulation - RuleLLM Agents")
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
