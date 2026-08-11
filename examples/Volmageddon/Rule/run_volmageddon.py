#!/usr/bin/env python
"""Volmageddon Rule-Based Simulation Runner.

Usage::

    python examples/Volmageddon/Rule/run_volmageddon.py \
        -c configs/Volmageddon/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="Volmageddon",
        variant="Rule-Based",
        default_config="configs/Volmageddon/Rule/simulation.yml",
        phenomenon="February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours",
        load_env=False,
    )
