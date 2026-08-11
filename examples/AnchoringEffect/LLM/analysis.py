#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Analysis (thin shim).

Usage:
    python examples/AnchoringEffect/LLM/analysis.py -c configs/AnchoringEffect/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.AnchoringEffect.Rule.analysis import _load_data, analyze_anchoring

if __name__ == "__main__":
    run_llm_analysis(
        scenario="AnchoringEffect",
        default_config="configs/AnchoringEffect/LLM/simulation.yml",
        analyze_fn=analyze_anchoring,
        load_data_fn=_load_data,
        analyze_kwargs={"variant": "LLM"},
    )
