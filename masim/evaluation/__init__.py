"""MASim Evaluation Module

Provides centralized analysis and evaluation functions for simulations.
Organized by domain (currently: finance), with domain-agnostic infrastructure
at the top level.

Structure:
    masim/evaluation/
    ├── __init__.py           - This file (top-level exports)
    ├── registry.py           - Metric, MetricsRegistry, MetricUnavailable
    ├── data_loader.py        - Standard data extraction from MASim results
    ├── pipeline.py           - High-level analysis orchestration
    └── finance/              - Financial market analysis submodule
        ├── __init__.py       - Finance module exports
        ├── timeseries.py     - Time-series metrics (returns, volatility, Sharpe)
        ├── behavioral.py     - Behavioral finance metrics (herding, cascades)
        ├── volatility.py     - Volatility modeling (GARCH, regime detection)
        ├── microstructure.py - Market microstructure (volume, liquidity, impact)
        ├── visualization.py  - Professional financial charting functions
        ├── validation.py     - Rule-based scenario validation
        └── validation_llm.py - LLM-based validation

Usage:
    # Domain-agnostic infrastructure
    from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable
    from masim.evaluation.data_loader import load_data, batch_to_rounds, series
    from masim.evaluation.pipeline import run_standard_analysis

    # Finance-specific metrics
    from masim.evaluation.finance import (
        calculate_returns,
        calculate_sharpe_ratio,
        calculate_bid_convergence_cv,
        plot_price_dynamics,
    )
"""

from . import finance
from .registry import Metric, MetricUnavailable, MetricsRegistry
from .data_loader import (
    batch_to_rounds,
    load_data,
    market_data_from_payload,
    market_players,
    series,
)

__all__ = [
    # Submodules
    "finance",
    # Registry
    "Metric",
    "MetricsRegistry",
    "MetricUnavailable",
    # Data loader
    "batch_to_rounds",
    "load_data",
    "market_data_from_payload",
    "market_players",
    "series",
]
