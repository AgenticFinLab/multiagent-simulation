#!/usr/bin/env python
"""CreditCycle RuleLLM Simulation Runner.

Usage::

    python examples/CreditCycle/RuleLLM/run_creditcycle_rulellm.py \
        -c configs/CreditCycle/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CreditCycle",
        variant="RuleLLM",
        default_config="configs/CreditCycle/RuleLLM/simulation.yml",
        phenomenon="Pro-cyclical credit expansion builds fragility that resolves in a Minsky-moment crash",
        load_env=True,
    )
