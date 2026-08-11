#!/usr/bin/env python
"""SVBBankRun Rag Simulation Runner.

Usage::

    python examples/SVBBankRun/Rag/run_svbbankrun_rag.py \
        -c configs/SVBBankRun/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SVBBankRun",
        variant="Rag",
        default_config="configs/SVBBankRun/Rag/simulation.yml",
        phenomenon="March 2023 SVB collapse - $42B deposit outflow triggered by social media panic",
        load_env=True,
    )
