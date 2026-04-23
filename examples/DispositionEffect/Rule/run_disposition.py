#!/usr/bin/env python3
"""
Run DispositionEffect Simulation

Demonstrates the disposition effect (Shefrin & Statman 1985):
- Investors sell winners too early (realize gains)
- Investors hold losers too long (reluctant to realize losses)

Usage:
    python examples/DispositionEffect/Rule/run_disposition.py -c configs/DispositionEffect/Rule/simulation.yml
"""

import argparse
import asyncio
import logging
import os
import shutil

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("DispositionEffect")


async def run_simulation(config_path: str):
    """Run the disposition effect simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    # Clear stale records from any previous run
    record_path = yaml_config["setting"]["record_path"]
    if os.path.exists(record_path):
        shutil.rmtree(record_path)
        logger.info(f"Cleared old records: {record_path}")  # pylint: disable=logging-fstring-interpolation
    logger.info("=" * 70)
    logger.info("DISPOSITION EFFECT SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Disposition Effect (Shefrin & Statman 1985)")
    logger.info("Theory: Prospect Theory (Kahneman & Tversky 1979)")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - DispositionInvestor: Sells winners, holds losers")
    logger.info("  - RationalInvestor:    Baseline expected utility")
    logger.info("  - TaxAwareInvestor:    Tax loss harvesting")
    logger.info("  - IndexHolder:         Passive buy-and-hold")
    logger.info("  - InstitutionalInvestor: Professional (less biased)")
    logger.info("=" * 70)

    simulator = GeneralSimulator(config)

    await simulator.setup()
    results = await simulator.run()
    await simulator.shutdown()

    logger.info("Simulation Complete!")
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Disposition Effect Simulation")
    parser.add_argument("-c", "--config", type=str, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_simulation(args.config))
