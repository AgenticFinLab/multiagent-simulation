#!/usr/bin/env python
"""CurrencyCrisis RuleLLM Simulation Runner.

Usage::

    python examples/CurrencyCrisis/RuleLLM/run_currencycrisis_rulellm.py \
        -c configs/CurrencyCrisis/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CurrencyCrisis",
        variant="RuleLLM",
        default_config="configs/CurrencyCrisis/RuleLLM/simulation.yml",
        phenomenon="Self-fulfilling speculative attacks deplete central-bank reserves and force peg abandonment",
        load_env=True,
    )
