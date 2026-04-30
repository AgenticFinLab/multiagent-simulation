#!/usr/bin/env python
"""SouthSeaBubble RAG-LLM Simulation Runner

1720 South Sea Company bubble: RAG-augmented LLM agents with narrative premium tracking

Usage:
    python examples/SouthSeaBubble/Rag/run_southseabubble_rag.py \
        -c configs/SouthSeaBubble/Rag/simulation.yml
"""

import argparse
import asyncio

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(description="Run SouthSeaBubble RAG-LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/SouthSeaBubble/Rag/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("SouthSeaBubble Simulation - RAG-LLM Agents")
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
