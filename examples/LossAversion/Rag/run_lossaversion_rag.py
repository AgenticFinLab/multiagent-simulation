#!/usr/bin/env python
"""LossAversion Rag Simulation Runner.

Usage::

    python examples/LossAversion/Rag/run_lossaversion_rag.py \
        -c configs/LossAversion/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="LossAversion",
        variant="Rag",
        default_config="configs/LossAversion/Rag/simulation.yml",
        phenomenon="Loss aversion causes investors to hold losers too long and sell winners too early",
        load_env=True,
    )
