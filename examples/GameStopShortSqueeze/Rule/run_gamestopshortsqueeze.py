#!/usr/bin/env python
"""GameStopShortSqueeze Rule-Based Simulation Runner.

Usage::

    python examples/GameStopShortSqueeze/Rule/run_gamestopshortsqueeze.py \
        -c configs/GameStopShortSqueeze/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GameStopShortSqueeze",
        variant="Rule-Based",
        default_config="configs/GameStopShortSqueeze/Rule/simulation.yml",
        phenomenon="January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase",
        load_env=False,
    )
