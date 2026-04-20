"""LiquidityDryupRag Analysis — LiquidityDryup Dynamics Evaluation (RAG+LLM Variant)

Analyzes liquidity dry-up dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based LiquidityDryup,
reusing the shared analysis pipeline from LiquidityDryup/analysis.py.

Usage:
    python examples/LiquidityDryup/Rag/analysis.py -c configs/LiquidityDryup/Rag/simulation.yml

See examples/LiquidityDryup/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.LiquidityDryup.Rule.analysis import analyze_liquidity_dryup, _load_data


def main():
    """Run liquidity dry-up analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze LiquidityDryupRag simulation")
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
    print("LiquidityDryupRag Analysis - LiquidityDryup Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_liquidity_dryup(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
