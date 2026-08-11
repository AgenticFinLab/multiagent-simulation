#!/usr/bin/env python
"""ArchegosCollapse Rule-Based Simulation Runner.

Usage::

    python examples/ArchegosCollapse/Rule/run_archegsoscollapse.py \
        -c configs/ArchegosCollapse/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ArchegosCollapse",
        variant="Rule-Based",
        default_config="configs/ArchegosCollapse/Rule/simulation.yml",
        phenomenon="March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales",
        load_env=False,
    )
