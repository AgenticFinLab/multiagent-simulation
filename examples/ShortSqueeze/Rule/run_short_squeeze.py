#!/usr/bin/env python
"""ShortSqueeze Rule-Based Simulation Runner.

Usage::

    python examples/ShortSqueeze/Rule/run_short_squeeze.py \
        -c configs/ShortSqueeze/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="ShortSqueeze",
        variant="Rule-Based",
        default_config="configs/ShortSqueeze/Rule/simulation.yml",
        phenomenon="Heavily shorted stock rises, forcing short covering cascade",
        load_env=False,
    )
