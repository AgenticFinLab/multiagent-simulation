"""historical-anchor — Historical-price anchoring trader.

Canonical implementation of the ``historical-anchor`` archetype documented in
``examples/AGENT_POOL/finance/historical-anchor.md``. Distinct from
``anchored-trader`` in that the reference point is a rolling window of past
prices rather than the single first-observed price.

Theoretical basis:
    Northcraft & Neale (1987) — anchoring on prior observations.
    Kahneman, Slovic & Tversky (1982) — availability of the recent past.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    hist_avg      = mean of the last ``lookback`` prices (rolling window,
                    seeded with the current price when the buffer is empty)
    perceived_dev = (price - hist_avg) / hist_avg * (1 - anchor_weight)

    If ``|perceived_dev| > threshold``: trade in the corrective direction
    with ``quantity = min(base_position_size, |perceived_dev| * sizing_scale)``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``anchor_weight``       : float in [0, 1] — dampening factor; higher =
                                 stronger anchoring (default 0.5).
    * ``lookback``            : int > 0 — rolling window length (default 60).
    * ``threshold``           : float in [0, 1] — no-trade band (default 0.03).
    * ``base_position_size``  : float > 0 — order-size cap (default 20.0).
    * ``sizing_scale``        : float > 0 — deviation→quantity factor
                                 (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHistoricalAnchor(CanonicalRulePlayer):
    STRATEGY = "historical-anchor"
    DISPLAY_NAME = "Historical-Price Anchoring Trader"
    SUMMARY = (
        "Anchors to a rolling average of past prices; converges on a "
        "backward-looking reference that lags fundamental regime changes."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["anchor_weight"] = float(
            extras.get("anchor_weight", 0.5)
        )
        self.state.custom_state["lookback"] = int(extras.get("lookback", 60))
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.03))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 1000.0)
        )
        self.state.custom_state["historical_prices"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        prices = self.state.custom_state["historical_prices"]
        prices.append(float(market_data["price"]))
        lookback = self.state.custom_state["lookback"]
        if len(prices) > lookback:
            # keep only the most-recent `lookback` observations
            self.state.custom_state["historical_prices"] = prices[-lookback:]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        prices = self.state.custom_state["historical_prices"]
        anchor_weight = self.state.custom_state["anchor_weight"]
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        hist_avg = sum(prices) / len(prices) if prices else state.price
        if hist_avg <= 0:
            return hold
        perceived_dev = (state.price - hist_avg) / hist_avg * (1.0 - anchor_weight)

        if abs(perceived_dev) <= threshold:
            return hold

        quantity = min(base, abs(perceived_dev) * sizing)
        factory = InvestorOrder.buy if perceived_dev < 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMHistoricalAnchor(CanonicalLLMPlayer):
    STRATEGY = "historical-anchor"
    DEFAULT_SYS_PROMPT = """\
You are a historical-anchor trader. You form your reference price from a
rolling average of recent history, and only slowly re-weight when the
current price drifts away. When the current price is far from your rolling
average, you fade the move; otherwise you hold.

Output format:
<analysis>report your rolling-average reference and how price compares.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide by comparing the current price against your rolling-average anchor:
buy if price is well below the rolling average, sell if well above.
"""


__all__ = ["RuleHistoricalAnchor", "LLMHistoricalAnchor"]
