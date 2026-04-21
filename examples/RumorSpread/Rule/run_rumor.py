#!/usr/bin/env python3
"""
Run RumorSpread Simulation

Demonstrates rumor propagation through serial transmission with distortion
and amplification, using heterogeneous social agents.

Phenomenon: Rumor Spread
    Rumors propagate through populations via serial transmission, with each
    retelling introducing distortion and amplification. Belief in unverified
    information spreads faster than corrections, producing collective error.

Theory: Allport & Postman (1947), Bordia & Rosnow (1998),
        DiFonzo & Bordia (2007), Shibutani (1966)

Usage:
    python examples/RumorSpread/Rule/run_rumor.py -c configs/RumorSpread/Rule/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("RumorSpread")


async def run_simulation(config_path: str):
    """Run the rumor spread simulation."""

    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("RUMOR SPREAD SIMULATION")
    logger.info("=" * 70)
    logger.info("Phenomenon: Rumor propagation through serial transmission")
    logger.info("Theory: Allport & Postman (1947) — Leveling, Sharpening, Assimilation")
    logger.info("")
    logger.info("Agent Types:")
    logger.info("  - GullibleSpreader:     Uncritical transmitter (DESTABILIZING)")
    logger.info("  - DistortingRelayer:    Serial distortion (DESTABILIZING)")
    logger.info("  - SkepticalEvaluator:   Critical assessor (STABILIZING)")
    logger.info("  - FactChecker:          Active debunker (STRONGLY STABILIZING)")
    logger.info("  - UninformedBystander:  Random participant (NEUTRAL)")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Initial rumor seed → some agents believe and relay")
    logger.info("  - Leveling: details lost in retelling")
    logger.info("  - Sharpening: salient details exaggerated")
    logger.info("  - Corrections spread slower than rumors")
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
    logger.info("  python examples/RumorSpread/Rule/analysis.py -c %s", config_path)
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="RumorSpread Simulation: Rumor Propagation with Distortion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent Types:
  - GullibleSpreader:     Uncritical transmitter (rumor amplifier)
  - DistortingRelayer:    Sharpening + leveling during relay
  - SkepticalEvaluator:   Critical assessor (correction source)
  - FactChecker:          Active debunker (strongest correction)
  - UninformedBystander:  Random low-engagement participant

Example:
    python examples/RumorSpread/Rule/run_rumor.py -c configs/RumorSpread/Rule/simulation.yml
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
