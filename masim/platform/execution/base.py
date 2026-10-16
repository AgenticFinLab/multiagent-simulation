"""Execution / settlement contract.

Scope of this module
--------------------
This file defines **only the seam** between an agent that wants to trade and
the world that decides what actually happened. It contains no pricing rule and
no matching algorithm: per the platform's mechanism/policy split, the *channel*
is platform-owned and the *rule* is user-owned.

Why the seam exists
-------------------
Before this contract, the fill was hardcoded inside the agent:

*   ``_apply_fill_and_emit_action`` set ``fill_price = bid_price`` and mutated
    cash/position immediately, so the agent **executed itself** at its own
    quoted price. The market coordinator never read ``bid_price`` (it aggregates
    quantities only), so the booked price and the market price could diverge
    without bound — measured at 1.14% on average and up to 4.5%, and, worse,
    *systematically by strategy type* (momentum always bought above the market
    price, contrarian always sold below it). Every P&L-derived metric inherited
    that bias.
*   ``on_fill`` was therefore not a fill report but a self-confirmation, and no
    scenario could express slippage, partial fills, queueing or depth.

The contract keeps the platform's guarantees and makes the rule pluggable:

======================  =========================================================
Platform owns           ``FillModel`` is the only way an order becomes a fill;
                        exactly one fill per accepted order; the portfolio is
                        mutated only through :meth:`Portfolio.apply_fill`; every
                        fill is recorded with its provenance.
User owns               How ``fill_price`` / ``fill_quantity`` are derived
                        (last price, uniform clearing price, book walk, VWAP,
                        slippage or impact model, partial fills, fees).
======================  =========================================================

:class:`~masim.execution.self_fill.SelfFillModel` is the platform's default and
reproduces the historical behaviour exactly, so existing runs are unchanged
until a scenario opts into a different model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrderIntent:
    """What an agent wants to do, before the world has decided anything.

    This is the *request*. It is not a fill and MUST NOT mutate any state.

    Attributes:
        investor: identity of the submitting agent.
        strategy: archetype identifier (``STRATEGY``) for audit and attribution.
        action: canonical action (``buy`` / ``sell`` / ``hold``).
        quantity: requested size, strictly positive for buy/sell.
        bid_price: the price the agent is willing to trade at. Its meaning is
            model-specific: a limit price for a limit-order model, a reference
            price for a market-order model.
        round_num: logical round the intent was produced in.
        extras: model-specific parameters (order type, time in force, …).
    """

    investor: str
    strategy: str
    action: str
    quantity: float
    bid_price: float
    round_num: int = 0
    extras: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Fill:
    """What actually happened — the execution report.

    One :class:`Fill` corresponds to exactly one accepted :class:`OrderIntent`.
    ``fill_price`` and ``fill_quantity`` are authoritative: the portfolio is
    mutated from these values and ``on_fill`` is driven by this object, never by
    the agent's own intent.

    Attributes:
        investor: identity of the agent whose order this settles.
        action: canonical action that was settled (``buy`` / ``sell`` / ``hold``).
        fill_quantity: settled size, ``>= 0``. Zero means "accepted, nothing
            traded" (e.g. clipped to zero liquidity) and is still a valid report.
        fill_price: price actually paid/received per unit, ``> 0`` for a
            non-zero quantity.
        requested_quantity: the size the agent asked for, kept for slippage and
            fill-ratio accounting.
        bid_price: the price the agent quoted, kept so quote-vs-fill deviation
            is measurable instead of implicit.
        round_num: logical round the fill settled in.
        model: identifier of the :class:`FillModel` that produced the fill.
        rejected: True when the order produced no position change at all
            (insufficient liquidity, risk check, …).
        reject_reason: human-readable reason, required when ``rejected``.
        extras: model-specific report fields (fees, counterparties, …).
    """

    investor: str
    action: str
    fill_quantity: float
    fill_price: float
    requested_quantity: float = 0.0
    bid_price: float = 0.0
    round_num: int = 0
    model: str = ""
    rejected: bool = False
    reject_reason: str = ""
    extras: Mapping[str, Any] = field(default_factory=dict)

    def notional(self) -> float:
        """Signed cash impact of this fill (positive = cash received)."""
        signed = self.fill_quantity if self.action == "sell" else -self.fill_quantity
        return signed * self.fill_price


@dataclass(frozen=True)
class MarketView:
    """Read-only snapshot of the world the fill model may consult.

    Deliberately narrow: a fill model may read the market state it is given and
    must never reach back into the agent's private state, so a model stays
    testable in isolation.

    Attributes:
        round_num: logical round the orders were produced in.
        price: last known market price, if any.
        prev_price: previous market price, if any.
        extras: additional observable world fields (volume, depth, …).
    """

    round_num: int = 0
    price: Optional[float] = None
    prev_price: Optional[float] = None
    extras: Mapping[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Policy contract
# ---------------------------------------------------------------------------


class FillModel(ABC):
    """Turns order intents into execution reports.

    Implementations are stateless with respect to the agent: they receive
    intents and a :class:`MarketView` and return one :class:`Fill` per intent,
    in the same order. A model MAY be stateful with respect to the world (for
    example an order-book model that keeps depth), in which case it is owned by
    the market agent, not by the trading agent.

    Contract:
        * Exactly one fill per intent, same order, same ``investor``.
        * A model MUST NOT mutate agent state; it only reports.
        * A model MUST be deterministic for identical ``(intents, view)``.
        * A model MUST NOT return a non-positive ``fill_price`` for a non-zero
          ``fill_quantity``; the platform re-validates this anyway.
    """

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Stable identifier recorded on every fill this model produces."""
        ...

    @abstractmethod
    def execute(
        self,
        intents: List[OrderIntent],
        view: MarketView,
    ) -> List[Fill]:
        """Settle ``intents`` against the world described by ``view``."""
        ...


class PortfolioView(ABC):
    """Read-only view of an agent's private bookkeeping for the platform.

    Exists so the platform can audit and persist a book without exposing a
    mutation path; mutation happens only through
    :meth:`~masim.player.portfolio.Portfolio.apply_fill`.
    """

    @property
    @abstractmethod
    def cash(self) -> float:
        """Current cash balance."""
        ...

    @property
    @abstractmethod
    def position(self) -> float:
        """Current signed position size."""
        ...

    @abstractmethod
    def equity(self, mark_price: Optional[float] = None) -> float:
        """Mark-to-market value of the book at ``mark_price``."""
        ...
