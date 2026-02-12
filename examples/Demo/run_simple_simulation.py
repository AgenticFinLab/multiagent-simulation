"""
Simple Price Averaging Simulation using MASim Framework.

This demo shows how to use GeneralSimulator from the masim framework.
The simulator handles all Ray actor management and persona creation automatically.

Simulation flow (10 rounds):
1. Market (Conductor) broadcasts current average price to all investors
2. Each investor updates: local_price += avg_price * random(-0.1, 0.1)
3. Each investor submits new local_price to market
4. Market calculates new average from all submissions
5. Repeat

Usage:
    cd /path/to/multiagent-simulation
    python examples/Demo/run_simple_simulation.py -c configs/Demo/simulation.yml
"""

import argparse
import asyncio
import logging
from typing import Any, Dict

import ray

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
    """Run the demo simulation using the framework."""

    # Load YAML and build SimulationConfig directly (keys match fields)
    yaml_config = load_config(config_path)
    sim_config = SimulationConfig(**yaml_config)

    logger.info("=" * 60)
    logger.info("Simple Price Averaging Simulation (MASim Framework)")
    logger.info("=" * 60)
    logger.info("Simulation: %s", sim_config.setting["name"])
    logger.info("Rounds: %d", sim_config.setting["total_rounds"])
    logger.info("Config: %s", config_path)

    # Create simulator - uses GeneralSimulator directly
    simulator = GeneralSimulator(sim_config)

    # Setup: creates all Ray actors from config
    logger.info("[1] Setting up simulation...")
    await simulator.setup()
    logger.info("    Actor prefix: %s", sim_config.setting["name"])
    logger.info("    Players: %d", len(simulator._player_persona_handles))
    logger.info("    Dashboard: %s", "http://127.0.0.1:8265")

    # Run: executes all rounds
    logger.info("[2] Running simulation...")
    results = await simulator.run()

    # Report results
    logger.info("-" * 60)
    logger.info("[3] Results")
    logger.info("-" * 60)

    final_round = results[-1]
    final_avg = final_round["coordination"]["decision"]["parameters"]["avg_price"]
    logger.info("    Final average price: %s", final_avg)

    # Get final player states
    for player_id, handle in simulator._player_persona_handles.items():
        state = ray.get(handle.get_state_snapshot.remote())
        local_price = state["custom_state"]["local_price"]
        logger.info("        %s: local_price = %.2f", player_id, local_price)

    # Shutdown: cleans up Ray actors
    logger.info("[4] Shutting down...")
    await simulator.shutdown()

    logger.info("=" * 60)
    logger.info("Simulation Complete!")
    logger.info("=" * 60)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MASim Demo: Simple Price Averaging Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python examples/Demo/run_simple_simulation.py -c configs/Demo/simulation.yml
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
