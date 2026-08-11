#!/usr/bin/env python
"""AsianFinancialCrisis RuleLLM Simulation Runner.

Usage::

    python examples/AsianFinancialCrisis/RuleLLM/run_asianfinancialcrisis_rulellm.py \
        -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AsianFinancialCrisis",
        variant="RuleLLM",
        default_config="configs/AsianFinancialCrisis/RuleLLM/simulation.yml",
        phenomenon="1997 Asian Financial Crisis - hot money reversal and contagion cascade",
        load_env=True,
    )
