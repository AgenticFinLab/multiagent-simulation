#!/usr/bin/env python
"""South Sea Bubble Rule Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_southseabubble_dynamics.png,
02_southseabubble_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("SouthSeaBubble", "configs/SouthSeaBubble/Rule/simulation.yml")


if __name__ == "__main__":
    main()
