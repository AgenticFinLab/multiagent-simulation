#!/usr/bin/env python3
"""
Run ShortSqueeze Simulation

Demonstrates short squeeze dynamics with supply-demand imbalance.

Usage:
    python examples/ShortSqueeze/Rule/run_short_squeeze.py -c configs/ShortSqueeze/Rule/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("ShortSqueeze")


async def run_simulation(config_path: str):
    """Run the short squeeze simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("SHORT SQUEEZE SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Heavily shorted stock rises, forcing short covering")
    logger.info("Example: GameStop 2021")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - ShortSeller:        Borrows and sells, must cover on losses")
    logger.info("  - MomentumBuyer:      Buys on upward momentum")
    logger.info("  - ValueInvestor:      Buys when undervalued")
    logger.info("  - RetailTrader:       Can trigger initial squeeze")
    logger.info("  - InstitutionalHolder: Large passive holder")
    logger.info("")
    logger.info("Squeeze Mechanism:")
    logger.info("  1. High short interest creates vulnerability")
    logger.info("  2. Buying pressure starts price increase")
    logger.info("  3. Shorts face margin pressure → forced covering")
    logger.info("  4. Covering = buying → price rises more")
    logger.info("  5. Positive feedback loop until shorts exhausted")
    logger.info("=" * 70)
    logger.info("Simulation: %s", config.setting["name"])
    logger.info("Rounds: %d", config.setting["total_rounds"])
    logger.info("")

    simulator = GeneralSimulator(config)

    logger.info("[1] Setting up simulation...")
    await simulator.setup()
    logger.info("    Players: %s", list(config.players.keys()))

    logger.info("")
    logger.info("[2] Running simulation (%d rounds)...", config.setting["total_rounds"])
    logger.info("-" * 70)

    results = await simulator.run()

    logger.info("-" * 70)
    logger.info("")
    logger.info("[3] Simulation Complete!")
    logger.info("Total rounds: %d", config.setting["total_rounds"])

    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Short Squeeze Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_simulation(args.config))
