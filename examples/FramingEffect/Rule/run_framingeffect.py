#!/usr/bin/env python
"""FramingEffect Rule-Based Simulation Runner.

Usage::

    python examples/FramingEffect/Rule/run_framingeffect.py \
        -c configs/FramingEffect/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FramingEffect",
        variant="Rule-Based",
        default_config="configs/FramingEffect/Rule/simulation.yml",
        phenomenon="Gain/loss frames elicit asymmetric risk attitudes, generating bias-driven order flow",
        load_env=False,
    )
