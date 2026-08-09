#!/usr/bin/env python
"""LTCMCollapse RuleLLM Simulation Runner.

Usage::

    python examples/LTCMCollapse/RuleLLM/run_ltcmcollapse_rulellm.py \
        -c configs/LTCMCollapse/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="LTCMCollapse",
        variant="RuleLLM",
        default_config="configs/LTCMCollapse/RuleLLM/simulation.yml",
        phenomenon="August-September 1998 LTCM crisis - Russian default triggered liquidity crisis",
        load_env=True,
    )
