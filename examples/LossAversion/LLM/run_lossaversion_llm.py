#!/usr/bin/env python
"""LossAversion LLM Simulation Runner.

Usage::

    python examples/LossAversion/LLM/run_lossaversion_llm.py \
        -c configs/LossAversion/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LossAversion",
        variant="LLM",
        default_config="configs/LossAversion/LLM/simulation.yml",
        phenomenon="Loss aversion causes investors to hold losers too long and sell winners too early",
        load_env=True,
    )
