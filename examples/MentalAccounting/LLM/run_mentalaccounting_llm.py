#!/usr/bin/env python
"""MentalAccounting LLM Simulation Runner.

Usage::

    python examples/MentalAccounting/LLM/run_mentalaccounting_llm.py \
        -c configs/MentalAccounting/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="MentalAccounting",
        variant="LLM",
        default_config="configs/MentalAccounting/LLM/simulation.yml",
        phenomenon="Investors evaluate wealth in separate psychological accounts instead of optimizing total portfolio",
        load_env=True,
    )
