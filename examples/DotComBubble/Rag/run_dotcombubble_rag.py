#!/usr/bin/env python
"""DotComBubble Rag Simulation Runner.

Usage::

    python examples/DotComBubble/Rag/run_dotcombubble_rag.py \
        -c configs/DotComBubble/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="DotComBubble",
        variant="Rag",
        default_config="configs/DotComBubble/Rag/simulation.yml",
        phenomenon="1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%",
        load_env=True,
    )
