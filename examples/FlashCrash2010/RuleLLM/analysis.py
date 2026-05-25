#!/usr/bin/env python
"""2010 Flash Crash RuleLLM Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_flashcrash2010_dynamics.png,
02_flashcrash2010_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("FlashCrash2010", "configs/FlashCrash2010/RuleLLM/simulation.yml")


if __name__ == "__main__":
    main()
