#!/usr/bin/env python
"""SorosPound Rule-Based Simulation Runner.

Usage::

    python examples/SorosPound/Rule/run_sorospound.py \
        -c configs/SorosPound/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SorosPound",
        variant="Rule-Based",
        default_config="configs/SorosPound/Rule/simulation.yml",
        phenomenon="Macro speculators attack an overvalued fixed peg, overwhelming central bank reserves",
        load_env=False,
    )
