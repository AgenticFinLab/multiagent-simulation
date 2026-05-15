#!/usr/bin/env python
"""ConfirmationBias RuleLLM Simulation Entry Point

Runs the confirmation bias simulation using RuleLLM hybrid agents.
LLM agents are guided by explicit decision rules via dual-section prompts
(== PERSONA == + == DECISION RULES ==).

Usage:
    python examples/ConfirmationBias/RuleLLM/run_confirmationbias_rulellm.py \\
        -c configs/ConfirmationBias/RuleLLM/simulation.yml

See RuleLLM/explain.md for full design documentation.
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging

setup_logging()
logger = logging.getLogger("ConfirmationBias")


async def run_simulation(config_path: str):
    """Run the ConfirmationBias RuleLLM simulation."""
    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)
    logger.info("=" * 70)
    logger.info("CONFIRMATIONBIAS SIMULATION — RuleLLM Variant")
    logger.info("=" * 70)
    logger.info("Config: %s", config_path)
    simulator = GeneralSimulator(config)
    await simulator.setup()
    results = await simulator.run()
    await simulator.shutdown()
    logger.info("=" * 70)
    logger.info("Simulation Complete!")
    logger.info("=" * 70)
    return results


def main() -> None:
    """Parse config and launch the ConfirmationBias RuleLLM simulation."""
    parser = argparse.ArgumentParser(
        description="Run ConfirmationBias RuleLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/RuleLLM/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()
    asyncio.run(run_simulation(args.config))


if __name__ == "__main__":
    main()
