#!/usr/bin/env python
"""LUNACollapse Rule-Based Simulation Runner.

Usage::

    python examples/LUNACollapse/Rule/run_lunacollapse.py \
        -c configs/LUNACollapse/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LUNACollapse",
        variant="Rule-Based",
        default_config="configs/LUNACollapse/Rule/simulation.yml",
        phenomenon="May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral",
        load_env=False,
    )
