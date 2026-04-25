#!/usr/bin/env python
"""CarryTradeUnwind Rule-Based Simulation Entry Point

Runs the carry trade unwind simulation using deterministic rule-based agents.
All agents act on published {price, fundamental, deviation, round} market data.

Usage:
    python examples/CarryTradeUnwind/Rule/run_carrytradeunwind_rule.py \\
        -c configs/CarryTradeUnwind/Rule/simulation.yml

See Rule/explain.md for full design documentation.
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
    """Parse config and launch the CarryTradeUnwind Rule simulation."""
    parser = argparse.ArgumentParser(
        description="Run CarryTradeUnwind Rule-Based simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/CarryTradeUnwind/Rule/simulation.yml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger.info("Starting CarryTradeUnwind Rule simulation: %s", args.config)

    runner = SimulationRunner(config)
    runner.run()

    logger.info(
        "Simulation complete. Records saved to: %s",
        config["setting"]["record_path"],
    )


if __name__ == "__main__":
    main()
