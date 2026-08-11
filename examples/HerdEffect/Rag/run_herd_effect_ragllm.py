#!/usr/bin/env python
"""HerdEffect RAG Simulation Runner (thin shim).

Usage:
    python examples/HerdEffect/Rag/run_herd_effect_ragllm.py
    python examples/HerdEffect/Rag/run_herd_effect_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HerdEffect",
        default_config="configs/HerdEffect/Rag/simulation.yml",
    )
