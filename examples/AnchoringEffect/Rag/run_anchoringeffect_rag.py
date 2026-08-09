#!/usr/bin/env python
"""AnchoringEffect Rag Simulation Runner (thin variant shim).

Phenomenon: Anchoring causes traders to insufficiently adjust from
reference prices, creating slow price discovery.

Usage::

    python examples/AnchoringEffect/Rag/run_anchoringeffect_rag.py \
        -c configs/AnchoringEffect/Rag/simulation.yml

Shared skeleton lives in :mod:`examples.AnchoringEffect._run`.
"""

from examples.AnchoringEffect._run import run

if __name__ == "__main__":
    run(
        variant="Rag",
        default_config="configs/AnchoringEffect/Rag/simulation.yml",
    )
