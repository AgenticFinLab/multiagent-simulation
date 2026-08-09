#!/usr/bin/env python
"""SouthSeaBubble RuleLLM Simulation Runner.

Usage::

    python examples/SouthSeaBubble/RuleLLM/run_southseabubble_rulellm.py \
        -c configs/SouthSeaBubble/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SouthSeaBubble",
        variant="RuleLLM",
        default_config="configs/SouthSeaBubble/RuleLLM/simulation.yml",
        phenomenon="Politically endorsed monopoly narratives inflate prices until insider exit triggers collapse",
        load_env=True,
    )
