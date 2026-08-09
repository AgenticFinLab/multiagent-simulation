#!/usr/bin/env python
"""SorosPound LLM Simulation Runner.

Usage::

    python examples/SorosPound/LLM/run_sorospound_llm.py \
        -c configs/SorosPound/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SorosPound",
        variant="LLM",
        default_config="configs/SorosPound/LLM/simulation.yml",
        phenomenon="Macro speculators attack an overvalued fixed peg, overwhelming central bank reserves",
        load_env=True,
    )
