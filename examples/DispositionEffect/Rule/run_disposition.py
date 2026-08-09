#!/usr/bin/env python
"""DispositionEffect Rule-Based Simulation Runner.

Usage::

    python examples/DispositionEffect/Rule/run_disposition.py \
        -c configs/DispositionEffect/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="DispositionEffect",
        variant="Rule-Based",
        default_config="configs/DispositionEffect/Rule/simulation.yml",
        phenomenon="Loss aversion causes investors to sell winners too early and hold losers too long",
        load_env=False,
    )
