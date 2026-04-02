#!/usr/bin/env python3
"""
Run VolatilityClusteringLLM Simulation

Demonstrates GARCH-like volatility clustering through LLM-powered
heterogeneous agent interactions.

Usage:
    python examples/VolatilityClustering/LLM/run_volatility_llm.py -c configs/VolatilityClustering/LLM/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("VolatilityClusteringLLM")


async def run_simulation(config_path: str):
    """Run the LLM-based volatility clustering simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("VOLATILITY CLUSTERING LLM SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: GARCH-like volatility persistence")
    logger.info("Theory: Heterogeneous Agent Models (HAM)")
    logger.info("")
    logger.info("LLM Investor Types:")
    logger.info("  - LLMFundamentalist: Slow mean reversion (stabilizing, delayed)")
    logger.info("  - LLMTrendFollower:  Fast momentum, vol-sensitive (destabilizing)")
    logger.info("  - LLMNoiseTrader:    Random liquidity (neutral)")
    logger.info("  - LLMSlowAdapter:    Conservative, slow (weak stabilizing)")
    logger.info("  - LLMVolatilityTrader: Trades vol regime (weak stabilizing)")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Large returns → High volatility → More aggressive trend trading")
    logger.info("  - Volatility clusters in time (GARCH effect)")
    logger.info("  - LLMs respond to volatility in prompts")
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
    logger.info(
        "  python examples/VolatilityClustering/LLM/analysis.py -c %s", config_path
    )
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Volatility Clustering LLM Simulation: GARCH-like Dynamics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LLM Investor Types:
  - LLMFundamentalist:   Slow mean reversion (stabilizing, delayed)
  - LLMTrendFollower:    Fast momentum, vol-sensitive (destabilizing)
  - LLMNoiseTrader:      Random liquidity (neutral)
  - LLMSlowAdapter:      Conservative, slow (weak stabilizing)
  - LLMVolatilityTrader: Trades vol regime (weak stabilizing)

Example:
    python examples/VolatilityClustering/LLM/run_volatility_llm.py -c configs/VolatilityClustering/LLM/simulation.yml
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
