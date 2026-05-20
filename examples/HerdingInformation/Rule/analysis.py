#!/usr/bin/env python
"""Herding Information Cascade Rule Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_herdinginformation_dynamics.png,
02_herdinginformation_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("HerdingInformation", "configs/HerdingInformation/Rule/simulation.yml")


if __name__ == "__main__":
    main()
