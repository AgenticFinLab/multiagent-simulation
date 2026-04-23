#!/usr/bin/env python3
"""
Run EquityPremium Simulation

Demonstrates equity premium puzzle with myopic loss aversion.

Usage:
    python examples/EquityPremium/Rule/run_equity_premium.py -c configs/EquityPremium/Rule/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("EquityPremium")


async def run_simulation(config_path: str):
    """Run the equity premium simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("EQUITY PREMIUM PUZZLE SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Stocks return ~6% more than bonds historically")
    logger.info("Theory: Mehra & Prescott (1985), Benartzi & Thaler (1995)")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - MyopicLossAverse:  Evaluates frequently, demands high premium")
    logger.info("  - LongTermInvestor:  Evaluates infrequently, more stocks")
    logger.info("  - RationalInvestor:  Expected utility maximizer")
    logger.info("  - RiskAverseSaver:   Prefers bonds")
    logger.info("  - InstitutionalInvestor: Balanced allocation")
    logger.info("")
    logger.info("Myopic Loss Aversion Mechanism:")
    logger.info("  1. Frequent evaluation → stocks look volatile")
    logger.info("  2. Loss aversion (λ=2.25) → losses hurt more")
    logger.info("  3. Combined effect → demand high equity premium")
    logger.info("  4. Long-term investors see smoother returns")
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
    parser = argparse.ArgumentParser(description="Equity Premium Puzzle Simulation")
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
