"""EquityPremiumRag Analysis — EquityPremium Dynamics Evaluation (RAG+LLM Variant)

Analyzes equity premium dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based EquityPremium,
reusing the shared analysis pipeline from EquityPremium/analysis.py.

Usage:
    python examples/EquityPremium/Rag/analysis.py -c configs/EquityPremium/Rag/simulation.yml

See examples/EquityPremium/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.EquityPremium.Rule.analysis import analyze_equity_premium, _load_data


def main():
    """Run equity premium analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze EquityPremiumRag simulation")
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
    print("EquityPremiumRag Analysis - EquityPremium Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_equity_premium(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
