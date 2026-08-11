#!/usr/bin/env python
"""AssetBubble RuleLLM Simulation Runner.

Usage::

    python examples/AssetBubble/RuleLLM/run_bubble_rulellm.py \
        -c configs/AssetBubble/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AssetBubble",
        variant="RuleLLM",
        default_config="configs/AssetBubble/RuleLLM/simulation.yml",
        phenomenon="Asset price deviation from fundamental value through heterogeneous agent interactions",
        load_env=True,
    )
