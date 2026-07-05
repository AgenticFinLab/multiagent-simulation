#!/usr/bin/env python
"""AsianFinancialCrisis LLM Simulation Runner

1997 Asian financial crisis with LLM-driven behavioral agents.

Usage:
    python examples/AsianFinancialCrisis/LLM/run_asianfinancialcrisis_llm.py \\
        -c configs/AsianFinancialCrisis/LLM/simulation.yml
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
        description="Run AsianFinancialCrisis LLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AsianFinancialCrisis/LLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("AsianFinancialCrisis Simulation - LLM Behavioral Agents")
    print("=" * 70)
    print("Phenomenon: 1997 Asian Financial Crisis — LLM behavioral personas")
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
