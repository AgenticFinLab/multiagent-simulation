#!/usr/bin/env python
"""GamblerFallacy Rule-Based Simulation Runner.

Usage::

    python examples/GamblerFallacy/Rule/run_gamblerfallacy.py \
        -c configs/GamblerFallacy/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GamblerFallacy",
        variant="Rule-Based",
        default_config="configs/GamblerFallacy/Rule/simulation.yml",
        phenomenon="Streak-conditioned trading from gambler's-fallacy reversal and hot-hand extrapolation",
        load_env=False,
    )
