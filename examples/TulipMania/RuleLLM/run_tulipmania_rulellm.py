#!/usr/bin/env python
"""TulipMania RuleLLM Simulation Runner.

Usage::

    python examples/TulipMania/RuleLLM/run_tulipmania_rulellm.py \
        -c configs/TulipMania/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="TulipMania",
        variant="RuleLLM",
        default_config="configs/TulipMania/RuleLLM/simulation.yml",
        phenomenon="Trend-chasing and social-proof amplification ratchet prices above fundamentals until crash",
        load_env=True,
    )
