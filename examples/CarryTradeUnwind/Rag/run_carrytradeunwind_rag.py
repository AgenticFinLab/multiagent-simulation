#!/usr/bin/env python
"""CarryTradeUnwind Rag Simulation Runner.

Usage::

    python examples/CarryTradeUnwind/Rag/run_carrytradeunwind_rag.py \
        -c configs/CarryTradeUnwind/Rag/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="CarryTradeUnwind",
        variant="Rag",
        default_config="configs/CarryTradeUnwind/Rag/simulation.yml",
        phenomenon="Funding-currency appreciation triggers forced deleveraging of crowded carry positions",
        load_env=True,
    )
