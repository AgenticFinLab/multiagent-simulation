#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Runner.

Usage::

    python examples/AnchoringEffect/LLM/run_anchoringeffect_llm.py \
        -c configs/AnchoringEffect/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AnchoringEffect",
        variant="LLM",
        default_config="configs/AnchoringEffect/LLM/simulation.yml",
        phenomenon="Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery",
        load_env=True,
    )
