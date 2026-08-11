#!/usr/bin/env python
"""SunkCostFallacy LLM Simulation Runner.

Usage::

    python examples/SunkCostFallacy/LLM/run_sunkcostfallacy_llm.py \
        -c configs/SunkCostFallacy/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SunkCostFallacy",
        variant="LLM",
        default_config="configs/SunkCostFallacy/LLM/simulation.yml",
        phenomenon="Investors irrationally hold losing positions to justify prior investment",
        load_env=True,
    )
