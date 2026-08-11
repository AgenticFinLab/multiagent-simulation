#!/usr/bin/env python
"""FramingEffect LLM Simulation Analysis (thin shim).

Usage:
    python examples/FramingEffect/LLM/analysis.py -c configs/FramingEffect/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.FramingEffect.Rule.analysis import _load_data, analyze_framingeffect

if __name__ == "__main__":
    run_llm_analysis(
        scenario="FramingEffect",
        default_config="configs/FramingEffect/LLM/simulation.yml",
        analyze_fn=analyze_framingeffect,
        load_data_fn=_load_data,
        analyze_kwargs={"variant": "LLM"},
    )
