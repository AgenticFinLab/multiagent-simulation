#!/usr/bin/env python
"""SVBBankRun RuleLLM Simulation Runner.

Usage::

    python examples/SVBBankRun/RuleLLM/run_svbbankrun_rulellm.py \
        -c configs/SVBBankRun/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="SVBBankRun",
        variant="RuleLLM",
        default_config="configs/SVBBankRun/RuleLLM/simulation.yml",
        phenomenon="March 2023 SVB collapse - $42B deposit outflow triggered by social media panic",
        load_env=True,
    )
