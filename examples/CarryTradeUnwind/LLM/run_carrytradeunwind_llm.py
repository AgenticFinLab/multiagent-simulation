#!/usr/bin/env python
"""CarryTradeUnwind LLM Simulation Runner.

Usage::

    python examples/CarryTradeUnwind/LLM/run_carrytradeunwind_llm.py \
        -c configs/CarryTradeUnwind/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CarryTradeUnwind",
        variant="LLM",
        default_config="configs/CarryTradeUnwind/LLM/simulation.yml",
        phenomenon="Funding-currency appreciation triggers forced deleveraging of crowded carry positions",
        load_env=True,
    )
