#!/usr/bin/env python
"""MomentumEffect Rule-Based Simulation Runner.

Usage::

    python examples/MomentumEffect/Rule/run_momentum.py \
        -c configs/MomentumEffect/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MomentumEffect",
        variant="Rule-Based",
        default_config="configs/MomentumEffect/Rule/simulation.yml",
        phenomenon="Momentum Anomaly (Jegadeesh & Titman 1993) - past winners continue to outperform",
        load_env=False,
    )
