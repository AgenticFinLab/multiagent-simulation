"""Shared, numerically stable price formation for EquityPremium variants."""

from __future__ import annotations

import math
import random
from typing import Any, Iterable, Mapping, Tuple


DEMAND_IMPACT_SCALE = 0.001


def calculate_stock_transition(
    current_price: float,
    orders: Iterable[Mapping[str, Any]],
    expected_return: float,
    volatility: float,
) -> Tuple[float, float]:
    """Return the next price and return using normalized order imbalance.

    Raw order quantities are portfolio-size dependent, so applying their sum
    directly as a percentage return makes the price process scale with agent
    wealth and can overflow.  Normalized imbalance is bounded to [-1, 1] while
    retaining the direction and relative strength of aggregate demand.
    """
    if not math.isfinite(current_price) or current_price <= 0:
        raise ValueError(f"stock price must be finite and positive: {current_price}")
    if not math.isfinite(expected_return) or not math.isfinite(volatility):
        raise ValueError("market return parameters must be finite")
    if volatility < 0:
        raise ValueError("stock_volatility must be non-negative")

    quantities = [float(order["stock_qty"]) for order in orders]
    if any(not math.isfinite(quantity) for quantity in quantities):
        raise ValueError("all stock orders must be finite")

    quantity_scale = max((abs(quantity) for quantity in quantities), default=0.0)
    if quantity_scale < 1.0:
        quantity_scale = 1.0
    scaled_quantities = [quantity / quantity_scale for quantity in quantities]
    net_demand = sum(scaled_quantities)
    gross_demand = sum(abs(quantity) for quantity in scaled_quantities)
    order_imbalance = net_demand / max(gross_demand, 1.0)
    demand_impact = DEMAND_IMPACT_SCALE * order_imbalance

    raw_return = expected_return + random.gauss(0, volatility) + demand_impact
    # A five-sigma guard prevents a malformed/random outlier from corrupting
    # the complete time series while leaving ordinary Gaussian draws intact.
    return_limit = max(0.01, abs(expected_return) + 5.0 * volatility)
    stock_return = max(-return_limit, min(return_limit, raw_return))
    new_price = current_price * (1.0 + stock_return)
    if not math.isfinite(new_price) or new_price <= 0:
        raise FloatingPointError("EquityPremium price transition became invalid")

    return new_price, stock_return
