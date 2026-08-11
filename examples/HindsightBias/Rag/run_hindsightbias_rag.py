#!/usr/bin/env python
"""HindsightBias Rag Simulation Runner.

Usage::

    python examples/HindsightBias/Rag/run_hindsightbias_rag.py \
        -c configs/HindsightBias/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HindsightBias",
        variant="Rag",
        default_config="configs/HindsightBias/Rag/simulation.yml",
        phenomenon="Hindsight bias leads to overconfident future predictions based on known outcomes",
        load_env=True,
    )
