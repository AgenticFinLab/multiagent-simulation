"""Fill models shipped with the platform.

Policy vs mechanism
-------------------
The platform owns the *channel* (an order becomes a fill only here, exactly once,
and the book is mutated only through the resulting report). How the price and
quantity are derived is a **policy** and lives in these classes, not in the
agent's ``act()``.

Two policies ship with the platform:

*   :class:`SelfFillModel` — the historical behaviour, and the default. The
    agent trades its full requested size at the price it quoted. Kept as the
    default so every existing scenario keeps producing identical results.
*   :class:`MarketPriceFillModel` — an example policy that settles at the
    observable market price, optionally with slippage and a participation cap.
    Useful for microstructure-shaped studies; it is **not** a matching engine.

A domain that needs queueing, an order book or uniform-price clearing implements
:class:`~masim.platform.execution.base.FillModel` itself and is referenced from a
scenario's ``extras.fill_model``.
"""

from __future__ import annotations

from typing import List

from masim.platform.execution.base import Fill, FillModel, MarketView, OrderIntent


class SelfFillModel(FillModel):
    """Trade the full requested size at the agent's own quoted price.

    This reproduces the historical behaviour exactly (``fill_price = bid_price``)
    and is the platform default, so introducing the execution seam does not
    change any existing run.

    Honest limitations, which are why a different model exists:

    * there is no counterparty, depth, queue or partial fill;
    * the market coordinator does not consume ``bid_price`` (it aggregates
      quantities), so the booked price can diverge without bound from the
      market price — measured at 1.14% on average, up to 4.5%, and
      systematically by strategy type;
    * P&L built on these fills therefore measures the agent's own quotes, not
      the market's verdict.
    """

    @property
    def model_id(self) -> str:
        return "self_fill"

    def execute(
        self,
        intents: List[OrderIntent],
        view: MarketView,
    ) -> List[Fill]:
        fills = []
        for intent in intents:
            if intent.action not in ("buy", "sell") or intent.quantity <= 0:
                fills.append(
                    Fill(
                        investor=intent.investor,
                        action=intent.action,
                        fill_quantity=0.0,
                        fill_price=float(intent.bid_price),
                        requested_quantity=float(intent.quantity),
                        bid_price=float(intent.bid_price),
                        round_num=intent.round_num,
                        model=self.model_id,
                    )
                )
                continue
            fills.append(
                Fill(
                    investor=intent.investor,
                    action=intent.action,
                    fill_quantity=float(intent.quantity),
                    fill_price=float(intent.bid_price),
                    requested_quantity=float(intent.quantity),
                    bid_price=float(intent.bid_price),
                    round_num=intent.round_num,
                    model=self.model_id,
                )
            )
        return fills


class MarketPriceFillModel(FillModel):
    """Example policy: settle at the observable market price.

    Both sides trade at ``view.price`` (a call-auction / mark-price
    approximation), adjusted by a symmetric slippage in basis points, and
    optionally capped to a fraction of a notional available size.

    This is intentionally **not** a matching engine: there is no book, no queue
    and no price impact. It exists to show how a domain policy plugs into the
    seam, and to make quote-versus-fill deviation measurable.

    Args:
        slippage_bps: half-spread applied against the taker, in basis points.
        participation_cap: maximum fraction of ``view.extras["available"]`` a
            single order may take; ``None`` disables the cap.
    """

    def __init__(
        self,
        slippage_bps: float = 0.0,
        participation_cap: float | None = None,
    ) -> None:
        self.slippage_bps = float(slippage_bps)
        self.participation_cap = participation_cap

    @property
    def model_id(self) -> str:
        return "market_price"

    def execute(
        self,
        intents: List[OrderIntent],
        view: MarketView,
    ) -> List[Fill]:
        fills = []
        for intent in intents:
            if intent.action not in ("buy", "sell") or intent.quantity <= 0:
                fills.append(
                    Fill(
                        investor=intent.investor,
                        action=intent.action,
                        fill_quantity=0.0,
                        fill_price=float(intent.bid_price),
                        requested_quantity=float(intent.quantity),
                        bid_price=float(intent.bid_price),
                        round_num=intent.round_num,
                        model=self.model_id,
                    )
                )
                continue

            if view.price is None:
                fills.append(
                    Fill(
                        investor=intent.investor,
                        action=intent.action,
                        fill_quantity=0.0,
                        fill_price=0.0,
                        requested_quantity=float(intent.quantity),
                        bid_price=float(intent.bid_price),
                        round_num=intent.round_num,
                        model=self.model_id,
                        rejected=True,
                        reject_reason="no_market_price",
                    )
                )
                continue

            slip = self.slippage_bps / 10_000.0
            price = float(view.price) * (1.0 + slip if intent.action == "buy" else 1.0 - slip)

            quantity = float(intent.quantity)
            if self.participation_cap is not None:
                available = view.extras.get("available")
                if available is not None:
                    quantity = min(quantity, self.participation_cap * float(available))

            rejected = quantity <= 0
            fills.append(
                Fill(
                    investor=intent.investor,
                    action=intent.action,
                    fill_quantity=quantity if not rejected else 0.0,
                    fill_price=price,
                    requested_quantity=float(intent.quantity),
                    bid_price=float(intent.bid_price),
                    round_num=intent.round_num,
                    model=self.model_id,
                    rejected=rejected,
                    reject_reason="no_liquidity" if rejected else "",
                    extras={"quote_deviation": (float(intent.bid_price) - float(view.price))},
                )
            )
        return fills


__all__ = ["SelfFillModel", "MarketPriceFillModel"]
