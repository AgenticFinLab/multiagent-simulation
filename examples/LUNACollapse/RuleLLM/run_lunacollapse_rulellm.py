#!/usr/bin/env python
"""LUNACollapse RuleLLM Simulation Runner.

Usage::

    python examples/LUNACollapse/RuleLLM/run_lunacollapse_rulellm.py \
        -c configs/LUNACollapse/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LUNACollapse",
        variant="RuleLLM",
        default_config="configs/LUNACollapse/RuleLLM/simulation.yml",
        phenomenon="May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral",
        load_env=True,
    )
