"""
MASim Evaluation Module

Provides centralized analysis and evaluation functions for financial simulations.
Organized by financial theory, directly importable for all scenario analysis.

Structure:
    masim/evaluation/
    ├── __init__.py           - This file
    └── finance/              - Financial analysis submodule
        ├── __init__.py       - Finance module exports
        ├── metrics.py        - Core metrics (returns, volatility, Sharpe, drawdown)
        ├── herding.py        - Herding behavior (CV, directional agreement, cascade)
        ├── garch.py          - Volatility clustering (GARCH signature, regime detection)
        ├── volume.py         - Market microstructure (volume, liquidity, price impact)
        └── visualization.py  - Professional financial charting functions

Usage:
    from masim.evaluation.finance import (
        # Metrics
        calculate_returns,
        calculate_sharpe_ratio,

        # Herding
        calculate_bid_convergence_cv,

        # Visualization
        plot_price_dynamics,
        plot_multi_panel_summary,
    )
"""

from . import finance

__all__ = ["finance"]
