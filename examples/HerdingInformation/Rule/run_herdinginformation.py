#!/usr/bin/env python
"""HerdingInformation Rule-Based Simulation Runner.

Usage::

    python examples/HerdingInformation/Rule/run_herdinginformation.py \
        -c configs/HerdingInformation/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HerdingInformation",
        variant="Rule-Based",
        default_config="configs/HerdingInformation/Rule/simulation.yml",
        phenomenon="Information cascade - individuals ignore private signals and follow the crowd",
        load_env=False,
    )
