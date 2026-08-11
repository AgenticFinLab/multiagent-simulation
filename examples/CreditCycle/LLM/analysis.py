#!/usr/bin/env python
"""CreditCycle LLM Simulation Analysis (thin shim).

Usage:
    python examples/CreditCycle/LLM/analysis.py -c configs/CreditCycle/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.CreditCycle.Rule.analysis import _load_data, analyze_credit_cycle

if __name__ == "__main__":
    run_llm_analysis(
        scenario="CreditCycle",
        default_config="configs/CreditCycle/LLM/simulation.yml",
        analyze_fn=analyze_credit_cycle,
        load_data_fn=_load_data,
    )
