#!/usr/bin/env python
"""CarryTradeUnwind LLM Simulation Analysis (thin shim).

Usage:
    python examples/CarryTradeUnwind/LLM/analysis.py -c configs/CarryTradeUnwind/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.CarryTradeUnwind.Rule.analysis import _load_data, analyze_carry_trade_unwind

if __name__ == "__main__":
    run_llm_analysis(
        scenario="CarryTradeUnwind",
        default_config="configs/CarryTradeUnwind/LLM/simulation.yml",
        analyze_fn=analyze_carry_trade_unwind,
        load_data_fn=_load_data,
    )
