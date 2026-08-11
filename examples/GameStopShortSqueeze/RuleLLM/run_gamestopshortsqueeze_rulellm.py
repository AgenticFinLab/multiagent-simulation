#!/usr/bin/env python
"""GameStopShortSqueeze RuleLLM Simulation Runner.

Usage::

    python examples/GameStopShortSqueeze/RuleLLM/run_gamestopshortsqueeze_rulellm.py \
        -c configs/GameStopShortSqueeze/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="GameStopShortSqueeze",
        variant="RuleLLM",
        default_config="configs/GameStopShortSqueeze/RuleLLM/simulation.yml",
        phenomenon="January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase",
        load_env=True,
    )
