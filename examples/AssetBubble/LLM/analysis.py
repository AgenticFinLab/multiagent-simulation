"""AssetBubbleLLM Analysis - Positive Feedback Dynamics Evaluation (LLM Version)

Analyzes asset bubble dynamics in LLM-driven agents.
Uses same methodology as rule-based AssetBubble.

Usage:
    python examples/AssetBubble/LLM/analysis.py -c configs/AssetBubble/LLM/simulation.yml

See examples/AssetBubble/Rule/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution

from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data


def main():
    """Run bubble analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze AssetBubbleLLM simulation")
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
    print("AssetBubbleLLM Analysis - Positive Feedback Dynamics (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_bubble(data, output_dir)

    action_dist = analyze_action_distribution(results)
    summary_path = os.path.join(output_dir, "summary.json")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            persisted = json.load(f)
    except (OSError, ValueError):
        persisted = summary if isinstance(summary, dict) else {}
    persisted["llm_action_distribution"] = action_dist
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(persisted, f, indent=2, default=str)
    if isinstance(summary, dict):
        summary["llm_action_distribution"] = action_dist
    return summary


if __name__ == "__main__":
    main()


__all__ = ["analyze_action_distribution", "main"]
