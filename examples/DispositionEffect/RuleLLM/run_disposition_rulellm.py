#!/usr/bin/env python
"""DispositionEffect RuleLLM Simulation Runner.

Usage::

    python examples/DispositionEffect/RuleLLM/run_disposition_rulellm.py \
        -c configs/DispositionEffect/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="DispositionEffect",
        variant="RuleLLM",
        default_config="configs/DispositionEffect/RuleLLM/simulation.yml",
        phenomenon="Loss aversion causes investors to sell winners too early and hold losers too long",
        load_env=True,
    )
