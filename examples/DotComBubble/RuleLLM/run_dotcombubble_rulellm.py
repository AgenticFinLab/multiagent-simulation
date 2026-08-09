#!/usr/bin/env python
"""DotComBubble RuleLLM Simulation Runner.

Usage::

    python examples/DotComBubble/RuleLLM/run_dotcombubble_rulellm.py \
        -c configs/DotComBubble/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="DotComBubble",
        variant="RuleLLM",
        default_config="configs/DotComBubble/RuleLLM/simulation.yml",
        phenomenon="1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%",
        load_env=True,
    )
