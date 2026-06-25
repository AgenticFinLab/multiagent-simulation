"""Standard market-state contract shared by every canonical agent.

Every scenario whose ``market_features`` list is empty is required to broadcast
``market_data`` payloads with at least the fields enumerated below. Canonical
agents read *only* these fields, which is what makes them portable between
scenarios.

Niche scenarios (e.g. FlashCrash with ``microstructure_book``) attach extra
fields to the same payload; canonical agents ignore them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StandardMarketState:
    """Per-round snapshot consumed by canonical agents.

    Required fields are populated from the market broadcast and the agent's
    own portfolio state. Optional fields default to ``None`` / empty when the
    scenario does not provide them; agents that depend on them must declare
    that dependency on their canonical Rule class via the
    ``REQUIRES_FEATURES`` class attribute (consumed by
    :mod:`masim.interface.customized.agent_catalog`).
    """

    # --- core market signal (every scenario broadcasts these) ---------------
    round: int
    price: float
    prev_price: float
    fundamental: float
    deviation: float
    price_change: float

    # --- agent portfolio (read from custom_state) ---------------------------
    cash: float
    position: float

    # --- derived convenience field ------------------------------------------
    portfolio_value: float

    # --- optional, scenario-dependent ---------------------------------------
    volatility: Optional[float] = None
    recent_returns: List[float] = field(default_factory=list)

    # --- escape hatch for scenarios that attach extra payload keys ----------
    raw: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    @classmethod
    def from_market_data(
        cls,
        market_data: Dict[str, Any],
        *,
        cash: float,
        position: float,
        recent_returns: Optional[List[float]] = None,
        volatility: Optional[float] = None,
    ) -> "StandardMarketState":
        """Build a :class:`StandardMarketState` from a broadcast payload."""
        price = float(market_data.get("price", 0.0))
        prev_price = float(market_data.get("prev_price", price))
        fundamental = float(market_data.get("fundamental", price))
        deviation = float(market_data.get("deviation", 0.0))
        if prev_price > 0:
            price_change = (price - prev_price) / prev_price
        else:
            price_change = 0.0
        return cls(
            round=int(market_data.get("round", 0)),
            price=price,
            prev_price=prev_price,
            fundamental=fundamental,
            deviation=deviation,
            price_change=price_change,
            cash=float(cash),
            position=float(position),
            portfolio_value=float(cash) + float(position) * price,
            volatility=volatility,
            recent_returns=list(recent_returns or []),
            raw=dict(market_data),
        )

    # ------------------------------------------------------------------
    def template_vars(self) -> Dict[str, Any]:
        """Return the kwargs that fill an LLM ``user_message`` template."""
        return {
            "round": self.round,
            "price": self.price,
            "prev_price": self.prev_price,
            "fundamental": self.fundamental,
            "deviation": self.deviation,
            "price_change": self.price_change,
            "cash": self.cash,
            "position": self.position,
            "portfolio_value": self.portfolio_value,
        }
