#!/usr/bin/env python3
"""
Run MarketCrash Simulation

Demonstrates market crash dynamics through forced deleveraging
and liquidity spiral mechanisms.

Usage:
    python examples/MarketCrash/run_crash.py -c configs/MarketCrash/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("MarketCrash")


async def run_simulation(config_path: str):
    """Run the market crash simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("MARKET CRASH SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Rapid price decline with liquidity evaporation")
    logger.info("Theory: Minsky Moment, Liquidity Spiral")
    logger.info("")
    logger.info("Investor Types:")
    logger.info(
        "  - RiskParityFund:     Vol-targeting, forced deleverage (PROCYCLICAL)"
    )
    logger.info(
        "  - LeveragedHedgeFund: Margin-constrained, forced liquidation (PROCYCLICAL)"
    )
    logger.info("  - MarketMaker:        Liquidity provider, withdraws in stress")
    logger.info("  - PassiveInvestor:    Buy-and-hold (NEUTRAL)")
    logger.info("  - PanicSeller:        Loss-triggered selling (PROCYCLICAL)")
    logger.info("  - BottomFisher:       Contrarian crash buyer (STABILIZING)")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Initial shock → Volatility rises")
    logger.info("  - Risk parity funds forced to deleverage")
    logger.info("  - Hedge funds hit margin calls → Fire sales")
    logger.info("  - Market makers withdraw → Liquidity evaporates")
    logger.info("  - Crash accelerates until bottom fishers provide floor")
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
    logger.info("Run analysis with:")
    logger.info("  python examples/MarketCrash/analysis.py -c %s", config_path)
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Market Crash Simulation: Liquidity Spiral Dynamics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Investor Types:
  - RiskParityFund:     Volatility targeting, forced deleveraging
  - LeveragedHedgeFund: Margin-constrained, forced liquidation
  - MarketMaker:        Liquidity provider (withdraws in stress)
  - PassiveInvestor:    Buy-and-hold stability
  - PanicSeller:        Loss-triggered retail selling
  - BottomFisher:       Contrarian crash buyer

Example:
    python examples/MarketCrash/run_crash.py -c configs/MarketCrash/simulation.yml
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
