#!/usr/bin/env python
"""2010 Flash Crash RuleLLM Simulation Analysis.

The RuleLLM variant embeds Rule-derived decision rules inside the LLM
prompts. From an analysis standpoint it produces the same records shape as
the Rule variant (identical Market coordinator, identical order payload
schema), so it re-uses the Rule analysis pipeline verbatim.

Usage
-----
    python examples/FlashCrash2010/RuleLLM/analysis.py \
        -c configs/FlashCrash2010/RuleLLM/simulation.yml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from examples.FlashCrash2010.Rule.analysis import (
    analyze_flash_crash,
)


def main() -> Dict[str, Any]:
    """CLI entry point delegating to the Rule pipeline with a RuleLLM config."""
    parser = argparse.ArgumentParser(
        description="Analyze FlashCrash2010 RuleLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()
    summary = analyze_flash_crash(args.config)
    summary["variant"] = "RuleLLM"
    return summary


__all__ = ["main"]


if __name__ == "__main__":
    main()
