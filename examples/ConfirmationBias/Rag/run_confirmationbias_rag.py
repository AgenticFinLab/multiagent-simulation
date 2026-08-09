#!/usr/bin/env python
"""ConfirmationBias Rag Simulation Runner.

Usage::

    python examples/ConfirmationBias/Rag/run_confirmationbias_rag.py \
        -c configs/ConfirmationBias/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ConfirmationBias",
        variant="Rag",
        default_config="configs/ConfirmationBias/Rag/simulation.yml",
        phenomenon="Investors selectively weight belief-confirming signals and discount contradictory evidence",
        load_env=True,
    )
