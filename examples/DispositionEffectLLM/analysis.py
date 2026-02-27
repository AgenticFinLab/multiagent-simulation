"""DispositionEffectLLM Analysis - Prospect Theory Evaluation (LLM Version)

Analyzes disposition effect in LLM-driven agents.
Uses same methodology as rule-based DispositionEffect.

Usage:
    python examples/DispositionEffectLLM/analysis.py -c configs/DispositionEffectLLM/simulation.yml

See examples/DispositionEffect/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

from masim.utils import load_config

# Import from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DispositionEffect.analysis import (
    load_simulation_data,
    analyze_by_strategy,
    plot_disposition_analysis,
    generate_summary,
)


def main():
    """Run disposition effect analysis for LLM version."""
    parser = argparse.ArgumentParser(
        description="Analyze DispositionEffectLLM simulation"
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
    print("DispositionEffectLLM Analysis - Prospect Theory (LLM Agents)")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")

    # Analyze by strategy
    print("\n[2] Analyzing PGR/PLR metrics...")
    strategy_results = analyze_by_strategy(data)

    # Generate plots
    print("\n[3] Generating plots...")
    plot_disposition_analysis(data, strategy_results, output_dir)
    print(f"    Saved to {output_dir}/")

    # Generate summary
    print("\n[4] Generating summary...")
    summary = generate_summary(data, strategy_results)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    return summary


if __name__ == "__main__":
    main()
