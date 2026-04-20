"""FlashCrashLLM Analysis - HFT Dynamics Evaluation (LLM Version)

Analyzes flash crash dynamics in LLM-driven agents.
Uses same methodology as rule-based FlashCrash.

Usage:
    python examples/FlashCrash/LLM/analysis.py -c configs/FlashCrash/LLM/simulation.yml

See examples/FlashCrash/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.FlashCrash.Rule.analysis import analyze_flash_crash, _load_data


def main():
    """Run flash crash analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrashLLM simulation")
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
    print("FlashCrashLLM Analysis - HFT Dynamics (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_flash_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
