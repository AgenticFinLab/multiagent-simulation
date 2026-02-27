"""FlashCrashLLM Analysis - HFT Dynamics Evaluation (LLM Version)

Analyzes flash crash dynamics in LLM-driven agents.
Uses same methodology as rule-based FlashCrash.

Usage:
    python examples/FlashCrashLLM/analysis.py -c configs/FlashCrashLLM/simulation.yml

See examples/FlashCrash/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_simulation_data

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from FlashCrash.analysis import analyze_flash_crash


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

    data = load_simulation_data(config)
    summary = analyze_flash_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
