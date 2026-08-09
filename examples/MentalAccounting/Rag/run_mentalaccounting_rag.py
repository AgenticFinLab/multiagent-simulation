#!/usr/bin/env python
"""MentalAccounting Rag Simulation Runner.

Usage::

    python examples/MentalAccounting/Rag/run_mentalaccounting_rag.py \
        -c configs/MentalAccounting/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="MentalAccounting",
        variant="Rag",
        default_config="configs/MentalAccounting/Rag/simulation.yml",
        phenomenon="Investors evaluate wealth in separate psychological accounts instead of optimizing total portfolio",
        load_env=True,
    )
