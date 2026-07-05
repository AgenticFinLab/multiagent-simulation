#!/usr/bin/env python
"""AsianFinancialCrisis Rule-Based Simulation Runner

1997 Asian financial crisis — hot money reversal + contagion cascade

Usage:
    python examples/AsianFinancialCrisis/Rule/run_asianfinancialcrisis_rule.py \\
        -c configs/AsianFinancialCrisis/Rule/simulation.yml
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
        description="Run AsianFinancialCrisis Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AsianFinancialCrisis/Rule/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("AsianFinancialCrisis Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: 1997 Asian Financial Crisis — hot money reversal + contagion")
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
