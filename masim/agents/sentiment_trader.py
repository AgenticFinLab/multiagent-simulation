"""sentiment-trader — Sentiment-driven noise trader.

Canonical implementation of the ``sentiment-trader`` archetype documented in
``examples/AGENT_POOL/finance/sentiment-trader.md``. Trades in the direction
of an exogenous sentiment signal whenever its magnitude exceeds a neutral
band.

Theoretical basis:
    De Long, Shleifer, Summers & Waldmann (1990) — Noise trader risk.
    Baker & Wurgler (2006) — Investor sentiment and the cross-section of
        stock returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    sentiment = raw["sentiment"]                 (from state.raw)

    IF sentiment > neutral_band:
        q_buy = min(cash / price,
                    sentiment_sensitivity * base_size * sentiment)
    ELIF sentiment < -neutral_band:
        q_sell = min(position,
                    sentiment_sensitivity * base_size * |sentiment|)
    ELSE: hold.

Scenario-specific fields (see ``REQUIRES_FEATURES``):
    * ``sentiment`` : float in [-1, +1] — sentiment index.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``sentiment_sensitivity`` : float (default 2.0, De Long et al. 1990).
    * ``base_size``             : float (default 300.0).
    * ``neutral_band``          : float (default 0.20, Baker & Wurgler 2006).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSentimentTrader(CanonicalRulePlayer):
    STRATEGY = "sentiment-trader"
    DISPLAY_NAME = "Sentiment-Driven Trader"
    SUMMARY = (
        "Trades directionally with an exogenous sentiment signal (De Long "
        "et al. 1990; Baker & Wurgler 2006)."
    )
    REQUIRES_FEATURES: tuple = ("sentiment",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["sentiment_sensitivity"] = float(
            extras.get("sentiment_sensitivity", 2.0)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 300.0)
        )
        self.state.custom_state["neutral_band"] = float(
            extras.get("neutral_band", 0.20)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        sentiment = state.raw_require("sentiment", cast=float)
        if math.isnan(sentiment):
            return hold

        band = cs["neutral_band"]
        if sentiment > band:
            raw_qty = cs["sentiment_sensitivity"] * cs["base_size"] * sentiment
            affordable = state.cash / state.price
            quantity = min(affordable, max(0.0, raw_qty))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if sentiment < -band:
            raw_qty = cs["sentiment_sensitivity"] * cs["base_size"] * abs(sentiment)
            quantity = min(state.position, max(0.0, raw_qty))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMSentimentTrader(CanonicalLLMPlayer):
    STRATEGY = "sentiment-trader"
    DEFAULT_SYS_PROMPT = """\
You are a sentiment-driven trader. You buy on positive sentiment and sell
on negative sentiment, with the trade size proportional to sentiment
magnitude. When sentiment is in the neutral band you stand aside — you do
not trade against the mood.

Output format:
<analysis>state the sentiment level and your directional response.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Follow sentiment: buy when it is meaningfully positive, sell when it is
meaningfully negative, hold in the neutral band.
"""


__all__ = ["RuleSentimentTrader", "LLMSentimentTrader"]
