"""MASim Financial Evaluation Module

Centralized analysis functions for financial market simulations.
Organized by financial theory into submodules.

Module Structure (by Financial Theory):
    - timeseries.py     : Core time series metrics (returns, volatility, Sharpe, drawdown)
                          + registry metrics: price_dynamics, information_efficiency,
                          statistical_inference, tail_risk (23 total)
    - behavioral.py     : Behavioral finance / agent-level metrics (herding, cascades,
                          agent PnL/wealth/Sharpe, Gini)
                          + registry metrics: agent_behaviour (8 total)
    - volatility.py     : Volatility clustering (GARCH signature, regime detection)
    - microstructure.py : Market microstructure (order flow, liquidity, price impact)
                          + registry metrics: microstructure (5 total)
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

        # Registry convenience
        register_standard_metrics,
        STANDARD_METRICS,
    )
"""

from typing import List

from masim.evaluation.registry import Metric, MetricsRegistry

# Time Series Analysis (timeseries.py)
from .timeseries import (
    calculate_autocorrelation,
    calculate_rolling_volatility,
    calculate_price_deviation,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_rolling_autocorrelation,
    # Registry metric functions
    m_price_deviation_ts,
    m_mad_pct,
    m_half_life_threshold,
    m_half_life_fitted,
    m_rolling_volatility_ts,
    m_mean_volatility_pct,
    m_max_drawdown_pct,
    m_return_skewness,
    m_return_kurtosis,
    m_return_autocorr_lag1,
    m_return_autocorr_profile,
    m_variance_ratio_lo_mackinlay,
    m_under_revision_ratio,
    m_regime_transition_lag,
    m_price_efficiency_ratio,
    m_forecast_error_persistence,
    m_deviation_decay_slope,
    m_mad_block_bootstrap_ci_95,
    m_half_life_block_bootstrap_ci_95,
    m_ljung_box_returns_pvalue,
    m_adf_unit_root_pvalue,
    m_value_at_risk_95,
    m_conditional_var_95,
    # Internal helpers (re-exported for scenario metrics.py that need them)
    _returns,
    _log_returns,
    # Metric definitions list
    TIMESERIES_METRICS,
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
    # Registry metric functions
    m_agent_action_frequency,
    m_silent_agent_count,
    m_agent_volume_buy_sell,
    m_agent_net_position_ts,
    m_agent_pnl_terminal,
    m_agent_sharpe_terminal,
    m_agent_wealth_terminal,
    m_gini_coefficient,
    # Metric definitions list
    BEHAVIORAL_METRICS,
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
    # Registry metric functions
    m_order_imbalance_ts,
    m_signed_volume_autocorr,
    m_herfindahl_volume_concentration,
    m_strategy_correlation_matrix,
    m_information_share_by_strategy,
    # Metric definitions list
    MICROSTRUCTURE_METRICS,
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

# Validation (scenario-specific reasonableness checks)
from .validation import (
    ValidationResult,
    validate_asset_bubble,
    validate_herd_effect,
    validate_flash_crash,
    validate_market_crash,
    validate_momentum_effect,
    validate_reversal_effect,
    validate_volatility_clustering,
    validate_short_squeeze,
    validate_liquidity_dryup,
    validate_disposition_effect,
    validate_equity_premium,
)

# LLM-based Validation (rigorous financial theory prompts)
from .validation_llm import (
    LLMValidationResult,
    LLMValidator,
    validate_with_llm,
    get_theory_prompt,
    list_supported_scenarios,
)


# ===========================================================================
# Standard Metrics Aggregation
# ===========================================================================


STANDARD_METRICS: List[Metric] = (
    TIMESERIES_METRICS + BEHAVIORAL_METRICS + MICROSTRUCTURE_METRICS
)
"""Complete list of 36 standard registry-compatible Metric definitions,
aggregated from timeseries (23) + behavioral (8) + microstructure (5).
"""


def register_standard_metrics(registry: MetricsRegistry) -> None:
    """Register all 36 standard metrics into the given registry.

    This is the canonical entry point for scenario metrics.py files::

        from masim.evaluation.finance import register_standard_metrics
        from masim.evaluation.registry import MetricsRegistry

        REGISTRY = MetricsRegistry()
        register_standard_metrics(REGISTRY)
        # ... then register scenario-specific metrics ...
    """
    for metric in STANDARD_METRICS:
        registry.register(metric)


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
    # Validation
    "ValidationResult",
    "validate_asset_bubble",
    "validate_herd_effect",
    "validate_flash_crash",
    "validate_market_crash",
    "validate_momentum_effect",
    "validate_reversal_effect",
    "validate_volatility_clustering",
    "validate_short_squeeze",
    "validate_liquidity_dryup",
    "validate_disposition_effect",
    "validate_equity_premium",
    # LLM Validation
    "LLMValidationResult",
    "LLMValidator",
    "validate_with_llm",
    "get_theory_prompt",
    "list_supported_scenarios",
    # Registry metric functions (timeseries)
    "m_price_deviation_ts",
    "m_mad_pct",
    "m_half_life_threshold",
    "m_half_life_fitted",
    "m_rolling_volatility_ts",
    "m_mean_volatility_pct",
    "m_max_drawdown_pct",
    "m_return_skewness",
    "m_return_kurtosis",
    "m_return_autocorr_lag1",
    "m_return_autocorr_profile",
    "m_variance_ratio_lo_mackinlay",
    "m_under_revision_ratio",
    "m_regime_transition_lag",
    "m_price_efficiency_ratio",
    "m_forecast_error_persistence",
    "m_deviation_decay_slope",
    "m_mad_block_bootstrap_ci_95",
    "m_half_life_block_bootstrap_ci_95",
    "m_ljung_box_returns_pvalue",
    "m_adf_unit_root_pvalue",
    "m_value_at_risk_95",
    "m_conditional_var_95",
    # Registry metric functions (behavioral)
    "m_agent_action_frequency",
    "m_silent_agent_count",
    "m_agent_volume_buy_sell",
    "m_agent_net_position_ts",
    "m_agent_pnl_terminal",
    "m_agent_sharpe_terminal",
    "m_agent_wealth_terminal",
    "m_gini_coefficient",
    # Registry metric functions (microstructure)
    "m_order_imbalance_ts",
    "m_signed_volume_autocorr",
    "m_herfindahl_volume_concentration",
    "m_strategy_correlation_matrix",
    "m_information_share_by_strategy",
    # Registry infrastructure
    "STANDARD_METRICS",
    "TIMESERIES_METRICS",
    "BEHAVIORAL_METRICS",
    "MICROSTRUCTURE_METRICS",
    "register_standard_metrics",
    # Helpers re-exported for scenario metrics
    "_returns",
    "_log_returns",
]
