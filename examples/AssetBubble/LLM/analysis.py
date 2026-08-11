#!/usr/bin/env python
"""AssetBubble LLM Simulation Analysis (thin shim).

Usage:
    python examples/AssetBubble/LLM/analysis.py -c configs/AssetBubble/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.AssetBubble.Rule.analysis import _load_data, analyze_bubble

if __name__ == "__main__":
    run_llm_analysis(
        scenario="AssetBubble",
        default_config="configs/AssetBubble/LLM/simulation.yml",
        analyze_fn=analyze_bubble,
        load_data_fn=_load_data,
    )
