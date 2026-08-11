#!/usr/bin/env python
"""MentalAccounting RuleLLM Simulation Runner.

Usage::

    python examples/MentalAccounting/RuleLLM/run_mentalaccounting_rulellm.py \
        -c configs/MentalAccounting/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MentalAccounting",
        variant="RuleLLM",
        default_config="configs/MentalAccounting/RuleLLM/simulation.yml",
        phenomenon="Investors evaluate wealth in separate psychological accounts instead of optimizing total portfolio",
        load_env=True,
    )
