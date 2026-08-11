#!/usr/bin/env python
"""CarryTradeUnwind Rule-Based Simulation Runner.

Usage::

    python examples/CarryTradeUnwind/Rule/run_carrytradeunwind_rule.py \
        -c configs/CarryTradeUnwind/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="CarryTradeUnwind",
        variant="Rule-Based",
        default_config="configs/CarryTradeUnwind/Rule/simulation.yml",
        phenomenon="Funding-currency appreciation triggers forced deleveraging of crowded carry positions",
        load_env=False,
    )
