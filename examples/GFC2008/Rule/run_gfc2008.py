#!/usr/bin/env python
"""GFC2008 Rule-Based Simulation Runner.

Usage::

    python examples/GFC2008/Rule/run_gfc2008.py \
        -c configs/GFC2008/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GFC2008",
        variant="Rule-Based",
        default_config="configs/GFC2008/Rule/simulation.yml",
        phenomenon="2007-2009 financial crisis - Housing bubble burst triggered global recession",
        load_env=False,
    )
