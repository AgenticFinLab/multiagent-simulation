#!/usr/bin/env python
"""VolatilityClustering RuleLLM Simulation Runner.

Usage::

    python examples/VolatilityClustering/RuleLLM/run_volatility_clustering_rulellm.py \
        -c configs/VolatilityClustering/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="VolatilityClustering",
        variant="RuleLLM",
        default_config="configs/VolatilityClustering/RuleLLM/simulation.yml",
        phenomenon="GARCH-like volatility persistence and clustering",
        load_env=True,
    )
