#!/usr/bin/env python3
"""
Run EchoChamber LLM Simulation

Demonstrates polarization by homophily using LLM-powered agents.

Usage:
    python examples/EchoChamber/LLM/run_echo_chamber_llm.py -c configs/EchoChamber/LLM/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("EchoChamberLLM")


async def run_simulation(config_path: str):
    """Run the echo chamber LLM simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("ECHO CHAMBER LLM SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Polarization by homophily with LLM-driven agents")
    logger.info("Theory: Sunstein (2001), Pariser (2011)")
    logger.info("")
    logger.info("Agent Types:")
    logger.info("  - LLMIdeologue:          Strong opinion holder (DESTABILIZING)")
    logger.info("  - LLMConformist:         Group opinion adopter (DESTABILIZING)")
    logger.info("  - LLMCriticalThinker:    Evidence evaluator (STABILIZING)")
    logger.info("  - LLMBridgeBuilder:      Cross-group engager (STRONGLY STABILIZING)")
    logger.info("  - LLMPassiveBystander:   Low-engagement participant (NEUTRAL)")
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
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="EchoChamber LLM Simulation",
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
