"""Herd Effect Simulation Runner

Demonstrates herd behavior in financial markets:
- 1 Market player that broadcasts prices and adjusts based on demand
- 5 Investors with different strategies

Usage:
    python examples/HerdEffect/Rule/run_herd.py -c configs/HerdEffect/Rule/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("HerdEffect")


async def run_simulation(config_path: str):
    """Run the herd effect simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("Herd Effect Simulation - Multi-Strategy Market")
    logger.info("=" * 70)
    logger.info("Simulation: %s", config.setting["name"])
    logger.info("Rounds: %d", config.setting["total_rounds"])
    logger.info("Config: %s", config_path)
    logger.info("")
    logger.info("Participants:")
    logger.info("  - 1 Market (price setter)")
    logger.info("  - 5 Investors (different strategies)")
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

    # Extract final market state (from last round's market result)
    # The results contain round data, we can analyze price history

    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Herd Effect Simulation: Multi-Strategy Market",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Investor Strategies:
  - Momentum:    Follows price trends (amplifies herd behavior)
  - Contrarian:  Goes against trends (stabilizing force)
  - RiskAverse:  Conservative, small adjustments
  - Aggressive:  Large positions, high risk tolerance
  - NoiseTrader: Random behavior, adds market noise

Example:
    python examples/HerdEffect/Rule/run_herd.py -c configs/HerdEffect/Rule/simulation.yml
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
