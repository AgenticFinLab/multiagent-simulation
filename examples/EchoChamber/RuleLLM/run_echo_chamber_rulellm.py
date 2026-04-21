#!/usr/bin/env python3
"""
Run EchoChamberRuleLLM Simulation

Demonstrates polarization by homophily using hybrid Rule+LLM agents.
Each LLM agent follows explicit quantitative rules (embedded in system prompt)
alongside a rich persona description.

Usage:
    python examples/EchoChamber/RuleLLM/run_echo_chamber_rulellm.py \
        -c configs/EchoChamber/RuleLLM/simulation.yml

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

    parser = argparse.ArgumentParser(description="Run EchoChamberRuleLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EchoChamber/RuleLLM/simulation.yml",
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set! LLM agents will not function.")

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("EchoChamberRuleLLM Simulation")
    print("=" * 60)
    print("Phenomenon: Echo Chamber Polarization with Rule-Guided LLM Decision-Making")
    print("Theory: Sunstein (2001) + Asch (1951) + Isenberg (1986) + Pariser (2011)")
    print("Agents: Ideologue, Conformist, CriticalThinker,")
    print("        BridgeBuilder, PassiveFollower  (all Rule+LLM hybrid)")
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
