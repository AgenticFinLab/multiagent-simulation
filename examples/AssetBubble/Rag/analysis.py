"""AssetBubbleRag Analysis — Positive Feedback Dynamics Evaluation (RAG+LLM Variant)

Analyzes asset bubble dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based AssetBubble,
reusing the shared analysis pipeline from AssetBubble/analysis.py.

Usage:
    python examples/AssetBubble/Rag/analysis.py -c configs/AssetBubble/Rag/simulation.yml

See examples/AssetBubble/Rule/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AssetBubble.analysis import analyze_bubble, _load_data


def main():
    """Run bubble analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze AssetBubbleRag simulation")
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
    print("AssetBubbleRag Analysis - Positive Feedback Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_bubble(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
