#!/usr/bin/env python
"""ConfirmationBias LLM Simulation Entry Point

Runs the confirmation bias simulation using LLM-driven agents.
Agents receive {price, fundamental, deviation, round} market data
and generate buy/sell/hold decisions via language model calls.

Usage:
    python examples/ConfirmationBias/LLM/run_confirmationbias_llm.py \\
        -c configs/ConfirmationBias/LLM/simulation.yml

See LLM/explain.md for full design documentation.
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
    """Parse config and launch the ConfirmationBias LLM simulation."""
    parser = argparse.ArgumentParser(description="Run ConfirmationBias LLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/LLM/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger.info("Starting ConfirmationBias LLM simulation: %s", args.config)

    runner = SimulationRunner(config)
    runner.run()

    logger.info(
        "Simulation complete. Records saved to: %s",
        config["setting"]["record_path"],
    )


if __name__ == "__main__":
    main()
