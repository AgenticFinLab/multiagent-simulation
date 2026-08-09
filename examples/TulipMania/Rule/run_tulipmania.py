#!/usr/bin/env python
"""TulipMania Rule-Based Simulation Runner.

Usage::

    python examples/TulipMania/Rule/run_tulipmania.py \
        -c configs/TulipMania/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="TulipMania",
        variant="Rule-Based",
        default_config="configs/TulipMania/Rule/simulation.yml",
        phenomenon="Trend-chasing and social-proof amplification ratchet prices above fundamentals until crash",
        load_env=False,
    )
