#!/usr/bin/env python
"""ConfirmationBias Rule-Based Simulation Runner.

Usage::

    python examples/ConfirmationBias/Rule/run_confirmationbias_rule.py \
        -c configs/ConfirmationBias/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ConfirmationBias",
        variant="Rule-Based",
        default_config="configs/ConfirmationBias/Rule/simulation.yml",
        phenomenon="Investors selectively weight belief-confirming signals and discount contradictory evidence",
        load_env=False,
    )
