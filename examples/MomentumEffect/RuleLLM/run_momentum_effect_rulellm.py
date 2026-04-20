#!/usr/bin/env python
"""MomentumEffectRuleLLM Simulation Runner

Run hybrid Rule+LLM momentum effect investor simulation.
Each LLM agent follows explicit quantitative rules (embedded in system prompt)
alongside a rich persona description.

Usage:
    python examples/MomentumEffect/RuleLLM/run_momentum_effect_rulellm.py -c configs/MomentumEffect/RuleLLM/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required)
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run MomentumEffectRuleLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/MomentumEffect/RuleLLM/simulation.yml",
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
    print("MomentumEffectRuleLLM Simulation")
    print("=" * 60)
    print("Phenomenon: MomentumEffect with Rule-Guided LLM Decision-Making")
    print("Theory: Market Microstructure, Kirilenko et al. (2017)")
    print("Agents: HFT, Market Maker, Algorithmic Trader,")
    print("        Stop-Loss Trader, Fundamental Trader  (all Rule+LLM hybrid)")
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
