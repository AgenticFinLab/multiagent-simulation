#!/usr/bin/env python
"""HindsightBias RuleLLM Simulation Runner.

Usage::

    python examples/HindsightBias/RuleLLM/run_hindsightbias_rulellm.py \
        -c configs/HindsightBias/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HindsightBias",
        variant="RuleLLM",
        default_config="configs/HindsightBias/RuleLLM/simulation.yml",
        phenomenon="Hindsight bias leads to overconfident future predictions based on known outcomes",
        load_env=True,
    )
