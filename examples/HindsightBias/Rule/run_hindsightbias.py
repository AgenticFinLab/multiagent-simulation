#!/usr/bin/env python
"""HindsightBias Rule-Based Simulation Runner.

Usage::

    python examples/HindsightBias/Rule/run_hindsightbias.py \
        -c configs/HindsightBias/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HindsightBias",
        variant="Rule-Based",
        default_config="configs/HindsightBias/Rule/simulation.yml",
        phenomenon="Hindsight bias leads to overconfident future predictions based on known outcomes",
        load_env=False,
    )
