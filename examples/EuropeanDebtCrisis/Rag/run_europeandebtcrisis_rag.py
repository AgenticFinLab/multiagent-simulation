#!/usr/bin/env python
"""EuropeanDebtCrisis Rag Simulation Runner.

Usage::

    python examples/EuropeanDebtCrisis/Rag/run_europeandebtcrisis_rag.py \
        -c configs/EuropeanDebtCrisis/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EuropeanDebtCrisis",
        variant="Rag",
        default_config="configs/EuropeanDebtCrisis/Rag/simulation.yml",
        phenomenon="Self-fulfilling creditor panic creates a sovereign doom loop",
        load_env=True,
    )
