#!/usr/bin/env python
"""ShortSqueeze LLM Simulation Runner.

Usage::

    python examples/ShortSqueeze/LLM/run_short_squeeze_llm.py \
        -c configs/ShortSqueeze/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ShortSqueeze",
        variant="LLM",
        default_config="configs/ShortSqueeze/LLM/simulation.yml",
        phenomenon="Heavily shorted stock rises, forcing short covering cascade",
        load_env=True,
    )
