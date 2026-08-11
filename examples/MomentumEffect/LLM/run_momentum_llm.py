#!/usr/bin/env python
"""MomentumEffect LLM Simulation Runner.

Usage::

    python examples/MomentumEffect/LLM/run_momentum_llm.py \
        -c configs/MomentumEffect/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="MomentumEffect",
        variant="LLM",
        default_config="configs/MomentumEffect/LLM/simulation.yml",
        phenomenon="Momentum Anomaly (Jegadeesh & Titman 1993) - past winners continue to outperform",
        load_env=True,
    )
