"""MarketCrashRag Analysis — MarketCrash Dynamics Evaluation (RAG+LLM Variant)

Analyzes market crash dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based MarketCrash,
reusing the shared analysis pipeline from MarketCrash/analysis.py.

Usage:
    python examples/MarketCrash/Rag/analysis.py -c configs/MarketCrash/Rag/simulation.yml

See examples/MarketCrash/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.MarketCrash.Rule.analysis import analyze_crash, _load_data


def main():
    """Run market crash analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze MarketCrashRag simulation")
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
    print("MarketCrashRag Analysis - MarketCrash Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
