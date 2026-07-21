"""Analysis utilities for the FramingEffect LLM variant.

Thin wrapper around :mod:`examples.FramingEffect.Rule.analysis`. The Rule
variant is the calibration anchor and single source of truth for metric
mathematics, validation, and dashboard rendering (analysis-bases.md).
This module only differs in (a) the config it loads and (b) the ``variant``
label stamped into ``summary.json`` and every panel title.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution

from examples.FramingEffect.Rule.analysis import (
    STANDARD_OUTPUT_FILES,
    _load_data,
    analyze_framingeffect,
    calculate_metrics,
    compute_all_metrics,
    create_visualizations,
    framing_asymmetry_ratio,
    framing_deviation_index,
    framing_volume_impact,
    load_simulation_data,
    rational_correction_efficiency,
    volatility_amplification_factor,
    wealth_distribution_index,
)


def main() -> Dict[str, Any]:
    """Run FramingEffect LLM analysis (rich 9-panel dashboard)."""
    parser = argparse.ArgumentParser(description="Analyze FramingEffect LLM simulation")
    parser.add_argument(
        "-c", "--config", type=str,
        default="configs/FramingEffect/LLM/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_framingeffect(data, config, output_dir, variant="LLM")

    # implement-simulation-skill §7.2 — LLM variants must expose an
    # action-distribution audit and inject it into summary.json.
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
    return summary


__all__ = [
    "framing_deviation_index",
    "framing_asymmetry_ratio",
    "framing_volume_impact",
    "rational_correction_efficiency",
    "volatility_amplification_factor",
    "wealth_distribution_index",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "compute_all_metrics",
    "analyze_framingeffect",
    "analyze_action_distribution",
    "STANDARD_OUTPUT_FILES",
    "main",
]


if __name__ == "__main__":
    main()
