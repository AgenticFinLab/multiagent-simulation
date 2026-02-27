#!/usr/bin/env python3
"""
Run LiquidityDryup Simulation

Demonstrates liquidity dry-up dynamics with market maker inventory model.

Usage:
    python examples/LiquidityDryup/run_liquidity.py -c configs/LiquidityDryup/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("LiquidityDryup")


async def run_simulation(config_path: str):
    """Run the liquidity dry-up simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("LIQUIDITY DRY-UP SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Market maker withdrawal creates illiquidity spirals")
    logger.info("Theory: Grossman & Miller (1988), Amihud & Mendelson (1986)")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - MarketMaker:        Provides liquidity, withdraws in stress")
    logger.info("  - LiquidityDemander:  Takes liquidity, suffers from dry-up")
    logger.info("  - Arbitrageur:        Profits from mispricings")
    logger.info("  - ValueInvestor:      Patient buyer during extreme mispricings")
    logger.info("  - ForcedSeller:       Must sell regardless of conditions")
    logger.info("")
    logger.info("Liquidity Spiral:")
    logger.info("  1. Stress event → Market makers reduce quotes")
    logger.info("  2. Reduced liquidity → Higher price impact")
    logger.info("  3. Higher impact → More MM withdrawal")
    logger.info("  4. Cycle continues until stabilizing forces arrive")
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
    logger.info("Total rounds: %d", len(results))

    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Liquidity Dry-up Simulation")
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
