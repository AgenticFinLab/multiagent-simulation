#!/usr/bin/env python
"""BlackMonday1987 RuleLLM Simulation Runner.

Usage::

    python examples/BlackMonday1987/RuleLLM/run_blackmonday1987_rulellm.py \
        -c configs/BlackMonday1987/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="BlackMonday1987",
        variant="RuleLLM",
        default_config="configs/BlackMonday1987/RuleLLM/simulation.yml",
        phenomenon="October 19, 1987 stock market crash - Dow fell 22.6% in one day",
        load_env=True,
    )
