#!/usr/bin/env python
"""MarketCrash RAG Simulation Runner (thin shim).

Usage:
    python examples/MarketCrash/Rag/run_market_crash_ragllm.py
    python examples/MarketCrash/Rag/run_market_crash_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MarketCrash",
        default_config="configs/MarketCrash/Rag/simulation.yml",
    )
