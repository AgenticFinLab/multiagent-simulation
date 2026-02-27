"""MASim Financial Evaluation Module

Centralized analysis functions for financial market simulations.
Organized by financial theory into submodules.

Module Structure (by Financial Theory):
    - timeseries/       : Core time series metrics (returns, volatility, Sharpe, drawdown)
    - behavioral/       : Herding behavior (Bikhchandani cascades, LSV measure, CSAD)
    - volatility/       : Volatility clustering (GARCH signature, regime detection)
    - microstructure/   : Market microstructure (volume, liquidity, price impact)
    - visualization.py  : Professional financial charting functions

Academic References:
    - Jegadeesh & Titman (1993): Momentum returns
    - Bikhchandani et al. (1992): Information cascades
    - Bollerslev (1986): GARCH model
    - Kyle (1985): Market impact model
    - Shiller (1981): Excess volatility

Usage:
    from masim.evaluation.finance import (
        # Core Metrics
        calculate_returns,
        calculate_rolling_volatility,
        calculate_sharpe_ratio,
        calculate_max_drawdown,

        # Herding Analysis
        calculate_bid_convergence_cv,
        calculate_directional_agreement,
        calculate_cascade_measure,

        # Volatility Clustering
        calculate_garch_signature,
        detect_volatility_regimes,

        # Market Impact
        calculate_volume_metrics,
        calculate_agent_impact,

        # Visualization
        plot_price_dynamics,
        plot_returns_analysis,
        plot_multi_panel_summary,
    )
"""

# Time Series Analysis (timeseries.py)
from .timeseries import (
    calculate_autocorrelation,
    calculate_rolling_volatility,
    calculate_price_deviation,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_rolling_autocorrelation,
)

# Behavioral Finance / Herding (behavioral.py)
from .behavioral import (
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
    calculate_cascade_measure,
    calculate_cross_sectional_std,
    calculate_investor_correlation_matrix,
    calculate_rolling_cv,
    detect_herding_episodes,
)

# Volatility / GARCH (volatility.py)
from .volatility import (
    calculate_volatility_persistence,
    calculate_return_clustering,
    detect_volatility_regimes,
    calculate_garch_signature,
)

# Market Microstructure (microstructure.py)
from .microstructure import (
    calculate_volume_metrics,
    calculate_agent_impact,
    calculate_bubble_magnitude,
    calculate_net_demand,
    calculate_strategy_contribution,
    calculate_liquidity_metrics,
)

# Visualization
from .visualization import (
    # Core plots
    plot_price_dynamics,
    plot_returns_analysis,
    plot_volatility_analysis,
    # Herding plots
    plot_herding_metrics,
    plot_bid_convergence,
    # Agent analysis
    plot_agent_activity,
    plot_strategy_contribution,
    # Comprehensive
    plot_multi_panel_summary,
    plot_bubble_crash_analysis,
    # Utilities
    get_style_generator,
    create_figure,
    save_figure,
)

__all__ = [
    # Metrics
    "calculate_autocorrelation",
    "calculate_rolling_volatility",
    "calculate_price_deviation",
    "calculate_returns",
    "calculate_sharpe_ratio",
    "calculate_max_drawdown",
    "calculate_rolling_autocorrelation",
    # Herding
    "calculate_bid_convergence_cv",
    "calculate_directional_agreement",
    "calculate_cascade_measure",
    "calculate_cross_sectional_std",
    "calculate_investor_correlation_matrix",
    "calculate_rolling_cv",
    "detect_herding_episodes",
    # GARCH
    "calculate_volatility_persistence",
    "calculate_return_clustering",
    "detect_volatility_regimes",
    "calculate_garch_signature",
    # Volume/Impact
    "calculate_volume_metrics",
    "calculate_agent_impact",
    "calculate_bubble_magnitude",
    "calculate_net_demand",
    "calculate_strategy_contribution",
    "calculate_liquidity_metrics",
    # Visualization
    "plot_price_dynamics",
    "plot_returns_analysis",
    "plot_volatility_analysis",
    "plot_herding_metrics",
    "plot_bid_convergence",
    "plot_agent_activity",
    "plot_strategy_contribution",
    "plot_multi_panel_summary",
    "plot_bubble_crash_analysis",
    "get_style_generator",
    "create_figure",
    "save_figure",
]
