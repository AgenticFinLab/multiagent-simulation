#!/usr/bin/env python
"""AsianFinancialCrisis RAG-LLM Simulation Runner

1997 Asian Financial Crisis: RAG-augmented LLM agents with domain knowledge

Usage:
    python examples/AsianFinancialCrisis/Rag/run_asianfinancialcrisis_rag.py \
        -c configs/AsianFinancialCrisis/Rag/simulation.yml
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(description="Run AsianFinancialCrisis RAG-LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AsianFinancialCrisis/Rag/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("AsianFinancialCrisis Simulation - RAG-LLM Agents")
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
