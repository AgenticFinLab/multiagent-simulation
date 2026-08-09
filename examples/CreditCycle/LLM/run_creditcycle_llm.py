#!/usr/bin/env python
"""CreditCycle LLM Simulation Runner.

Usage::

    python examples/CreditCycle/LLM/run_creditcycle_llm.py \
        -c configs/CreditCycle/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CreditCycle",
        variant="LLM",
        default_config="configs/CreditCycle/LLM/simulation.yml",
        phenomenon="Pro-cyclical credit expansion builds fragility that resolves in a Minsky-moment crash",
        load_env=True,
    )
