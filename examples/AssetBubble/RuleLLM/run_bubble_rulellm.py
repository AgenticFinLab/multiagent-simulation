#!/usr/bin/env python
"""AssetBubbleRuleLLM Simulation Runner

Run hybrid Rule+LLM bubble investor simulation.
Each LLM agent follows explicit quantitative rules (embedded in system prompt)
alongside a rich persona description.

Usage:
    python examples/AssetBubble/RuleLLM/run_bubble_rulellm.py -c configs/AssetBubble/RuleLLM/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required)
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run AssetBubbleRuleLLM Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default="configs/AssetBubble/RuleLLM/simulation.yml"
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set! LLM investors will not function.")

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("AssetBubbleRuleLLM Simulation")
    print("=" * 60)
    print("Phenomenon: Asset Bubble with Rule-Guided LLM Decision-Making")
    print("Theory: Greater Fool Theory + Explicit Quantitative Rules")
    print("Agents: Momentum Speculator, Rational Arbitrageur, Noise Trader,")
    print("        Value Investor, Leveraged Buyer  (all Rule+LLM hybrid)")
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
