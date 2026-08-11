#!/usr/bin/env python
"""GamblerFallacy Rag Simulation Runner.

Usage::

    python examples/GamblerFallacy/Rag/run_gamblerfallacy_rag.py \
        -c configs/GamblerFallacy/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GamblerFallacy",
        variant="Rag",
        default_config="configs/GamblerFallacy/Rag/simulation.yml",
        phenomenon="Streak-conditioned trading from gambler's-fallacy reversal and hot-hand extrapolation",
        load_env=True,
    )
