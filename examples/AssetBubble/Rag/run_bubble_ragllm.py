#!/usr/bin/env python
"""AssetBubble RAG Simulation Runner (thin shim).

Usage:
    python examples/AssetBubble/Rag/run_bubble_ragllm.py
    python examples/AssetBubble/Rag/run_bubble_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AssetBubble",
        default_config="configs/AssetBubble/Rag/simulation.yml",
    )
