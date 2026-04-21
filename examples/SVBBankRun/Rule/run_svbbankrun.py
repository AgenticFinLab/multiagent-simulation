#!/usr/bin/env python
"""SVBBankRun Rule-Based Simulation Runner

March 2023 SVB collapse - $42B deposit outflow in one day triggered by social media panic

Usage:
    python examples/SVBBankRun/Rule/run_svbbankrun.py \
        -c configs/SVBBankRun/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run SVBBankRun Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/SVBBankRun/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("SVBBankRun Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: March 2023 SVB collapse - $42B deposit outflow in one day triggered by social media panic")
    print("Rounds:     %%s" %% config.setting["total_rounds"])
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
