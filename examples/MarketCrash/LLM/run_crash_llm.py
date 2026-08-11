#!/usr/bin/env python
"""MarketCrash LLM Simulation Runner.

Usage::

    python examples/MarketCrash/LLM/run_crash_llm.py \
        -c configs/MarketCrash/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MarketCrash",
        variant="LLM",
        default_config="configs/MarketCrash/LLM/simulation.yml",
        phenomenon="Rapid price decline with liquidity evaporation",
        load_env=True,
    )
