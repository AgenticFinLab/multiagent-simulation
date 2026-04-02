#!/usr/bin/env python
"""AssetBubbleRag Simulation Runner

Run RAG-augmented Rule+LLM bubble investor simulation.

Each agent:
  1. Downloads/caches reference documents at initialization (LLM-suggested
     URLs by default, or from docs_dir / url_csv in config).
  2. Builds a personal LlamaIndex RAG vector index (persisted to disk).
  3. Retrieves the top-k most relevant chunks before every trading decision
     and injects them into the LLM prompt.

Usage:
    python examples/AssetBubble/Rag/run_bubble_ragllm.py -c configs/AssetBubble/Rag/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key — used for both LLM inference
                 and embedding (doubao-embedding-large-text-240915)
"""

import argparse
import asyncio
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run AssetBubbleRag Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default="configs/AssetBubble/Rag/simulation.yml"
    )
    parser.add_argument("-r", "--rounds", type=int, default=None)
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print(
            "WARNING: ARK_API_KEY not set! LLM inference and RAG embedding will not function."
        )

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    print("\n" + "=" * 60)
    print("AssetBubbleRag Simulation")
    print("=" * 60)
    print("Phenomenon: Asset Bubble with RAG-Augmented LLM Decision-Making")
    print("Theory:     Greater Fool Theory + Explicit Quantitative Rules + RAG")
    print("Agents:     Momentum Speculator, Rational Arbitrageur, Noise Trader,")
    print("            Value Investor, Leveraged Buyer  (all Rule+LLM+RAG)")
    print("Note:       Each agent builds a personal RAG library on round 1.")
    print("            Document download may take 30-90s per agent type.")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 60 + "\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 60)
        print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
        print("=" * 60)
    except Exception as e:
        import traceback

        print("\n" + "=" * 60)
        print("SIMULATION FAILED WITH ERROR:")
        print("=" * 60)
        traceback.print_exc()
        raise
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
