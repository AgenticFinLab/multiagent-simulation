#!/usr/bin/env python
"""AnchoringEffect RuleLLM Simulation Analysis (registry-driven thin wrapper).

The RuleLLM variant blends rule-based and LLM-driven personae. All metric
mathematics live in :mod:`examples.AnchoringEffect.metrics`; the analysis
pipeline (data load → registry metrics → validation → 9-panel dashboards
→ 36-metric Layer A + universal PNGs → summary.json) is implemented once
in :mod:`examples.AnchoringEffect.Rule.analysis` and reused verbatim. This
module supplies only the variant label.

Usage::

    python examples/AnchoringEffect/RuleLLM/analysis.py \
        -c configs/AnchoringEffect/RuleLLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.AnchoringEffect.Rule.analysis import (
    _load_data,
    analyze_anchoring,
)

VARIANT = "RuleLLM"


def main() -> None:
    """Run full AnchoringEffect RuleLLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect RuleLLM simulation results"
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
