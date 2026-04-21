#!/usr/bin/env python
"""Volmageddon Rag Simulation Runner

February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading

Usage:
    python examples/Volmageddon/Rag/run_volmageddon_rag.py \
        -c configs/Volmageddon/Rag/simulation.yml
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
        description="Run Volmageddon Rag Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/Volmageddon/Rag/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("Volmageddon Simulation - Rag Agents")
    print("=" * 70)
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
