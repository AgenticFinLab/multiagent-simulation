#!/usr/bin/env python3
"""
Run ReversalEffect Simulation

Demonstrates long-term mean reversion dynamics.

Usage:
    python examples/ReversalEffect/Rule/run_reversal.py -c configs/ReversalEffect/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("ReversalEffect")


async def run_simulation(config_path: str):
    """Run the reversal effect simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("REVERSAL EFFECT SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Past losers outperform past winners (3-5 year horizon)")
    logger.info("Theory: De Bondt & Thaler (1985), Overreaction Hypothesis")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - ContrarianInvestor:  Buys losers, sells winners (KEY)")
    logger.info("  - MomentumInvestor:    Short-term trend following")
    logger.info("  - OverconfidentTrader: Overreacts to news")
    logger.info("  - NoiseTrader:         Random liquidity")
    logger.info("  - ValueInvestor:       Slow fundamental investor")
    logger.info("  - IndexTracker:        Passive benchmark")
    logger.info("")
    logger.info("Reversal Mechanism:")
    logger.info("  1. News arrives → Overconfident traders overreact")
    logger.info("  2. Price deviates from fundamental")
    logger.info("  3. Contrarians recognize mispricing")
    logger.info("  4. Gradual reversal to fundamental (long horizon)")
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
    parser = argparse.ArgumentParser(description="Reversal Effect Simulation")
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
