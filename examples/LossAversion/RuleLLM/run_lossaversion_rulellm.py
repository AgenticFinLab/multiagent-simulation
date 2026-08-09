#!/usr/bin/env python
"""LossAversion RuleLLM Simulation Runner.

Usage::

    python examples/LossAversion/RuleLLM/run_lossaversion_rulellm.py \
        -c configs/LossAversion/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="LossAversion",
        variant="RuleLLM",
        default_config="configs/LossAversion/RuleLLM/simulation.yml",
        phenomenon="Loss aversion causes investors to hold losers too long and sell winners too early",
        load_env=True,
    )
