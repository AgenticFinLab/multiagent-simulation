#!/usr/bin/env python3
"""
Run FlashCrash Simulation

Demonstrates flash crash dynamics with liquidity-sensitive pricing.

Usage:
    python examples/FlashCrash/run_flash_crash.py -c configs/FlashCrash/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("FlashCrash")


async def run_simulation(config_path: str):
    """Run the flash crash simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("FLASH CRASH SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Extreme rapid price decline with liquidity evaporation")
    logger.info("Theory: Market Microstructure, Kirilenko et al. (2017)")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - HighFrequencyTrader: Rapid momentum, can trigger cascades")
    logger.info("  - MarketMaker:         Provides liquidity, withdraws in stress")
    logger.info("  - AlgorithmicTrader:   Trend-following algorithm")
    logger.info("  - StopLossTrader:      Triggered selling at thresholds")
    logger.info("  - FundamentalTrader:   Stabilizing, buys during crash")
    logger.info("  - RetailTrader:        Slow, delayed reaction")
    logger.info("")
    logger.info("Flash Crash Mechanism:")
    logger.info("  1. Initial selling pressure")
    logger.info("  2. HFTs detect momentum → start selling")
    logger.info("  3. Stop-losses triggered → cascade")
    logger.info("  4. Market makers withdraw → liquidity vacuum")
    logger.info("  5. Price collapses rapidly")
    logger.info("  6. Fundamental traders buy → recovery")
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
    parser = argparse.ArgumentParser(description="Flash Crash Simulation")
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
