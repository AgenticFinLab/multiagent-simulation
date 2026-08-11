#!/usr/bin/env python
"""EquityPremium RAG Simulation Runner (thin shim).

Usage:
    python examples/EquityPremium/Rag/run_equity_premium_ragllm.py
    python examples/EquityPremium/Rag/run_equity_premium_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EquityPremium",
        default_config="configs/EquityPremium/Rag/simulation.yml",
    )
