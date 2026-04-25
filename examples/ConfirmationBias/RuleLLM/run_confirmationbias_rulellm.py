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
import logging
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from masim.runner import SimulationRunner
from masim.utils.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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

    config = load_config(args.config)
    logger.info("Starting ConfirmationBias RuleLLM simulation: %s", args.config)

    runner = SimulationRunner(config)
    runner.run()

    logger.info(
        "Simulation complete. Records saved to: %s",
        config["setting"]["record_path"],
    )


if __name__ == "__main__":
    main()
