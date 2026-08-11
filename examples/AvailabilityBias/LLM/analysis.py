#!/usr/bin/env python
"""AvailabilityBias LLM Simulation Analysis (thin shim).

Usage:
    python examples/AvailabilityBias/LLM/analysis.py -c configs/AvailabilityBias/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.AvailabilityBias.Rule.analysis import _load_data, analyze_availability_bias

if __name__ == "__main__":
    run_llm_analysis(
        scenario="AvailabilityBias",
        default_config="configs/AvailabilityBias/LLM/simulation.yml",
        analyze_fn=analyze_availability_bias,
        load_data_fn=_load_data,
    )
