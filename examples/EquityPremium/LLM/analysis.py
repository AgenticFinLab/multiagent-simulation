#!/usr/bin/env python
"""EquityPremium LLM Simulation Analysis (thin shim).

Usage:
    python examples/EquityPremium/LLM/analysis.py -c configs/EquityPremium/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.EquityPremium.Rule.analysis import _load_data, analyze_equity_premium

if __name__ == "__main__":
    run_llm_analysis(
        scenario="EquityPremium",
        default_config="configs/EquityPremium/LLM/simulation.yml",
        analyze_fn=analyze_equity_premium,
        load_data_fn=_load_data,
    )
