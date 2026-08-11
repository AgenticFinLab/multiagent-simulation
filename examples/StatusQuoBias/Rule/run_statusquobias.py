#!/usr/bin/env python
"""StatusQuoBias Rule-Based Simulation Runner.

Usage::

    python examples/StatusQuoBias/Rule/run_statusquobias.py \
        -c configs/StatusQuoBias/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="StatusQuoBias",
        variant="Rule-Based",
        default_config="configs/StatusQuoBias/Rule/simulation.yml",
        phenomenon="Psychological inertia suppresses portfolio rebalancing, causing persistent mispricing",
        load_env=False,
    )
