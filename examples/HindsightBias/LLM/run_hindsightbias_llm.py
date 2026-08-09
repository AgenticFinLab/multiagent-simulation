#!/usr/bin/env python
"""HindsightBias LLM Simulation Runner.

Usage::

    python examples/HindsightBias/LLM/run_hindsightbias_llm.py \
        -c configs/HindsightBias/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HindsightBias",
        variant="LLM",
        default_config="configs/HindsightBias/LLM/simulation.yml",
        phenomenon="Hindsight bias leads to overconfident future predictions based on known outcomes",
        load_env=True,
    )
