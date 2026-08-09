#!/usr/bin/env python
"""FlashCrash2010 Rule-Based Simulation Runner.

Usage::

    python examples/FlashCrash2010/Rule/run_flashcrash2010.py \
        -c configs/FlashCrash2010/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash2010",
        variant="Rule-Based",
        default_config="configs/FlashCrash2010/Rule/simulation.yml",
        phenomenon="May 6, 2010 Flash Crash - Dow dropped 1000 points in minutes",
        load_env=False,
    )
