#!/usr/bin/env python
"""SVBBankRun LLM Simulation Runner.

Usage::

    python examples/SVBBankRun/LLM/run_svbbankrun_llm.py \
        -c configs/SVBBankRun/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="SVBBankRun",
        variant="LLM",
        default_config="configs/SVBBankRun/LLM/simulation.yml",
        phenomenon="March 2023 SVB collapse - $42B deposit outflow triggered by social media panic",
        load_env=True,
    )
