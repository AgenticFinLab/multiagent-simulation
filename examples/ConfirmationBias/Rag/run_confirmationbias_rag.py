#!/usr/bin/env python
"""ConfirmationBias Rag Simulation Entry Point

Runs the confirmation bias simulation using RAG-augmented LLM agents.
Agents retrieve relevant knowledge about cognitive biases from KnowledgeStore
before making decisions.

Usage:
    python examples/ConfirmationBias/Rag/run_confirmationbias_rag.py \\
        -c configs/ConfirmationBias/Rag/simulation.yml

See Rag/explain.md for full design documentation.
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
    """Parse config and launch the ConfirmationBias Rag simulation."""
    parser = argparse.ArgumentParser(description="Run ConfirmationBias Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/Rag/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger.info("Starting ConfirmationBias Rag simulation: %s", args.config)

    runner = SimulationRunner(config)
    runner.run()

    logger.info(
        "Simulation complete. Records saved to: %s",
        config["setting"]["record_path"],
    )


if __name__ == "__main__":
    main()
