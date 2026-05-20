"""Analysis utilities for the SunkCostFallacy RuleLLM variant."""

from examples.SunkCostFallacy.Rule.analysis import (
    calculate_metrics,
    compute_agent_attribution,
    compute_escalation_volume,
    compute_losing_holding_rate,
    compute_loss_onset,
    compute_opportunity_reallocation,
    compute_performance_drag,
    compute_rational_cut_volume,
    create_visualizations,
    load_simulation_data,
)

__all__ = [
    "compute_losing_holding_rate",
    "compute_escalation_volume",
    "compute_rational_cut_volume",
    "compute_opportunity_reallocation",
    "compute_performance_drag",
    "compute_loss_onset",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
]
