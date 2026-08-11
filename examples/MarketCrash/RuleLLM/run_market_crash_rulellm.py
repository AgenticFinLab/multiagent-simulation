#!/usr/bin/env python
"""MarketCrash RuleLLM Simulation Runner.

Usage::

    python examples/MarketCrash/RuleLLM/run_market_crash_rulellm.py \
        -c configs/MarketCrash/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MarketCrash",
        variant="RuleLLM",
        default_config="configs/MarketCrash/RuleLLM/simulation.yml",
        phenomenon="Rapid price decline with liquidity evaporation",
        load_env=True,
    )
