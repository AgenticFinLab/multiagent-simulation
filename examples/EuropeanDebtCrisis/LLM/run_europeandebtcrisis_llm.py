#!/usr/bin/env python
"""EuropeanDebtCrisis LLM Simulation Runner.

Usage::

    python examples/EuropeanDebtCrisis/LLM/run_europeandebtcrisis_llm.py \
        -c configs/EuropeanDebtCrisis/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EuropeanDebtCrisis",
        variant="LLM",
        default_config="configs/EuropeanDebtCrisis/LLM/simulation.yml",
        phenomenon="Self-fulfilling creditor panic creates a sovereign doom loop",
        load_env=True,
    )
