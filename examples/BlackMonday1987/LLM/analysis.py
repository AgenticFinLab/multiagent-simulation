#!/usr/bin/env python
"""BlackMonday1987 LLM Simulation Analysis (thin shim).

Usage:
    python examples/BlackMonday1987/LLM/analysis.py -c configs/BlackMonday1987/LLM/simulation.yml
"""

from masim.evaluation.llm_harness import run_llm_analysis

from examples.BlackMonday1987.Rule.analysis import _load_data, analyze_black_monday

if __name__ == "__main__":
    run_llm_analysis(
        scenario="BlackMonday1987",
        default_config="configs/BlackMonday1987/LLM/simulation.yml",
        analyze_fn=analyze_black_monday,
        load_data_fn=_load_data,
    )
