#!/usr/bin/env python
"""StatusQuoBias RuleLLM Simulation Runner.

Usage::

    python examples/StatusQuoBias/RuleLLM/run_statusquobias_rulellm.py \
        -c configs/StatusQuoBias/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="StatusQuoBias",
        variant="RuleLLM",
        default_config="configs/StatusQuoBias/RuleLLM/simulation.yml",
        phenomenon="Psychological inertia suppresses portfolio rebalancing, causing persistent mispricing",
        load_env=True,
    )
