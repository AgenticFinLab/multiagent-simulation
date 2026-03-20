"""VolatilityClusteringLLM Analysis - GARCH Dynamics Evaluation (LLM Version)

Analyzes volatility clustering in LLM-driven agents.
Uses same methodology as rule-based VolatilityClustering.

Usage:
    python examples/VolatilityClusteringLLM/analysis.py -c configs/VolatilityClusteringLLM/simulation.yml

See examples/VolatilityClustering/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from VolatilityClustering.analysis import (
    analyze_volatility_clustering,
    _load_data,
)


def main():
    """Run volatility clustering analysis for LLM version."""
    parser = argparse.ArgumentParser(
        description="Analyze VolatilityClusteringLLM simulation"
    )
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
    print("VolatilityClusteringLLM Analysis - GARCH Dynamics (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_volatility_clustering(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
