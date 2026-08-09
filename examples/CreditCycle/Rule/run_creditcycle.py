#!/usr/bin/env python
"""CreditCycle Rule-Based Simulation Runner.

Usage::

    python examples/CreditCycle/Rule/run_creditcycle.py \
        -c configs/CreditCycle/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CreditCycle",
        variant="Rule-Based",
        default_config="configs/CreditCycle/Rule/simulation.yml",
        phenomenon="Pro-cyclical credit expansion builds fragility that resolves in a Minsky-moment crash",
        load_env=False,
    )
