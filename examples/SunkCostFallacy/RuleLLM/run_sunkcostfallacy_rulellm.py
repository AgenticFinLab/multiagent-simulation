#!/usr/bin/env python
"""SunkCostFallacy RuleLLM Simulation Runner.

Usage::

    python examples/SunkCostFallacy/RuleLLM/run_sunkcostfallacy_rulellm.py \
        -c configs/SunkCostFallacy/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SunkCostFallacy",
        variant="RuleLLM",
        default_config="configs/SunkCostFallacy/RuleLLM/simulation.yml",
        phenomenon="Investors irrationally hold losing positions to justify prior investment",
        load_env=True,
    )
