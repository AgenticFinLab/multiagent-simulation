#!/usr/bin/env python
"""TulipMania Rag Simulation Runner.

Usage::

    python examples/TulipMania/Rag/run_tulipmania_rag.py \
        -c configs/TulipMania/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="TulipMania",
        variant="Rag",
        default_config="configs/TulipMania/Rag/simulation.yml",
        phenomenon="Trend-chasing and social-proof amplification ratchet prices above fundamentals until crash",
        load_env=True,
    )
