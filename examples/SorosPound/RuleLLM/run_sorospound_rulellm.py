#!/usr/bin/env python
"""SorosPound RuleLLM Simulation Runner.

Usage::

    python examples/SorosPound/RuleLLM/run_sorospound_rulellm.py \
        -c configs/SorosPound/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SorosPound",
        variant="RuleLLM",
        default_config="configs/SorosPound/RuleLLM/simulation.yml",
        phenomenon="Macro speculators attack an overvalued fixed peg, overwhelming central bank reserves",
        load_env=True,
    )
