#!/usr/bin/env python
"""GFC2008 Rule-Based Simulation Runner

2007-2009 financial crisis - Housing bubble burst triggered global recession

Usage:
    python examples/GFC2008/Rule/run_gfc2008.py \
        -c configs/GFC2008/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run GFC2008 Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/GFC2008/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("GFC2008 Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: 2007-2009 financial crisis - Housing bubble burst triggered global recession")
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
