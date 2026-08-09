#!/usr/bin/env python
"""ConfirmationBias RuleLLM Simulation Runner.

Usage::

    python examples/ConfirmationBias/RuleLLM/run_confirmationbias_rulellm.py \
        -c configs/ConfirmationBias/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ConfirmationBias",
        variant="RuleLLM",
        default_config="configs/ConfirmationBias/RuleLLM/simulation.yml",
        phenomenon="Investors selectively weight belief-confirming signals and discount contradictory evidence",
        load_env=True,
    )
