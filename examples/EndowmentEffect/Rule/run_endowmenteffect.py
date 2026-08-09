#!/usr/bin/env python
"""EndowmentEffect Rule-Based Simulation Runner.

Usage::

    python examples/EndowmentEffect/Rule/run_endowmenteffect.py \
        -c configs/EndowmentEffect/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EndowmentEffect",
        variant="Rule-Based",
        default_config="configs/EndowmentEffect/Rule/simulation.yml",
        phenomenon="Ownership-induced loss aversion suppresses trade volume and inflates transaction prices",
        load_env=False,
    )
