"""VolatilityClusteringRag Analysis — VolatilityClustering Dynamics Evaluation (RAG+LLM Variant)

Analyzes volatility clustering dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based VolatilityClustering,
reusing the shared analysis pipeline from VolatilityClustering/analysis.py.

Usage:
    python examples/VolatilityClustering/Rag/analysis.py -c configs/VolatilityClustering/Rag/simulation.yml

See examples/VolatilityClustering/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.VolatilityClustering.Rule.analysis import (
    analyze_volatility_clustering,
    _load_data,
)


def main():
    """Run volatility clustering analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze VolatilityClusteringRag simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print(
        "VolatilityClusteringRag Analysis - VolatilityClustering Dynamics (RAG+LLM Agents)"
    )
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_volatility_clustering(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
