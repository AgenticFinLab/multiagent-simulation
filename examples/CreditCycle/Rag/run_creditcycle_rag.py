#!/usr/bin/env python
"""CreditCycle Rag Simulation Runner.

Usage::

    python examples/CreditCycle/Rag/run_creditcycle_rag.py \
        -c configs/CreditCycle/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="CreditCycle",
        variant="Rag",
        default_config="configs/CreditCycle/Rag/simulation.yml",
        phenomenon="Pro-cyclical credit expansion builds fragility that resolves in a Minsky-moment crash",
        load_env=True,
    )
