#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Analysis (registry-driven thin wrapper).

All metric mathematics live in :mod:`examples.AnchoringEffect.metrics`. The
analysis pipeline (data load, metric computation, validation, dashboards) is
implemented once in :mod:`examples.AnchoringEffect.Rule.analysis`. This module
adds the variant label so the LLM run gets its own ``summary.json`` and titled
plots, and augments that ``summary.json`` with the required LLM
``action-distribution`` audit block (implement-simulation-skill §7.2).

LLM-specific notes (analysis-bases.md §4):
    * Metric values may show higher variance than Rule due to stochastic LLM
      decisions.
    * Persona Consistency Drift and Narrative Framing Effects are LLM-specific
      observables surfaced through ``investor_payloads`` reasoning fields.

Usage::

    python examples/AnchoringEffect/LLM/analysis.py \
        -c configs/AnchoringEffect/LLM/simulation.yml
"""

import argparse
import json
import os

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution

from examples.AnchoringEffect.Rule.analysis import (
    _load_data,
    analyze_anchoring,
)

VARIANT = "LLM"


def main() -> None:
    """Run full AnchoringEffect LLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect LLM simulation results"
    )
    parser.add_argument(
        "-c", "--config", type=str, required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_anchoring(data, config, output_dir, variant=VARIANT)

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


if __name__ == "__main__":
    main()


__all__ = [
    "analyze_action_distribution",
    "main",
]
