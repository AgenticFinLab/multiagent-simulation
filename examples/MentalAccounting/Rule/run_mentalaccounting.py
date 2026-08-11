#!/usr/bin/env python
"""MentalAccounting Rule-Based Simulation Runner.

Usage::

    python examples/MentalAccounting/Rule/run_mentalaccounting.py \
        -c configs/MentalAccounting/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MentalAccounting",
        variant="Rule-Based",
        default_config="configs/MentalAccounting/Rule/simulation.yml",
        phenomenon="Investors evaluate wealth in separate psychological accounts instead of optimizing total portfolio",
        load_env=False,
    )
