#!/usr/bin/env python
"""LTCMCollapse Rule-Based Simulation Runner

August-September 1998 LTCM crisis - Russian default triggered liquidity crisis

Usage:
    python examples/LTCMCollapse/Rule/run_ltcmcollapse.py \
        -c configs/LTCMCollapse/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run LTCMCollapse Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/LTCMCollapse/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("LTCMCollapse Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: August-September 1998 LTCM crisis - Russian default triggered liquidity crisis")
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
