"""ShortSqueezeRag Analysis — ShortSqueeze Dynamics Evaluation (RAG+LLM Variant)

Analyzes short squeeze dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based ShortSqueeze,
reusing the shared analysis pipeline from ShortSqueeze/analysis.py.

Usage:
    python examples/ShortSqueeze/Rag/analysis.py -c configs/ShortSqueeze/Rag/simulation.yml

See examples/ShortSqueeze/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.ShortSqueeze.Rule.analysis import analyze_short_squeeze, _load_data


def main():
    """Run short squeeze analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze ShortSqueezeRag simulation")
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
    print("ShortSqueezeRag Analysis - ShortSqueeze Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_short_squeeze(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
