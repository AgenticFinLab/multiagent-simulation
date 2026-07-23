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
        # FAIL-LOUD: `price` is the minimum viable market signal. If the market
        # coordinator broadcasts a payload without a price, agents cannot make
        # decisions — silently defaulting to 0.0 would allow "free buys"
        # (fill_price=0) and poison every portfolio-based metric.
        if "price" not in market_data or market_data["price"] is None:
            raise ValueError(
                "StandardMarketState.from_market_data: market_data is missing "
                "'price'. Every scenario coordinator MUST broadcast price. "
                "Silent default to 0.0 would falsify portfolio_value and "
                "make fill_price=0 (agents 'buy for free')."
            )
        price = float(market_data["price"])
        prev_price = float(market_data.get("prev_price", price))
        # For fundamental/deviation: if the scenario does NOT model a
        # fundamental value, coordinators should still broadcast an explicit
        # `fundamental` field (NaN or matching price). Silently defaulting
        # to price would lie to the LLM prompt ("Fundamental = Price,
        # Deviation = 0", i.e. perfect fair pricing) and poison every
        # under_revision / bias_magnitude / price_deviation metric.
        _fund_raw = market_data.get("fundamental")
        if _fund_raw is None:
            fundamental = float("nan")
        else:
            fundamental = float(_fund_raw)
        _dev_raw = market_data.get("deviation")
        if _dev_raw is None:
            # Derive from price/fundamental when possible; else NaN.
            if fundamental == fundamental and fundamental != 0.0:  # not NaN
                deviation = (price - fundamental) / fundamental
            else:
                deviation = float("nan")
        else:
            deviation = float(_dev_raw)
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
