#!/usr/bin/env python
"""EndowmentEffect LLM Simulation Runner

Endowment effect: LLM-driven biased holders vs. rational agents

Usage:
    python -m examples.EndowmentEffect.LLM.run_endowmenteffect_llm -c configs/EndowmentEffect/LLM/simulation.yml
"""

import argparse
import asyncio

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main() -> None:
    load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(description="Run EndowmentEffect LLM Simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EndowmentEffect/LLM/simulation.yml",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 70)
    print("EndowmentEffect Simulation - LLM Agents")
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
