#!/usr/bin/env python
"""FlashCrash LLM Simulation Runner.

Usage::

    python examples/FlashCrash/LLM/run_flash_crash_llm.py \
        -c configs/FlashCrash/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash",
        variant="LLM",
        default_config="configs/FlashCrash/LLM/simulation.yml",
        phenomenon="Extreme rapid price decline with liquidity evaporation",
        load_env=True,
    )
