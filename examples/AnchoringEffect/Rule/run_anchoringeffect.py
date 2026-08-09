#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Runner (thin variant shim).

Phenomenon: Anchoring causes traders to insufficiently adjust from
reference prices, creating slow price discovery.

Usage::

    python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
        -c configs/AnchoringEffect/Rule/simulation.yml

Shared skeleton lives in :mod:`examples.AnchoringEffect._run`.
"""

from examples.AnchoringEffect._run import run

if __name__ == "__main__":
    run(
        variant="Rule-Based",
        default_config="configs/AnchoringEffect/Rule/simulation.yml",
        load_env=False,
    )
