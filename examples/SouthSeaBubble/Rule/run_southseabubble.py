#!/usr/bin/env python
"""SouthSeaBubble Rule-Based Simulation Runner.

Usage::

    python examples/SouthSeaBubble/Rule/run_southseabubble.py \
        -c configs/SouthSeaBubble/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SouthSeaBubble",
        variant="Rule-Based",
        default_config="configs/SouthSeaBubble/Rule/simulation.yml",
        phenomenon="Politically endorsed monopoly narratives inflate prices until insider exit triggers collapse",
        load_env=False,
    )
