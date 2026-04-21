#!/usr/bin/env python
"""BlackMonday1987 Rule-Based Simulation Runner

October 19, 1987 stock market crash - Dow fell 22.6% in one day

Usage:
    python examples/BlackMonday1987/Rule/run_blackmonday1987.py \
        -c configs/BlackMonday1987/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run BlackMonday1987 Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/BlackMonday1987/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("BlackMonday1987 Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: October 19, 1987 stock market crash - Dow fell 22.6% in one day")
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
