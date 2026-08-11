#!/usr/bin/env python
"""SouthSeaBubble Rag Simulation Runner.

Usage::

    python examples/SouthSeaBubble/Rag/run_southseabubble_rag.py \
        -c configs/SouthSeaBubble/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SouthSeaBubble",
        variant="Rag",
        default_config="configs/SouthSeaBubble/Rag/simulation.yml",
        phenomenon="Politically endorsed monopoly narratives inflate prices until insider exit triggers collapse",
        load_env=True,
    )
