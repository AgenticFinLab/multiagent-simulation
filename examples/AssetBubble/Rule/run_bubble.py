#!/usr/bin/env python3
"""
Run AssetBubble Simulation

Demonstrates asset bubble formation through heterogeneous agent interactions.

Usage:
    python examples/AssetBubble/Rule/run_bubble.py -c configs/AssetBubble/Rule/simulation.yml
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("AssetBubble")


async def run_simulation(config_path: str):
    """Run the asset bubble simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("ASSET BUBBLE SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Asset price deviation from fundamental value")
    logger.info("Theory: Greater Fool Theory, Limits to Arbitrage")
    logger.info("")
    logger.info("Investor Types:")
    logger.info("  - MomentumSpeculator:  Chases trends, high leverage (DESTABILIZING)")
    logger.info(
        "  - RationalArbitrageur: Value investor, limited shorts (WEAK STABILIZING)"
    )
    logger.info("  - NoiseTrader:         Sentiment-driven herding (DESTABILIZING)")
    logger.info("  - FundamentalInvestor: Anchors to value (WEAK STABILIZING)")
    logger.info("  - LeveragedBuyer:      Amplified positions (STRONGLY DESTABILIZING)")
    logger.info("  - ConservativeHolder:  Long-term stable (VERY WEAK STABILIZING)")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Price rises above fundamental → Speculators chase")
    logger.info("  - Arbitrageurs try to short → But face limits")
    logger.info("  - Bubble builds until momentum exhausts")
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
    logger.info("Total rounds completed: %d", config.setting["total_rounds"])

    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("Run analysis with:")
    logger.info("  python examples/AssetBubble/Rule/analysis.py -c %s", config_path)
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Asset Bubble Simulation: Price Deviation from Fundamentals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Investor Types:
  - MomentumSpeculator:  Aggressive trend chaser (bubble driver)
  - RationalArbitrageur: Value-based short seller (limited)
  - NoiseTrader:         Sentiment/herd follower
  - FundamentalInvestor: Slow value anchor
  - LeveragedBuyer:      Margin-amplified positions
  - ConservativeHolder:  Long-term stability

Example:
    python examples/AssetBubble/Rule/run_bubble.py -c configs/AssetBubble/Rule/simulation.yml
""",
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
