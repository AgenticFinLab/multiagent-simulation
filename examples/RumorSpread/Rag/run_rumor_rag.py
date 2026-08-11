#!/usr/bin/env python
"""RumorSpread RAG Simulation Runner (thin shim).

Usage:
    python examples/RumorSpread/Rag/run_rumor_rag.py
    python examples/RumorSpread/Rag/run_rumor_rag.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RumorSpread",
        default_config="configs/RumorSpread/Rag/simulation.yml",
    )
