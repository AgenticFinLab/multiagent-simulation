#!/usr/bin/env python
"""ArchegosCollapse Rule-Based Simulation Runner

March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales

Usage:
    python examples/ArchegosCollapse/Rule/run_archegsoscollapse.py \
        -c configs/ArchegosCollapse/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run ArchegosCollapse Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ArchegosCollapse/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("ArchegosCollapse Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales")
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
