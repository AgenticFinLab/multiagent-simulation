#!/usr/bin/env python
"""LiquidityDryup Rule-Based Simulation Runner.

Usage::

    python examples/LiquidityDryup/Rule/run_liquidity.py \
        -c configs/LiquidityDryup/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LiquidityDryup",
        variant="Rule-Based",
        default_config="configs/LiquidityDryup/Rule/simulation.yml",
        phenomenon="Market maker withdrawal creates illiquidity spirals",
        load_env=False,
    )
