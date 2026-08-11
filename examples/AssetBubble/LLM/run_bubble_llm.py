#!/usr/bin/env python
"""AssetBubble LLM Simulation Runner.

Usage::

    python examples/AssetBubble/LLM/run_bubble_llm.py \
        -c configs/AssetBubble/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AssetBubble",
        variant="LLM",
        default_config="configs/AssetBubble/LLM/simulation.yml",
        phenomenon="Asset price deviation from fundamental value through heterogeneous agent interactions",
        load_env=True,
    )
