#!/usr/bin/env python
"""SunkCostFallacy Rule-Based Simulation Runner.

Usage::

    python examples/SunkCostFallacy/Rule/run_sunkcostfallacy.py \
        -c configs/SunkCostFallacy/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SunkCostFallacy",
        variant="Rule-Based",
        default_config="configs/SunkCostFallacy/Rule/simulation.yml",
        phenomenon="Investors irrationally hold losing positions to justify prior investment",
        load_env=False,
    )
