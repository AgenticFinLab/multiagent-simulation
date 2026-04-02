"""ReversalEffectLLM Analysis - Mean Reversion Evaluation (LLM Version)

Analyzes reversal effect in LLM-driven agents.
Uses same methodology as rule-based ReversalEffect.

Usage:
    python examples/ReversalEffect/LLM/analysis.py -c configs/ReversalEffect/LLM/simulation.yml

See examples/ReversalEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ReversalEffect.analysis import (
    analyze_reversal,
    _load_data,
)


def main():
    """Run reversal analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze ReversalEffectLLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    # Load config and derive paths
    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("ReversalEffectLLM Analysis - Mean Reversion (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_reversal(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
