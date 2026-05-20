#!/usr/bin/env python
"""Market Crash LLM Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_marketcrash_dynamics.png,
02_marketcrash_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("MarketCrash", "configs/MarketCrash/LLM/simulation.yml")


if __name__ == "__main__":
    main()
