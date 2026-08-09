#!/usr/bin/env python
"""LiquidityDryup LLM Simulation Runner.

Usage::

    python examples/LiquidityDryup/LLM/run_liquidity_llm.py \
        -c configs/LiquidityDryup/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="LiquidityDryup",
        variant="LLM",
        default_config="configs/LiquidityDryup/LLM/simulation.yml",
        phenomenon="Market maker withdrawal creates illiquidity spirals",
        load_env=True,
    )
