#!/usr/bin/env python
"""HindsightBias RAG-LLM Simulation Runner

Hindsight bias: RAG-augmented LLM agents with research-enriched hindsight reasoning

Usage:
    python examples/HindsightBias/Rag/run_hindsightbias_rag.py \
        -c configs/HindsightBias/Rag/simulation.yml
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

    parser = argparse.ArgumentParser(description="Run HindsightBias RAG-LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/HindsightBias/Rag/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("HindsightBias Simulation - RAG-LLM Agents")
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
