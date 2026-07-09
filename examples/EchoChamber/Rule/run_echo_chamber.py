#!/usr/bin/env python3
"""
Run EchoChamber Simulation

Demonstrates polarization by homophily where like-minded reinforcement
drives extremity, using heterogeneous social agents.

Phenomenon: Echo Chamber Polarization
    Like-minded individuals reinforce each other's views through homophilic
    interaction, producing group polarization, where group members converge
    on positions more extreme than any individual initially held.

Theory: Sunstein (2001), Pariser (2011), Moscovici & Zavalloni (1969),
        Isenberg (1986)

Usage:
    python -m examples.EchoChamber.Rule.run_echo_chamber -c configs/EchoChamber/Rule/simulation.yml
"""

import argparse
import asyncio
import logging

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


setup_logging()
logger = logging.getLogger("EchoChamber")


async def run_simulation(config_path: str, steps: int | None = None):
    """Run the echo chamber polarization simulation."""

    yaml_config = load_config(config_path)
    if steps is not None:
        if steps < 1:
            raise ValueError("steps must be at least 1")
        yaml_config["setting"]["total_rounds"] = steps
    config = SimulationConfig(**yaml_config)

    logger.info("=" * 70)
    logger.info("ECHO CHAMBER POLARIZATION SIMULATION")
    logger.info("=" * 70)
    logger.info(
        "Phenomenon: Polarization by homophily - like-minded reinforcement drives extremity"
    )
    logger.info(
        "Theory: Sunstein (2001) - Echo Chambers; Pariser (2011) - Filter Bubble"
    )
    logger.info("")
    logger.info("Agent Types:")
    logger.info("  - Ideologue:          Strong views amplifier (DESTABILIZING)")
    logger.info("  - Conformist:         Group opinion adopter (DESTABILIZING)")
    logger.info("  - CriticalThinker:    Evidence evaluator (STABILIZING)")
    logger.info("  - BridgeBuilder:      Cross-group engager (STRONGLY STABILIZING)")
    logger.info("  - PassiveFollower:    Low-engagement drifter (NEUTRAL)")
    logger.info("")
    logger.info("Expected Behavior:")
    logger.info("  - Initial moderate opinions -> some agents amplify in-group views")
    logger.info("  - Conformists reinforce homophily -> cluster formation")
    logger.info("  - Cluster separation grows -> echo chamber emerges")
    logger.info("  - BridgeBuilders and CriticalThinkers resist polarization")
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
    logger.info("  python -m examples.EchoChamber.Rule.analysis -c %s", config_path)
    logger.info("=" * 70)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="EchoChamber Simulation: Polarization by Homophily",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent Types:
  - Ideologue:          Strong views amplifier (polarization driver)
  - Conformist:         Group opinion adopter (homophily reinforcer)
  - CriticalThinker:    Evidence evaluator (correction source)
  - BridgeBuilder:      Cross-group engager (strongest depolarizer)
  - PassiveFollower:    Low-engagement drifter (baseline)

Example:
    python -m examples.EchoChamber.Rule.run_echo_chamber -c configs/EchoChamber/Rule/simulation.yml
""",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Override total_rounds for a short smoke or calibration run",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_simulation(args.config, args.steps))
