#!/usr/bin/env python
"""SorosPound Rag Simulation Runner.

Usage::

    python examples/SorosPound/Rag/run_sorospound_rag.py \
        -c configs/SorosPound/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SorosPound",
        variant="Rag",
        default_config="configs/SorosPound/Rag/simulation.yml",
        phenomenon="Macro speculators attack an overvalued fixed peg, overwhelming central bank reserves",
        load_env=True,
    )
