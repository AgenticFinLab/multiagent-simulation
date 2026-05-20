#!/usr/bin/env python
"""Reversal Effect LLM Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_reversaleffect_dynamics.png,
02_reversaleffect_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("ReversalEffect", "configs/ReversalEffect/LLM/simulation.yml")


if __name__ == "__main__":
    main()
