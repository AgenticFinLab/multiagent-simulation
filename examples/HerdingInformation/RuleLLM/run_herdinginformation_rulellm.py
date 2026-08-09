#!/usr/bin/env python
"""HerdingInformation RuleLLM Simulation Runner.

Usage::

    python examples/HerdingInformation/RuleLLM/run_herdinginformation_rulellm.py \
        -c configs/HerdingInformation/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HerdingInformation",
        variant="RuleLLM",
        default_config="configs/HerdingInformation/RuleLLM/simulation.yml",
        phenomenon="Information cascade - individuals ignore private signals and follow the crowd",
        load_env=True,
    )
