#!/usr/bin/env python
"""LiquidityDryup RuleLLM Simulation Runner.

Usage::

    python examples/LiquidityDryup/RuleLLM/run_liquidity_dryup_rulellm.py \
        -c configs/LiquidityDryup/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LiquidityDryup",
        variant="RuleLLM",
        default_config="configs/LiquidityDryup/RuleLLM/simulation.yml",
        phenomenon="Market maker withdrawal creates illiquidity spirals",
        load_env=True,
    )
