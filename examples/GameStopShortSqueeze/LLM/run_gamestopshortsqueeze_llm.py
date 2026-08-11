#!/usr/bin/env python
"""GameStopShortSqueeze LLM Simulation Runner.

Usage::

    python examples/GameStopShortSqueeze/LLM/run_gamestopshortsqueeze_llm.py \
        -c configs/GameStopShortSqueeze/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GameStopShortSqueeze",
        variant="LLM",
        default_config="configs/GameStopShortSqueeze/LLM/simulation.yml",
        phenomenon="January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase",
        load_env=True,
    )
