#!/usr/bin/env python
"""FlashCrash2010 RuleLLM Simulation Runner

Run the 2010 Flash Crash simulation with LLM-driven agents.

This simulation models the May 6, 2010 flash crash using LLM-powered agents
with personas based on Kirilenko et al. (2017) findings.

Usage:
    python examples/FlashCrash2010/LLM/run_flashcrash2010_rulellm.py \
        -c configs/FlashCrash2010/LLM/simulation.yml

Expected Runtime: ~10-15 minutes for 200 rounds (depends on API latency)
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
        description="Run FlashCrash2010 RuleLLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/LLM/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("FlashCrash2010 Simulation - LLM Agents")
    print("=" * 70)
    print("Phenomenon: 2010 Flash Crash (May 6, 2010)")
    print("Theory:     Kirilenko et al. (2017) - HFT Liquidity Dynamics")
    print("Agents:     LLM-driven HFT Market Makers, Momentum Chasers,")
    print("            Fundamental Traders, Stop-Loss Traders, Noise Traders")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("Note:       LLM API calls will slow down simulation")
    print("=" * 70 + "\n")
    
    simulator = GeneralSimulator(config)
    
    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 70)
        print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
