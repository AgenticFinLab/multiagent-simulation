#!/usr/bin/env python
"""SouthSeaBubble LLM Simulation Runner.

Usage::

    python examples/SouthSeaBubble/LLM/run_southseabubble_llm.py \
        -c configs/SouthSeaBubble/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SouthSeaBubble",
        variant="LLM",
        default_config="configs/SouthSeaBubble/LLM/simulation.yml",
        phenomenon="Politically endorsed monopoly narratives inflate prices until insider exit triggers collapse",
        load_env=True,
    )
