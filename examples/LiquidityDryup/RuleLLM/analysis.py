#!/usr/bin/env python
"""Liquidity Dry-up RuleLLM Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_liquiditydryup_dynamics.png,
02_liquiditydryup_analysis.png, and 03_summary.png.
"""

from examples.LiquidityDryup.Rule.analysis import run_liquidity_analysis


def main():
    """Run the standard analysis output contract for this variant."""
    return run_liquidity_analysis("configs/LiquidityDryup/RuleLLM/simulation.yml")


if __name__ == "__main__":
    main()
