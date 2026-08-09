#!/usr/bin/env python
"""StatusQuoBias LLM Simulation Runner.

Usage::

    python examples/StatusQuoBias/LLM/run_statusquobias_llm.py \
        -c configs/StatusQuoBias/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="StatusQuoBias",
        variant="LLM",
        default_config="configs/StatusQuoBias/LLM/simulation.yml",
        phenomenon="Psychological inertia suppresses portfolio rebalancing, causing persistent mispricing",
        load_env=True,
    )
