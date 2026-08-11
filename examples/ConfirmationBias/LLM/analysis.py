#!/usr/bin/env python
"""ConfirmationBias LLM Simulation Analysis (thin shim).

Usage:
    python examples/ConfirmationBias/LLM/analysis.py -c configs/ConfirmationBias/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.ConfirmationBias.Rule.analysis import _load_data, analyze_confirmation_bias

if __name__ == "__main__":
    run_llm_analysis(
        scenario="ConfirmationBias",
        default_config="configs/ConfirmationBias/LLM/simulation.yml",
        analyze_fn=analyze_confirmation_bias,
        load_data_fn=_load_data,
    )
