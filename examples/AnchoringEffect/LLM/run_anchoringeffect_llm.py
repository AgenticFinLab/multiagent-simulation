#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Runner (thin variant shim).

Phenomenon: Anchoring causes traders to insufficiently adjust from
reference prices, creating slow price discovery.

Usage::

    python examples/AnchoringEffect/LLM/run_anchoringeffect_llm.py \
        -c configs/AnchoringEffect/LLM/simulation.yml

Shared skeleton lives in :mod:`examples.AnchoringEffect._run`.
"""

from examples.AnchoringEffect._run import run

if __name__ == "__main__":
    run(
        variant="LLM",
        default_config="configs/AnchoringEffect/LLM/simulation.yml",
    )
