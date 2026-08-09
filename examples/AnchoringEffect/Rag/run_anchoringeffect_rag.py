#!/usr/bin/env python
"""AnchoringEffect Rag Simulation Runner.

Usage::

    python examples/AnchoringEffect/Rag/run_anchoringeffect_rag.py \
        -c configs/AnchoringEffect/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="AnchoringEffect",
        variant="Rag",
        default_config="configs/AnchoringEffect/Rag/simulation.yml",
        phenomenon="Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery",
        load_env=True,
    )
