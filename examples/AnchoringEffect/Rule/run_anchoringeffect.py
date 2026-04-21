#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Runner

Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery

Usage:
    python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run AnchoringEffect Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AnchoringEffect/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\n" + "=" * 70)
    print("AnchoringEffect Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery")
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
