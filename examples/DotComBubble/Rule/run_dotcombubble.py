#!/usr/bin/env python
"""DotComBubble Rule-Based Simulation Runner.

Usage::

    python examples/DotComBubble/Rule/run_dotcombubble.py \
        -c configs/DotComBubble/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="DotComBubble",
        variant="Rule-Based",
        default_config="configs/DotComBubble/Rule/simulation.yml",
        phenomenon="1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%",
        load_env=False,
    )
