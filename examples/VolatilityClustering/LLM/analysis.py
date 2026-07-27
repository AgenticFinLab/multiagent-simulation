#!/usr/bin/env python
"""Volatility Clustering LLM Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_volatilityclustering_dynamics.png,
02_volatilityclustering_analysis.png, and 03_summary.png.
"""

from examples.standard_rule_analysis import run_standard_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_standard_analysis("VolatilityClustering", "configs/VolatilityClustering/LLM/simulation.yml")


if __name__ == "__main__":
    main()
