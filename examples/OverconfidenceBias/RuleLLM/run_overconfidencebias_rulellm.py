#!/usr/bin/env python
"""OverconfidenceBias RuleLLM Simulation Runner.

Usage::

    python examples/OverconfidenceBias/RuleLLM/run_overconfidencebias_rulellm.py \
        -c configs/OverconfidenceBias/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="OverconfidenceBias",
        variant="RuleLLM",
        default_config="configs/OverconfidenceBias/RuleLLM/simulation.yml",
        phenomenon="Overconfidence bias causes traders to overestimate precision and trade excessively",
        load_env=True,
    )
