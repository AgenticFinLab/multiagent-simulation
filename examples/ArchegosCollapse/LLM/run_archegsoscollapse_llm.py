#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Runner.

Usage::

    python examples/ArchegosCollapse/LLM/run_archegsoscollapse_llm.py \
        -c configs/ArchegosCollapse/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ArchegosCollapse",
        variant="LLM",
        default_config="configs/ArchegosCollapse/LLM/simulation.yml",
        phenomenon="March 2021 - Archegos Capital Management lost $20B, triggering block trade fire sales",
        load_env=True,
    )
