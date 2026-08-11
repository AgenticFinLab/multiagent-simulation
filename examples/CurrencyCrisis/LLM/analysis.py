#!/usr/bin/env python
"""CurrencyCrisis LLM Simulation Analysis (thin shim).

Usage:
    python examples/CurrencyCrisis/LLM/analysis.py -c configs/CurrencyCrisis/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.CurrencyCrisis.Rule.analysis import _load_data, analyze_currency_crisis

if __name__ == "__main__":
    run_llm_analysis(
        scenario="CurrencyCrisis",
        default_config="configs/CurrencyCrisis/LLM/simulation.yml",
        analyze_fn=analyze_currency_crisis,
        load_data_fn=_load_data,
    )
