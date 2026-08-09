#!/usr/bin/env python
"""AnchoringEffect RuleLLM Simulation Runner (thin variant shim).

Phenomenon: Anchoring causes traders to insufficiently adjust from
reference prices, creating slow price discovery.

Usage::

    python examples/AnchoringEffect/RuleLLM/run_anchoringeffect_rulellm.py \
        -c configs/AnchoringEffect/RuleLLM/simulation.yml

Shared skeleton lives in :mod:`examples.AnchoringEffect._run`.
"""

from examples.AnchoringEffect._run import run

if __name__ == "__main__":
    run(
        variant="RuleLLM",
        default_config="configs/AnchoringEffect/RuleLLM/simulation.yml",
    )
