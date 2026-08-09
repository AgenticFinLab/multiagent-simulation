#!/usr/bin/env python
"""HerdEffect RuleLLM Simulation Runner.

Usage::

    python examples/HerdEffect/RuleLLM/run_herd_rulellm.py \
        -c configs/HerdEffect/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HerdEffect",
        variant="RuleLLM",
        default_config="configs/HerdEffect/RuleLLM/simulation.yml",
        phenomenon="Emergent herding from heterogeneous investors converging on shared price-return signals",
        load_env=True,
    )
