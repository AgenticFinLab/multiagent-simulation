#!/usr/bin/env python
"""HerdEffect Rule-Based Simulation Runner.

Usage::

    python examples/HerdEffect/Rule/run_herd.py \
        -c configs/HerdEffect/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HerdEffect",
        variant="Rule-Based",
        default_config="configs/HerdEffect/Rule/simulation.yml",
        phenomenon="Emergent herding from heterogeneous investors converging on shared price-return signals",
        load_env=False,
    )
