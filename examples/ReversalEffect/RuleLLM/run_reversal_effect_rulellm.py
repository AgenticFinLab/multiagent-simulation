#!/usr/bin/env python
"""ReversalEffect RuleLLM Simulation Runner.

Usage::

    python examples/ReversalEffect/RuleLLM/run_reversal_effect_rulellm.py \
        -c configs/ReversalEffect/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ReversalEffect",
        variant="RuleLLM",
        default_config="configs/ReversalEffect/RuleLLM/simulation.yml",
        phenomenon="Past losers outperform past winners over 3-5 year horizons",
        load_env=True,
    )
