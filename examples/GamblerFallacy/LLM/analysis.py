"""Analysis utilities for the GamblerFallacy LLM variant."""

from examples.GamblerFallacy.Rule.analysis import (
    arbitrage_correction_index,
    calculate_metrics,
    create_visualizations,
    gambler_fallacy_index,
    hot_hand_momentum,
    load_simulation_data,
    streak_asymmetry_ratio,
    volatility_amplification_factor,
    wealth_distribution_index,
)
from examples.standard_rule_analysis import run_standard_analysis as _run_standard_analysis


def main():
    """Run GamblerFallacy LLM analysis using the standard output contract."""
    return _run_standard_analysis(
        "GamblerFallacy", "configs/GamblerFallacy/LLM/simulation.yml"
    )

__all__ = [
    "gambler_fallacy_index",
    "streak_asymmetry_ratio",
    "hot_hand_momentum",
    "arbitrage_correction_index",
    "volatility_amplification_factor",
    "wealth_distribution_index",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "main",
]


if __name__ == "__main__":
    main()
