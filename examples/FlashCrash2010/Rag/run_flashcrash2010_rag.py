#!/usr/bin/env python
"""FlashCrash2010 Rag Simulation Runner.

Usage::

    python examples/FlashCrash2010/Rag/run_flashcrash2010_rag.py \
        -c configs/FlashCrash2010/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash2010",
        variant="Rag",
        default_config="configs/FlashCrash2010/Rag/simulation.yml",
        phenomenon="May 6, 2010 Flash Crash - Dow dropped 1000 points in minutes",
        load_env=True,
    )
