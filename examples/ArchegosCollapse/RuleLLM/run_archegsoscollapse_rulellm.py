#!/usr/bin/env python
"""ArchegosCollapse RuleLLM Simulation Runner.

Usage::

    python examples/ArchegosCollapse/RuleLLM/run_archegsoscollapse_rulellm.py \
        -c configs/ArchegosCollapse/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ArchegosCollapse",
        variant="RuleLLM",
        default_config="configs/ArchegosCollapse/RuleLLM/simulation.yml",
        phenomenon="March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales",
        load_env=True,
    )
