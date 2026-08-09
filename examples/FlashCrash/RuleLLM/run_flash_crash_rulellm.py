#!/usr/bin/env python
"""FlashCrash RuleLLM Simulation Runner.

Usage::

    python examples/FlashCrash/RuleLLM/run_flash_crash_rulellm.py \
        -c configs/FlashCrash/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash",
        variant="RuleLLM",
        default_config="configs/FlashCrash/RuleLLM/simulation.yml",
        phenomenon="Extreme rapid price decline with liquidity evaporation",
        load_env=True,
    )
