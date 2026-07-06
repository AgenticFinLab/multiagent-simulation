#!/usr/bin/env python
"""AsianFinancialCrisis RuleLLM Simulation Runner

1997 Asian financial crisis with LLM agents using rule-embedded prompts.

Usage:
    python examples/AsianFinancialCrisis/RuleLLM/run_asianfinancialcrisis_rulellm.py \\
        -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run AsianFinancialCrisis RuleLLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AsianFinancialCrisis/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("AsianFinancialCrisis Simulation - RuleLLM Hybrid Agents")
    print("=" * 70)
    print("Phenomenon: 1997 Asian Financial Crisis — LLM with embedded rules")
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
