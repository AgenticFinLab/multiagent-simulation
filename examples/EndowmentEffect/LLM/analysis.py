"""Analysis entry point and metric exports for the LLM variant."""

from typing import List

import numpy as np

from examples.EndowmentEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    endowment_premium_capture_rate,
    load_simulation_data,
    main,
    mean_absolute_deviation,
    price_deviation,
    validate_endowment_effect,
    volume_suppression_ratio,
)


def deviation_half_life(price_history: List[float], fundamental: float) -> float:
    """Estimate absolute-deviation half-life with a log-linear decay fit."""
    deviations = np.abs(np.asarray(price_deviation(price_history, fundamental)))
    usable = np.flatnonzero(deviations > 0)
    if usable.size < 2:
        raise ValueError("at least two non-zero deviations are required")
    slope, _ = np.polyfit(usable, np.log(deviations[usable]), 1)
    if slope >= 0:
        return float("inf")
    return float(np.log(2.0) / -slope)


def portfolio_wealth_ratio(
    cash_history: List[float],
    position_history: List[float],
    final_price: float,
    initial_wealth: float,
) -> float:
    """Return final marked-to-market wealth divided by initial wealth."""
    if not cash_history or not position_history:
        raise ValueError("cash and position histories must not be empty")
    if initial_wealth <= 0:
        raise ValueError("initial_wealth must be positive")
    return (cash_history[-1] + position_history[-1] * final_price) / initial_wealth


def turnover_rate(
    trades_by_agent: List[float], mean_position: float, total_rounds: int
) -> float:
    """Return per-round units traded relative to the mean position."""
    if mean_position <= 0 or total_rounds <= 0:
        raise ValueError("mean_position and total_rounds must be positive")
    return sum(abs(value) for value in trades_by_agent) / (
        mean_position * total_rounds
    )


if __name__ == "__main__":
    main()


__all__ = [
    "price_deviation",
    "mean_absolute_deviation",
    "deviation_half_life",
    "volume_suppression_ratio",
    "endowment_premium_capture_rate",
    "portfolio_wealth_ratio",
    "turnover_rate",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "validate_endowment_effect",
    "main",
]
