#!/usr/bin/env python
"""FlashCrash2010 RuleLLM Simulation Runner.

Usage::

    python examples/FlashCrash2010/RuleLLM/run_flashcrash2010_rulellm.py \
        -c configs/FlashCrash2010/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash2010",
        variant="RuleLLM",
        default_config="configs/FlashCrash2010/RuleLLM/simulation.yml",
        phenomenon="May 6, 2010 Flash Crash - Dow dropped 1000 points in minutes",
        load_env=True,
    )
