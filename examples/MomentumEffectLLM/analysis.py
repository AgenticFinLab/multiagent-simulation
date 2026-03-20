"""MomentumEffectLLM Analysis - Price Continuation Evaluation (LLM Version)

Analyzes momentum effect in LLM-driven agents.
Uses same methodology as rule-based MomentumEffect.

Usage:
    python examples/MomentumEffectLLM/analysis.py -c configs/MomentumEffectLLM/simulation.yml

See examples/MomentumEffect/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MomentumEffect.analysis import (
    analyze_momentum,
    _load_data,
)


def main():
    """Run momentum analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze MomentumEffectLLM simulation")
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
    print("MomentumEffectLLM Analysis - Price Continuation (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_momentum(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
