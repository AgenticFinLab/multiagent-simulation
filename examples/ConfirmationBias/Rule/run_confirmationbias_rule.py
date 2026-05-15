#!/usr/bin/env python
"""ConfirmationBias Rule-Based Simulation Entry Point

Runs the confirmation bias simulation using deterministic rule-based agents.
All agents act on published {price, fundamental, deviation, round} market data.

Usage:
    python examples/ConfirmationBias/Rule/run_confirmationbias_rule.py \\
        -c configs/ConfirmationBias/Rule/simulation.yml

See Rule/explain.md for full design documentation.
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
    """Run the ConfirmationBias Rule simulation."""
    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("CONFIRMATION BIAS SIMULATION — Rule Variant")
    logger.info("=" * 70)
    logger.info("Config: %s", config_path)

    simulator = GeneralSimulator(config)
    await simulator.setup()
    results = await simulator.run()
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("Run analysis with:")
    logger.info(
        "  python examples/ConfirmationBias/Rule/analysis.py -c %s", config_path
    )
    logger.info("=" * 70)
    return results


def main() -> None:
    """Parse config and launch the ConfirmationBias Rule simulation."""
    parser = argparse.ArgumentParser(
        description="Run ConfirmationBias Rule-Based simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/Rule/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()
    asyncio.run(run_simulation(args.config))


if __name__ == "__main__":
    main()
