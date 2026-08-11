#!/usr/bin/env python
"""LTCMCollapse Rule-Based Simulation Runner.

Usage::

    python examples/LTCMCollapse/Rule/run_ltcmcollapse.py \
        -c configs/LTCMCollapse/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LTCMCollapse",
        variant="Rule-Based",
        default_config="configs/LTCMCollapse/Rule/simulation.yml",
        phenomenon="August-September 1998 LTCM crisis - Russian default triggered liquidity crisis",
        load_env=False,
    )
