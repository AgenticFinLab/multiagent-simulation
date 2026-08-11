#!/usr/bin/env python
"""ReversalEffect RAG Simulation Runner (thin shim).

Usage:
    python examples/ReversalEffect/Rag/run_reversal_effect_ragllm.py
    python examples/ReversalEffect/Rag/run_reversal_effect_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ReversalEffect",
        default_config="configs/ReversalEffect/Rag/simulation.yml",
    )
