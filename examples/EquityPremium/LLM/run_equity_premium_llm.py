#!/usr/bin/env python
"""EquityPremium LLM Simulation Runner.

Usage::

    python examples/EquityPremium/LLM/run_equity_premium_llm.py \
        -c configs/EquityPremium/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EquityPremium",
        variant="LLM",
        default_config="configs/EquityPremium/LLM/simulation.yml",
        phenomenon="Stocks return ~6% more than bonds historically (Equity Premium Puzzle)",
        load_env=True,
    )
