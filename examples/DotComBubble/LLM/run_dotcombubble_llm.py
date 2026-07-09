#!/usr/bin/env python
"""DotComBubble LLM Simulation Runner

1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%

Usage:
    python -m examples.DotComBubble.LLM.run_dotcombubble_llm \
        -c configs/DotComBubble/LLM/simulation.yml
"""

import argparse
import asyncio
import os

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main() -> None:
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run DotComBubble LLM Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/DotComBubble/LLM/simulation.yml",
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        help="Override total_rounds for smoke tests or short runs",
    )
    args = parser.parse_args()

    if args.rounds is not None and args.rounds <= 0:
        parser.error("--rounds must be a positive integer")
    if not os.getenv("ARK_API_KEY"):
        raise RuntimeError("ARK_API_KEY is required for the DotComBubble LLM variant")

    yaml_config = load_config(args.config)
    if args.rounds is not None:
        yaml_config["setting"]["total_rounds"] = args.rounds
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("DotComBubble Simulation - LLM Agents")
    print("=" * 70)
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 70 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        await simulator.run()
        print("\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
