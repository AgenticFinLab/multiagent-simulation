#!/usr/bin/env python
"""AsianFinancialCrisis LLM Simulation Runner.

Usage::

    python examples/AsianFinancialCrisis/LLM/run_asianfinancialcrisis_llm.py \
        -c configs/AsianFinancialCrisis/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="AsianFinancialCrisis",
        variant="LLM",
        default_config="configs/AsianFinancialCrisis/LLM/simulation.yml",
        phenomenon="1997 Asian Financial Crisis - hot money reversal and contagion cascade",
        load_env=True,
    )
