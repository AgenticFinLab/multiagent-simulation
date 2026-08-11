#!/usr/bin/env python
"""ReversalEffect LLM Simulation Runner.

Usage::

    python examples/ReversalEffect/LLM/run_reversal_llm.py \
        -c configs/ReversalEffect/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="ReversalEffect",
        variant="LLM",
        default_config="configs/ReversalEffect/LLM/simulation.yml",
        phenomenon="Past losers outperform past winners over 3-5 year horizons",
        load_env=True,
    )
