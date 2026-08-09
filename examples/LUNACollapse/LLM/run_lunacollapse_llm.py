#!/usr/bin/env python
"""LUNACollapse LLM Simulation Runner.

Usage::

    python examples/LUNACollapse/LLM/run_lunacollapse_llm.py \
        -c configs/LUNACollapse/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="LUNACollapse",
        variant="LLM",
        default_config="configs/LUNACollapse/LLM/simulation.yml",
        phenomenon="May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral",
        load_env=True,
    )
