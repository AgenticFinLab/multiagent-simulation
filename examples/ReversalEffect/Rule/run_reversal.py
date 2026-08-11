#!/usr/bin/env python
"""ReversalEffect Rule-Based Simulation Runner.

Usage::

    python examples/ReversalEffect/Rule/run_reversal.py \
        -c configs/ReversalEffect/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ReversalEffect",
        variant="Rule-Based",
        default_config="configs/ReversalEffect/Rule/simulation.yml",
        phenomenon="Past losers outperform past winners over 3-5 year horizons",
        load_env=False,
    )
