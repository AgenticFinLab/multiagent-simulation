#!/usr/bin/env python
"""FlashCrash Rule-Based Simulation Runner.

Usage::

    python examples/FlashCrash/Rule/run_flash_crash.py \
        -c configs/FlashCrash/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="FlashCrash",
        variant="Rule-Based",
        default_config="configs/FlashCrash/Rule/simulation.yml",
        phenomenon="Extreme rapid price decline with liquidity evaporation",
        load_env=False,
    )
