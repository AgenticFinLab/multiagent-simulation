#!/usr/bin/env python
"""CarryTradeUnwind RuleLLM Simulation Runner.

Usage::

    python examples/CarryTradeUnwind/RuleLLM/run_carrytradeunwind_rulellm.py \
        -c configs/CarryTradeUnwind/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CarryTradeUnwind",
        variant="RuleLLM",
        default_config="configs/CarryTradeUnwind/RuleLLM/simulation.yml",
        phenomenon="Funding-currency appreciation triggers forced deleveraging of crowded carry positions",
        load_env=True,
    )
