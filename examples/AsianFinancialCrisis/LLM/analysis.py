#!/usr/bin/env python
"""AsianFinancialCrisis LLM Simulation Analysis (thin shim).

Usage:
    python examples/AsianFinancialCrisis/LLM/analysis.py -c configs/AsianFinancialCrisis/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.AsianFinancialCrisis.Rule.analysis import (
    _load_data,
    analyze_asian_financial_crisis,
)

if __name__ == "__main__":
    run_llm_analysis(
        scenario="AsianFinancialCrisis",
        default_config="configs/AsianFinancialCrisis/LLM/simulation.yml",
        analyze_fn=analyze_asian_financial_crisis,
        load_data_fn=_load_data,
    )
