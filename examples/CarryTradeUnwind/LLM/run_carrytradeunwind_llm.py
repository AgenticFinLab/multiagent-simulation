#!/usr/bin/env python
"""CarryTradeUnwind LLM Simulation Entry Point

Runs the carry trade unwind simulation using LLM-driven agents.
Agents receive {price, fundamental, deviation, round} market data
and generate buy/sell/hold decisions via language model calls.

Usage:
    python examples/CarryTradeUnwind/LLM/run_carrytradeunwind_llm.py \\
        -c configs/CarryTradeUnwind/LLM/simulation.yml

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
    """Parse config and launch the CarryTradeUnwind LLM simulation."""
    parser = argparse.ArgumentParser(description="Run CarryTradeUnwind LLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/CarryTradeUnwind/LLM/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger.info("Starting CarryTradeUnwind LLM simulation: %s", args.config)

    runner = SimulationRunner(config)
    runner.run()

    logger.info(
        "Simulation complete. Records saved to: %s",
        config["setting"]["record_path"],
    )


if __name__ == "__main__":
    main()
