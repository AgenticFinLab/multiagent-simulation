#!/usr/bin/env python
"""DotComBubble LLM Simulation Runner.

Usage::

    python examples/DotComBubble/LLM/run_dotcombubble_llm.py \
        -c configs/DotComBubble/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="DotComBubble",
        variant="LLM",
        default_config="configs/DotComBubble/LLM/simulation.yml",
        phenomenon="1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%",
        load_env=True,
    )
