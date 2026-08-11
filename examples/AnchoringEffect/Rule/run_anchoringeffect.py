#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Runner.

Usage::

    python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AnchoringEffect",
        variant="Rule-Based",
        default_config="configs/AnchoringEffect/Rule/simulation.yml",
        phenomenon="Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery",
        load_env=False,
    )
