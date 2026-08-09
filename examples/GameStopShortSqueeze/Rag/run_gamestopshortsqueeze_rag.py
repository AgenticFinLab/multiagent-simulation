#!/usr/bin/env python
"""GameStopShortSqueeze Rag Simulation Runner.

Usage::

    python examples/GameStopShortSqueeze/Rag/run_gamestopshortsqueeze_rag.py \
        -c configs/GameStopShortSqueeze/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="GameStopShortSqueeze",
        variant="Rag",
        default_config="configs/GameStopShortSqueeze/Rag/simulation.yml",
        phenomenon="January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase",
        load_env=True,
    )
