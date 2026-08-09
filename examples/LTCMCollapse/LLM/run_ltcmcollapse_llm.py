#!/usr/bin/env python
"""LTCMCollapse LLM Simulation Runner.

Usage::

    python examples/LTCMCollapse/LLM/run_ltcmcollapse_llm.py \
        -c configs/LTCMCollapse/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="LTCMCollapse",
        variant="LLM",
        default_config="configs/LTCMCollapse/LLM/simulation.yml",
        phenomenon="August-September 1998 LTCM crisis - Russian default triggered liquidity crisis",
        load_env=True,
    )
