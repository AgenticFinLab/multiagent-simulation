#!/usr/bin/env python
"""VolatilityClustering Rule-Based Simulation Runner.

Usage::

    python examples/VolatilityClustering/Rule/run_volatility.py \
        -c configs/VolatilityClustering/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="VolatilityClustering",
        variant="Rule-Based",
        default_config="configs/VolatilityClustering/Rule/simulation.yml",
        phenomenon="GARCH-like volatility persistence and clustering",
        load_env=False,
    )
