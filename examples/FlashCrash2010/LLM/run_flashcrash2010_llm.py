#!/usr/bin/env python
"""FlashCrash2010 LLM Simulation Runner.

Usage::

    python examples/FlashCrash2010/LLM/run_flashcrash2010_llm.py \
        -c configs/FlashCrash2010/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash2010",
        variant="LLM",
        default_config="configs/FlashCrash2010/LLM/simulation.yml",
        phenomenon="May 6, 2010 Flash Crash - Dow dropped 1000 points in minutes",
        load_env=True,
    )
