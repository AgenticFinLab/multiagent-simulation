#!/usr/bin/env python
"""LossAversion Rule-Based Simulation Runner.

Usage::

    python examples/LossAversion/Rule/run_lossaversion.py \
        -c configs/LossAversion/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LossAversion",
        variant="Rule-Based",
        default_config="configs/LossAversion/Rule/simulation.yml",
        phenomenon="Loss aversion causes investors to hold losers too long and sell winners too early",
        load_env=False,
    )
