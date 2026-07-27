#!/usr/bin/env python
"""Tulip Mania RuleLLM Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_tulipmania_dynamics.png,
02_tulipmania_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("TulipMania", "configs/TulipMania/RuleLLM/simulation.yml")


if __name__ == "__main__":
    main()
