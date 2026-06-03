#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Analysis (registry-driven thin wrapper).

All metric mathematics live in :mod:`examples.AnchoringEffect.metrics`. The
analysis pipeline (data load, metric computation, validation, dashboards) is
implemented once in :mod:`examples.AnchoringEffect.Rule.analysis`. This module
adds the variant label so the LLM run gets its own ``summary.json`` and titled
plots.

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
import os

from masim.utils import load_config, load_results

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
    return analyze_anchoring(data, config, output_dir, variant=VARIANT)


if __name__ == "__main__":
    main()
