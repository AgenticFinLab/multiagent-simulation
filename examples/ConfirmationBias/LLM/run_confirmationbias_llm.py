#!/usr/bin/env python
"""ConfirmationBias LLM Simulation Runner.

Usage::

    python examples/ConfirmationBias/LLM/run_confirmationbias_llm.py \
        -c configs/ConfirmationBias/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ConfirmationBias",
        variant="LLM",
        default_config="configs/ConfirmationBias/LLM/simulation.yml",
        phenomenon="Investors selectively weight belief-confirming signals and discount contradictory evidence",
        load_env=True,
    )
