#!/usr/bin/env python
"""HerdEffectRuleLLM Simulation Runner

Run hybrid Rule+LLM investor simulation for emergent herding behavior.
Uses ByteDance Doubao API via lmbase.

Usage:
    python examples/HerdEffect/RuleLLM/run_herd_rulellm.py -c configs/HerdEffect/RuleLLM/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required)

Requirements:
    pip install lmbase python-dotenv
"""

import argparse
import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run HerdEffectRuleLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/HerdEffect/RuleLLM/simulation.yml",
        help="Path to simulation config file",
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=None,
        help="Override number of rounds",
    )
    args = parser.parse_args()

    # Check for API key (ByteDance Doubao)
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("=" * 60)
        print("WARNING: ARK_API_KEY environment variable not set!")
        print("LLM investors will not function properly.")
        print("Set it via: export ARK_API_KEY='your-doubao-api-key'")
        print("Or create a .env file with: ARK_API_KEY=your-doubao-api-key")
        print("=" * 60)

    # Load config
    print("Loading config from: %s" % args.config)
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    # Override rounds if specified
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("HerdEffectRuleLLM Simulation (ByteDance Doubao)")
    print("=" * 60)
    print("Name: %s" % config.setting["name"])
    print("Total Rounds: %s" % config.setting["total_rounds"])
    print("Record Path: %s" % config.setting["record_path"])
    print("=" * 60 + "\n")

    # Create and run simulator
    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 60)
        print("Simulation Complete!")
        print("Total rounds executed: %d" % config.setting["total_rounds"])
        print("Results saved to: %s" % config.setting["record_path"])
        print("=" * 60)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
