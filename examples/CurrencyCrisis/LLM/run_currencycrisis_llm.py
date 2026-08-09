#!/usr/bin/env python
"""CurrencyCrisis LLM Simulation Runner.

Usage::

    python examples/CurrencyCrisis/LLM/run_currencycrisis_llm.py \
        -c configs/CurrencyCrisis/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CurrencyCrisis",
        variant="LLM",
        default_config="configs/CurrencyCrisis/LLM/simulation.yml",
        phenomenon="Self-fulfilling speculative attacks deplete central-bank reserves and force peg abandonment",
        load_env=True,
    )
