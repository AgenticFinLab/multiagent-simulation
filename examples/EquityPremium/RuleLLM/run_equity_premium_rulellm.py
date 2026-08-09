#!/usr/bin/env python
"""EquityPremium RuleLLM Simulation Runner.

Usage::

    python examples/EquityPremium/RuleLLM/run_equity_premium_rulellm.py \
        -c configs/EquityPremium/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EquityPremium",
        variant="RuleLLM",
        default_config="configs/EquityPremium/RuleLLM/simulation.yml",
        phenomenon="Stocks return ~6% more than bonds historically (Equity Premium Puzzle)",
        load_env=True,
    )
