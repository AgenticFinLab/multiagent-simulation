#!/usr/bin/env python
"""TulipMania LLM Simulation Runner.

Usage::

    python examples/TulipMania/LLM/run_tulipmania_llm.py \
        -c configs/TulipMania/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="TulipMania",
        variant="LLM",
        default_config="configs/TulipMania/LLM/simulation.yml",
        phenomenon="Trend-chasing and social-proof amplification ratchet prices above fundamentals until crash",
        load_env=True,
    )
