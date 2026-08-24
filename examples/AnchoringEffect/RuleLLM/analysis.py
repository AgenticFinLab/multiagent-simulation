#!/usr/bin/env python
"""AnchoringEffect RuleLLM Simulation Analysis (thin wrapper).

All metric mathematics live in :mod:`examples.AnchoringEffect.metrics`; the
analysis pipeline (data load -> registry metrics -> validation -> dashboards
-> universal summary) is implemented once in
:mod:`examples.AnchoringEffect.Rule.analysis` and shared via
:func:`run_anchoring_analysis`.  This module supplies only the variant label.

Usage::

    python examples/AnchoringEffect/RuleLLM/analysis.py \\
        -c configs/AnchoringEffect/RuleLLM/simulation.yml
"""

import argparse

from examples.AnchoringEffect.Rule.analysis import run_anchoring_analysis

VARIANT = "RuleLLM"


def main() -> None:
    """Run the full AnchoringEffect RuleLLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect RuleLLM simulation results"
    )
    parser.add_argument(
        "-c", "--config", type=str, required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()
    return run_anchoring_analysis(args.config, VARIANT)


if __name__ == "__main__":
    main()
