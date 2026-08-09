#!/usr/bin/env python
"""EquityPremium Rule-Based Simulation Runner.

Usage::

    python examples/EquityPremium/Rule/run_equity_premium.py \
        -c configs/EquityPremium/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EquityPremium",
        variant="Rule-Based",
        default_config="configs/EquityPremium/Rule/simulation.yml",
        phenomenon="Stocks return ~6% more than bonds historically (Equity Premium Puzzle)",
        load_env=False,
    )
