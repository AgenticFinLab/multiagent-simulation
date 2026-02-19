"""MASim Demo - Topology-Driven Message Passing

Demonstrates topology-driven message passing architecture:
- All players are equal - topology defines communication targets
- Coordinator broadcasts to connected players
- Players receive, process, and respond back

Architecture:
    ┌─────────┐  broadcast   ┌─────────┐   ┌─────────┐
    │ Coord   │ ───────────► │Player 1 │   │Player 2 │
    └────┬────┘              └────┬────┘   └────┬────┘
         │                        │             │
         │  ◄──── send ───────────┘             │
         │  ◄──────────── send ─────────────────┘

Usage:
    python examples/Demo/run_demo.py -c configs/Demo/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


# Configure logging
setup_logging()
logger = logging.getLogger("Demo")


# =============================================================================
# Main Entry Point
# =============================================================================


async def run_simulation(config_path: str):
    """Run the simple coordinator demo."""

    # Load YAML and build SimulationConfig directly
    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 60)
    logger.info("MASim Demo - Topology-Driven Message Passing")
    logger.info("=" * 60)
    logger.info("Simulation: %s", config.setting["name"])
    logger.info("Rounds: %d", config.setting["total_rounds"])
    logger.info("Config: %s", config_path)
    logger.info("")
    logger.info("Architecture: Topology-driven message passing")

    # Create simulator
    simulator = GeneralSimulator(config)

    # Setup: creates all Ray actors from config
    logger.info("")
    logger.info("[1] Setting up simulation...")
    await simulator.setup()
    logger.info("    Players: %s", list(config.players.keys()))

    # Run: executes all rounds
    logger.info("")
    logger.info("[2] Running simulation...")
    results = await simulator.run()

    # Report results
    logger.info("")
    logger.info("-" * 60)
    logger.info("[3] Results")
    logger.info("-" * 60)

    for i, round_result in enumerate(results, 1):
        logger.info("Round %d:", i)
        turn_results = round_result["turn_results"]
        for player_id, turn_result in turn_results.items():
            if turn_result and hasattr(turn_result, "final_action"):
                action = turn_result.final_action
                logger.info(
                    "    %s: %s - %s", player_id, action.action_type, action.payload
                )

    # Shutdown: cleans up Ray actors
    logger.info("")
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 60)
    logger.info("Simulation Complete!")
    logger.info("=" * 60)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MASim Demo: Topology-Driven Message Passing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python examples/Demo/run_demo.py -c configs/Demo/simulation.yml
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
