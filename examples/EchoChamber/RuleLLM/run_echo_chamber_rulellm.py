#!/usr/bin/env python3
"""
Run EchoChamberRuleLLM Simulation

Demonstrates polarization by homophily using hybrid Rule+LLM agents.
Each LLM agent follows explicit quantitative rules (embedded in system prompt)
alongside a rich persona description.

Usage:
    python examples/EchoChamber/RuleLLM/run_echo_chamber_rulellm.py -c configs/EchoChamber/RuleLLM/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required)
"""

import argparse
import asyncio
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


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
    parser.add_argument(
        "--record-path",
        type=str,
        default=None,
        help="Override the output directory (useful for a clean rerun).",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Initialize and shut down without consuming LLM API calls.",
    )
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set! LLM agents will not function.")

    yaml_config = load_config(args.config)
    if args.record_path:
        yaml_config["setting"]["record_path"] = args.record_path
        for player in yaml_config["players"].values():
            player.setdefault("config", {}).setdefault("extras", {})[
                "record_path"
            ] = args.record_path
            storage = player.setdefault("persona", {}).setdefault("proxy", {}).setdefault(
                "storage", {}
            )
            storage["record_path"] = args.record_path
            storage["checkpoint_dir"] = os.path.join(args.record_path, "checkpoints")
            player["persona"].setdefault("proxy", {}).setdefault("monitoring", {})[
                "record_path"
            ] = os.path.join(args.record_path, "monitoring")
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
        if args.setup_only:
            print("Setup-only validation passed; simulation rounds were skipped.")
        else:
            await simulator.run()
            print("\n" + "=" * 60)
            print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
            print("=" * 60)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
