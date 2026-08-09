#!/usr/bin/env python
"""ShortSqueeze RuleLLM Simulation Runner.

Usage::

    python examples/ShortSqueeze/RuleLLM/run_short_squeeze_rulellm.py \
        -c configs/ShortSqueeze/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ShortSqueeze",
        variant="RuleLLM",
        default_config="configs/ShortSqueeze/RuleLLM/simulation.yml",
        phenomenon="Heavily shorted stock rises, forcing short covering cascade",
        load_env=True,
    )
