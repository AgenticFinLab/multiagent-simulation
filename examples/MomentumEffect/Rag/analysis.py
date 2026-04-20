"""MomentumEffectRag Analysis — MomentumEffect Dynamics Evaluation (RAG+LLM Variant)

Analyzes momentum effect dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based MomentumEffect,
reusing the shared analysis pipeline from MomentumEffect/analysis.py.

Usage:
    python examples/MomentumEffect/Rag/analysis.py -c configs/MomentumEffect/Rag/simulation.yml

See examples/MomentumEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.MomentumEffect.Rule.analysis import analyze_momentum, _load_data


def main():
    """Run momentum effect analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze MomentumEffectRag simulation")
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
    print("MomentumEffectRag Analysis - MomentumEffect Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_momentum(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
