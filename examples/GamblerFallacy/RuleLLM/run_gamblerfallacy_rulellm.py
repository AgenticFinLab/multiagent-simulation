#!/usr/bin/env python
"""GamblerFallacy RuleLLM Simulation Runner.

Usage::

    python examples/GamblerFallacy/RuleLLM/run_gamblerfallacy_rulellm.py \
        -c configs/GamblerFallacy/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GamblerFallacy",
        variant="RuleLLM",
        default_config="configs/GamblerFallacy/RuleLLM/simulation.yml",
        phenomenon="Streak-conditioned trading from gambler's-fallacy reversal and hot-hand extrapolation",
        load_env=True,
    )
