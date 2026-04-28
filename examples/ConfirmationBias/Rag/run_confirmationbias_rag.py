#!/usr/bin/env python
"""ConfirmationBias Rag Simulation Entry Point

Runs the confirmation bias simulation using RAG-augmented LLM agents.
Agents retrieve relevant knowledge about cognitive biases from KnowledgeStore
before making decisions.

Usage:
    python examples/ConfirmationBias/Rag/run_confirmationbias_rag.py \\
        -c configs/ConfirmationBias/Rag/simulation.yml

See Rag/explain.md for full design documentation.
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging

setup_logging()
logger = logging.getLogger("ConfirmationBias")


async def run_simulation(config_path: str):
    """Run the ConfirmationBias Rag simulation."""
    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("CONFIRMATION BIAS SIMULATION — Rag Variant")
    logger.info("=" * 70)
    logger.info("Config: %s", config_path)

    simulator = GeneralSimulator(config)
    await simulator.setup()
    results = await simulator.run()
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)
    return results


def main() -> None:
    """Parse config and launch the ConfirmationBias Rag simulation."""
    parser = argparse.ArgumentParser(description="Run ConfirmationBias Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/Rag/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()
    asyncio.run(run_simulation(args.config))


if __name__ == "__main__":
    main()
