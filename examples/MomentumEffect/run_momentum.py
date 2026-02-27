#!/usr/bin/env python3
"""
Run MomentumEffect Simulation

Demonstrates momentum trading anomaly (Jegadeesh & Titman 1993):
Past winners continue to outperform, past losers continue to underperform.

Usage:
    python examples/MomentumEffect/run_momentum.py -c configs/MomentumEffect/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("MomentumEffect")


async def run_simulation(config_path: str):
    """Run the momentum effect simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("MOMENTUM EFFECT SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Momentum Anomaly (Jegadeesh & Titman 1993)")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - MomentumTrader:    Buys winners, sells losers")
    logger.info("  - ContrarianTrader:  Mean reversion (opposing)")
    logger.info("  - IndexFund:         Passive baseline")
    logger.info("  - MarketMaker:       Liquidity provision")
    logger.info("  - TechnicalTrader:   MA crossover")
    logger.info("  - FundamentalTrader: Value anchor")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Momentum traders amplify trends")
    logger.info("  - Price momentum persists 3-12 months")
    logger.info("  - Eventually contrarians stabilize")
    logger.info("=" * 70)
    logger.info("Simulation: %s", config.setting["name"])
    logger.info("Rounds: %d", config.setting["total_rounds"])
    logger.info("Config: %s", config_path)
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
    logger.info("[3] Simulation Summary")
    logger.info("-" * 70)
    logger.info("Total rounds completed: %d", len(results))

    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Momentum Effect Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
