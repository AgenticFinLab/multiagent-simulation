#!/usr/bin/env python
"""AssetBubble Rule-Based Simulation Runner.

Usage::

    python examples/AssetBubble/Rule/run_bubble.py \
        -c configs/AssetBubble/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="AssetBubble",
        variant="Rule-Based",
        default_config="configs/AssetBubble/Rule/simulation.yml",
        phenomenon="Asset price deviation from fundamental value through heterogeneous agent interactions",
        load_env=False,
    )
