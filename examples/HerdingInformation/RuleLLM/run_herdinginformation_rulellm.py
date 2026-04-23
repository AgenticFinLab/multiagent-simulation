#!/usr/bin/env python
"""HerdingInformation RuleLLM Simulation Runner

Information cascade occurs when individuals ignore private signals and follow the crowd

Usage:
    python examples/HerdingInformation/RuleLLM/run_herdinginformation_rulellm.py \
        -c configs/HerdingInformation/RuleLLM/simulation.yml
"""

import argparse
import asyncio

import os

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    load_dotenv()
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run HerdingInformation RuleLLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/HerdingInformation/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("HerdingInformation Simulation - RuleLLM Agents")
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
