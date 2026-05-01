"""Investor order format validation."""

from typing import List, Set

INVESTOR_ORDER_REQUIRED_FIELDS: List[str] = [
    "action",
    "quantity",
    "investor",
    "strategy",
]

INVESTOR_ORDER_ACTION_VALUES: Set[str] = {"buy", "sell", "hold"}


def validate_order(order: dict) -> None:
    """Validate an investor order dict against the required schema.

    Raises:
        ValueError: If any required field is missing or action has an invalid value.
    """
    missing = [f for f in INVESTOR_ORDER_REQUIRED_FIELDS if f not in order]
    if missing:
        raise ValueError(f"Order missing required fields: {', '.join(missing)}")

    action = order["action"]
    if action not in INVESTOR_ORDER_ACTION_VALUES:
        raise ValueError(
            f"Invalid action '{action}'. Must be one of: {', '.join(sorted(INVESTOR_ORDER_ACTION_VALUES))}"
        )

    quantity = order["quantity"]
    if not isinstance(quantity, (int, float)):
        raise ValueError(f"Quantity must be numeric, got {type(quantity).__name__}")

    bid_price = order.get("bid_price")
    if bid_price is not None:
        if not isinstance(bid_price, (int, float)):
            raise ValueError(
                f"bid_price must be numeric, got {type(bid_price).__name__}"
            )
        if bid_price <= 0:
            raise ValueError(f"bid_price must be positive, got {bid_price}")
