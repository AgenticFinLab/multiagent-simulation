#!/usr/bin/env python
"""AnchoringEffect RuleLLM Simulation Runner.

Usage::

    python examples/AnchoringEffect/RuleLLM/run_anchoringeffect_rulellm.py \
        -c configs/AnchoringEffect/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="AnchoringEffect",
        variant="RuleLLM",
        default_config="configs/AnchoringEffect/RuleLLM/simulation.yml",
        phenomenon="Anchoring causes traders to insufficiently adjust from reference prices, creating slow price discovery",
        load_env=True,
    )
