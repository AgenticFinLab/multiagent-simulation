#!/usr/bin/env python
"""SVBBankRun Rule-Based Simulation Runner.

Usage::

    python examples/SVBBankRun/Rule/run_svbbankrun.py \
        -c configs/SVBBankRun/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SVBBankRun",
        variant="Rule-Based",
        default_config="configs/SVBBankRun/Rule/simulation.yml",
        phenomenon="March 2023 SVB collapse - $42B deposit outflow triggered by social media panic",
        load_env=False,
    )
