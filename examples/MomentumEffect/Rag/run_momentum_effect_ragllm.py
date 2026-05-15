#!/usr/bin/env python
"""MomentumEffectRag Simulation Runner

Run RAG-augmented Rule+LLM momentum effect investor simulation.

Knowledge Management Architecture:
  1. ResourceManager pre-processes ALL documents during simulation setup
     (before agents start). This ensures PDFs are processed only once,
     preventing duplicate MinerU API calls and resource contention.
  2. Agents load pre-processed documents from shared cache during initialization.
  3. Each agent builds its own RAG index from pre-processed documents.

Usage:
    python examples/MomentumEffect/Rag/run_momentum_effect_ragllm.py -c configs/MomentumEffect/Rag/simulation.yml

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key — used for LLM inference
    HUNYUAN_API_KEY: Tencent Hunyuan API key — used for RAG embedding
    MINERU_API_KEY: MinerU API key — used for PDF parsing
"""

import argparse
import asyncio
import os
import traceback

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.knowledge import ResourceManager
from masim.knowledge.manager import KnowledgeManager
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Run MomentumEffectRag Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default="configs/MomentumEffect/Rag/simulation.yml"
    )
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("ARK_API_KEY"):
        print("WARNING: ARK_API_KEY not set! LLM inference will not function.")
    if not os.getenv("HUNYUAN_API_KEY"):
        print("WARNING: HUNYUAN_API_KEY not set! RAG embedding will not function.")
    if not os.getenv("MINERU_API_KEY"):
        print("WARNING: MINERU_API_KEY not set! PDF parsing will not function.")

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\n" + "=" * 60)
    print("MomentumEffectRag Simulation")
    print("=" * 60)
    print("Phenomenon: Momentum Effect with RAG-Augmented LLM Decision-Making")
    print("Theory:     Market Microstructure, Kirilenko et al. (2017) + RAG")
    print("Agents:     HFT, Market Maker, Algorithmic Trader,")
    print("            Stop-Loss Trader, Fundamental Trader  (all Rule+LLM+RAG)")
    print("Note:       Documents are pre-processed during simulation setup.")
    print("            Each agent loads from shared cache (no duplicates).")
    print("Rounds:     %s" % config.setting["total_rounds"])
    print("=" * 60 + "\n")

    # PHASE 1: Document Pre-processing
    knowledge_config = config.knowledge
    if not knowledge_config:
        for player_cfg in config.players.values():
            extras = player_cfg.get("config", {}).get("extras", {})
            pk = extras["private_knowledge"]
            rag_cfg = pk["rag"]
            if rag_cfg:
                knowledge_config = {
                    "backend": "local",
                    "global_uri": rag_cfg.get("docs_dir", "examples/document-sources"),
                    "preprocessing": {
                        "parser": "mineru",
                        "output_position": rag_cfg.get(
                            "mineru_output_dir", "MinerU_processed"
                        ),
                    },
                    "rag": {
                        "output_position": rag_cfg.get(
                            "shared_rag_index_dir", "rag_index"
                        ),
                    },
                }
                break

    print("[SETUP] Initializing ResourceManager...")
    resource_manager = ResourceManager(knowledge_config)

    knowledge_manager = KnowledgeManager.from_config(knowledge_config)

    print("[SETUP] Checking and pre-processing documents...")
    results = resource_manager.prepare_shared_resources(fail_fast=False)

    success = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"[SETUP] Document status: {success}/{total} ready")
    if success == total and total > 0:
        print(f"[SETUP] All documents ready!")
    elif total == 0:
        print(f"[SETUP] No PDFs found in shared resources.")

    print("[SETUP] Building shared RAG index...")
    shared_store = knowledge_manager.build_shared_rag_index()
    if shared_store:
        print("[SETUP] Shared RAG index ready!")
    else:
        print("[SETUP] No shared RAG index built (no processed documents available).")

    # Inject knowledge config into each RAG agent's extras
    for player_key, player_cfg in config.players.items():
        extras = player_cfg.get("config", {}).get("extras", {})
        if isinstance(extras, dict) and "private_knowledge" in extras:
            extras["knowledge"] = knowledge_config

    # PHASE 2: Run Simulation
    simulator = GeneralSimulator(config)
    simulator.resource_manager = resource_manager

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\n" + "=" * 60)
        print("Simulation Complete! Rounds: %d" % config.setting["total_rounds"])
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("SIMULATION FAILED WITH ERROR:")
        print("=" * 60)
        traceback.print_exc()
        raise
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
