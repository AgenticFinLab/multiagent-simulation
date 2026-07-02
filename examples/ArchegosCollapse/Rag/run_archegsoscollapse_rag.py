#!/usr/bin/env python
"""ArchegosCollapse Rag Simulation Runner

March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales

Usage:
    python examples/ArchegosCollapse/Rag/run_archegsoscollapse_rag.py \
        -c configs/ArchegosCollapse/Rag/simulation.yml
"""

import argparse
import asyncio

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    load_dotenv()
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run ArchegosCollapse Rag Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ArchegosCollapse/Rag/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("ArchegosCollapse Simulation - Rag Agents")
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
