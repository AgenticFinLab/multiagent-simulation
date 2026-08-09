#!/usr/bin/env python
"""EuropeanDebtCrisis RuleLLM Simulation Runner.

Usage::

    python examples/EuropeanDebtCrisis/RuleLLM/run_europeandebtcrisis_rulellm.py \
        -c configs/EuropeanDebtCrisis/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EuropeanDebtCrisis",
        variant="RuleLLM",
        default_config="configs/EuropeanDebtCrisis/RuleLLM/simulation.yml",
        phenomenon="Self-fulfilling creditor panic creates a sovereign doom loop",
        load_env=True,
    )
