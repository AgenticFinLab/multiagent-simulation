#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Analysis

LLM-variant analysis for the ArchegosCollapse simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §4): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline.

Additionally injects the LLM ``action-distribution`` audit required by
``implement-simulation-skill §7.2`` into ``summary.json``.

Usage:
    python examples/ArchegosCollapse/LLM/analysis.py \\
        -c configs/ArchegosCollapse/LLM/simulation.yml
"""

import argparse
import json
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution
from masim.evaluation import write_universal_summary

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

    action_dist = analyze_action_distribution(results)
    summary_path = os.path.join(output_dir, "summary.json")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            persisted = json.load(f)
    except (OSError, ValueError):
        persisted = summary if isinstance(summary, dict) else {}
    persisted["llm_action_distribution"] = action_dist
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(persisted, f, indent=2, default=str)
    if isinstance(summary, dict):
        summary["llm_action_distribution"] = action_dist
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'LLM'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='ArchegosCollapse',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["analyze_action_distribution", "main"]

if __name__ == "__main__":
    main()
