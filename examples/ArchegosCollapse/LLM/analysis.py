#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Analysis

LLM-variant analysis for the ArchegosCollapse simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §4): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline.

Usage:
    python examples/ArchegosCollapse/LLM/analysis.py \\
        -c configs/ArchegosCollapse/LLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.ArchegosCollapse.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_archegos_collapse,
    _build_interpretation,
    analyze_archegos_collapse,
)


def main() -> None:
    """Run full ArchegosCollapse LLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_archegos_collapse().
    LLM-variant note: stochastic decisions may produce higher variance in
    drawdown depth and cascade timing vs. Rule baseline.
    """
    parser = argparse.ArgumentParser(
        description="Analyze ArchegosCollapse LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)

    summary = analyze_archegos_collapse(data, config, output_dir)
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
