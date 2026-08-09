#!/usr/bin/env python
"""GamblerFallacy LLM Simulation Runner.

Usage::

    python examples/GamblerFallacy/LLM/run_gamblerfallacy_llm.py \
        -c configs/GamblerFallacy/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="GamblerFallacy",
        variant="LLM",
        default_config="configs/GamblerFallacy/LLM/simulation.yml",
        phenomenon="Streak-conditioned trading from gambler's-fallacy reversal and hot-hand extrapolation",
        load_env=True,
    )
