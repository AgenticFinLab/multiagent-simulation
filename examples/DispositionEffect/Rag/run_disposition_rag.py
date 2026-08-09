#!/usr/bin/env python
"""DispositionEffect Rag Simulation Runner.

Usage::

    python examples/DispositionEffect/Rag/run_disposition_rag.py \
        -c configs/DispositionEffect/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="DispositionEffect",
        variant="Rag",
        default_config="configs/DispositionEffect/Rag/simulation.yml",
        phenomenon="Loss aversion causes investors to sell winners too early and hold losers too long",
        load_env=True,
    )
