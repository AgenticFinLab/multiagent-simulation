#!/usr/bin/env python
"""ShortSqueeze RAG Simulation Runner (thin shim).

Usage:
    python examples/ShortSqueeze/Rag/run_short_squeeze_ragllm.py
    python examples/ShortSqueeze/Rag/run_short_squeeze_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ShortSqueeze",
        default_config="configs/ShortSqueeze/Rag/simulation.yml",
    )
