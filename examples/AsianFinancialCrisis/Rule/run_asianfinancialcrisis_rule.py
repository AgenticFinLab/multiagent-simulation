#!/usr/bin/env python
"""AsianFinancialCrisis Rule-Based Simulation Runner.

Usage::

    python examples/AsianFinancialCrisis/Rule/run_asianfinancialcrisis_rule.py \
        -c configs/AsianFinancialCrisis/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AsianFinancialCrisis",
        variant="Rule-Based",
        default_config="configs/AsianFinancialCrisis/Rule/simulation.yml",
        phenomenon="1997 Asian Financial Crisis - hot money reversal and contagion cascade",
        load_env=False,
    )
