#!/usr/bin/env python
"""2010 Flash Crash LLM Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json and variant-specific metrics.

Usage:
    python examples/FlashCrash2010/LLM/analysis.py -c configs/FlashCrash2010/LLM/simulation.yml
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from examples.FlashCrash2010.Rule.analysis import analyze_flash_crash


def main():
    """Run the standard analysis output contract for this variant."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrash2010 LLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/LLM/simulation.yml",
    )
    args = parser.parse_args()
    result = analyze_flash_crash(args.config)
    print(json.dumps(result, indent=2))
    return result


__all__ = ["main"]


if __name__ == "__main__":
    main()
