#!/usr/bin/env python
"""LiquidityDryup RAG Simulation Runner (thin shim).

Usage:
    python examples/LiquidityDryup/Rag/run_liquidity_dryup_ragllm.py
    python examples/LiquidityDryup/Rag/run_liquidity_dryup_ragllm.py -c path/to/config.yml -r 50
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LiquidityDryup",
        default_config="configs/LiquidityDryup/Rag/simulation.yml",
    )
