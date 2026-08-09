#!/usr/bin/env python
"""MomentumEffect RuleLLM Simulation Runner.

Usage::

    python examples/MomentumEffect/RuleLLM/run_momentum_effect_rulellm.py \
        -c configs/MomentumEffect/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="MomentumEffect",
        variant="RuleLLM",
        default_config="configs/MomentumEffect/RuleLLM/simulation.yml",
        phenomenon="Momentum Anomaly (Jegadeesh & Titman 1993) - past winners continue to outperform",
        load_env=True,
    )
