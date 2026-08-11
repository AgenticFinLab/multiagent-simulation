#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Analysis (thin shim).

Usage:
    python examples/ArchegosCollapse/LLM/analysis.py -c configs/ArchegosCollapse/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.ArchegosCollapse.Rule.analysis import _load_data, analyze_archegos_collapse

if __name__ == "__main__":
    run_llm_analysis(
        scenario="ArchegosCollapse",
        default_config="configs/ArchegosCollapse/LLM/simulation.yml",
        analyze_fn=analyze_archegos_collapse,
        load_data_fn=_load_data,
    )
