#!/usr/bin/env python
"""AsianFinancialCrisis Rag Simulation Runner.

Usage::

    python examples/AsianFinancialCrisis/Rag/run_asianfinancialcrisis_rag.py \
        -c configs/AsianFinancialCrisis/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AsianFinancialCrisis",
        variant="Rag",
        default_config="configs/AsianFinancialCrisis/Rag/simulation.yml",
        phenomenon="1997 Asian Financial Crisis - hot money reversal and contagion cascade",
        load_env=True,
    )
