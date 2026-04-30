#!/usr/bin/env python
"""EuropeanDebtCrisis RuleLLM Simulation Runner

European Sovereign Debt Crisis (2010-2012): rule+LLM hybrid bond market agents

Usage:
    python examples/EuropeanDebtCrisis/RuleLLM/run_europeandebtcrisis_rulellm.py \
        -c configs/EuropeanDebtCrisis/RuleLLM/simulation.yml
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

    parser = argparse.ArgumentParser(description="Run EuropeanDebtCrisis RuleLLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EuropeanDebtCrisis/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("EuropeanDebtCrisis Simulation - RuleLLM Agents")
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
