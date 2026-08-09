#!/usr/bin/env python
"""MarketCrash Rule-Based Simulation Runner.

Usage::

    python examples/MarketCrash/Rule/run_crash.py \
        -c configs/MarketCrash/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="MarketCrash",
        variant="Rule-Based",
        default_config="configs/MarketCrash/Rule/simulation.yml",
        phenomenon="Rapid price decline with liquidity evaporation",
        load_env=False,
    )
