#!/usr/bin/env python
"""VolatilityClustering RAG Simulation Runner (thin shim).

Usage:
    python examples/VolatilityClustering/Rag/run_volatility_clustering_ragllm.py
    python examples/VolatilityClustering/Rag/run_volatility_clustering_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="VolatilityClustering",
        default_config="configs/VolatilityClustering/Rag/simulation.yml",
    )
