#!/usr/bin/env python
"""MomentumEffect RAG Simulation Runner (thin shim).

Usage:
    python examples/MomentumEffect/Rag/run_momentum_effect_ragllm.py
    python examples/MomentumEffect/Rag/run_momentum_effect_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MomentumEffect",
        default_config="configs/MomentumEffect/Rag/simulation.yml",
    )
