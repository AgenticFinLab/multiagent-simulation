#!/usr/bin/env python
"""EuropeanDebtCrisis Rule-Based Simulation Runner.

Usage::

    python examples/EuropeanDebtCrisis/Rule/run_europeandebtcrisis.py \
        -c configs/EuropeanDebtCrisis/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="EuropeanDebtCrisis",
        variant="Rule-Based",
        default_config="configs/EuropeanDebtCrisis/Rule/simulation.yml",
        phenomenon="Self-fulfilling creditor panic creates a sovereign doom loop",
        load_env=False,
    )
