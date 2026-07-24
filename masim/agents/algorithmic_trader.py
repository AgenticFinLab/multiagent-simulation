"""algorithmic-trader — Systematic trend follower over a fixed lookback.

Canonical implementation of the ``algorithmic-trader`` archetype documented
in ``examples/AGENT_POOL/finance/algorithmic-trader.md``.

Theoretical basis:
    Jegadeesh & Titman (1993) — momentum profits in equities; Moskowitz,
    Ooi & Pedersen (2012) — time-series momentum in systematic strategies.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain own price history (>= lookback entries).
    trend = (P[-1] - P[-lookback]) / P[-lookback]
    raw   = trend * trend_sensitivity * base_position_size * trend_multiplier
    qty   = clamp(raw, -max_quantity, +max_quantity)

    Positive qty -> buy; negative -> sell; zero -> hold. Cold start
    (<lookback entries): hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``            : int — trend window length (default 5).
    * ``trend_sensitivity``   : float — sensitivity multiplier (default 1.0).
    * ``base_position_size``  : float — base share unit (default 10.0).
    * ``trend_multiplier``    : float — trend-to-size gain (default 10.0).
    * ``max_quantity``        : float — absolute per-tick cap (default 40.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleAlgorithmicTrader(CanonicalRulePlayer):
    STRATEGY = "algorithmic-trader"
    DISPLAY_NAME = "Systematic Trend Follower"
    SUMMARY = (
        "Systematic time-series momentum trader sizing by the k-tick "
        "trend (Jegadeesh & Titman 1993; Moskowitz et al. 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 5))
        self.state.custom_state["trend_sensitivity"] = float(
            extras.get("trend_sensitivity", 1.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 10.0)
        )
        self.state.custom_state["trend_multiplier"] = float(
            extras.get("trend_multiplier", 10.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 40.0)
        )
        self.state.custom_state["own_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["own_price_history"]
        history.append(float(market_data["price"]))
        cap = max(64, self.state.custom_state["lookback"] * 4)
        if len(history) > cap:
            del history[: len(history) - cap]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        history: List[float] = self.state.custom_state["own_price_history"]
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        lookback = self.state.custom_state["lookback"]
        if len(history) < lookback or lookback < 1:
            return hold

        p_now = history[-1]
        p_ref = history[-lookback]
        if p_ref <= 0:
            return hold

        trend = (p_now - p_ref) / p_ref
        trend_sens = self.state.custom_state["trend_sensitivity"]
        base = self.state.custom_state["base_position_size"]
        multiplier = self.state.custom_state["trend_multiplier"]
        max_qty = self.state.custom_state["max_quantity"]

        raw = trend * trend_sens * base * multiplier
        clipped = max(-max_qty, min(max_qty, raw))
        quantity = int(round(clipped))

        if quantity == 0:
            return hold
        if quantity > 0:
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=float(-quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMAlgorithmicTrader(CanonicalLLMPlayer):
    STRATEGY = "algorithmic-trader"
    DEFAULT_SYS_PROMPT = """\
You are a systematic algorithmic trader executing time-series momentum
over a fixed lookback window. You compute a rolling k-tick return and
size positions proportional to trend magnitude, clipped at a maximum
per-tick quantity. Direction follows trend sign; you do not trade on
fundamentals or narratives.

Output format:
<analysis>report the k-tick trend and target quantity.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Follow the k-tick trend: buy if the recent trend is positive, sell if
negative; scale size by trend magnitude within your cap.
"""


__all__ = ["RuleAlgorithmicTrader", "LLMAlgorithmicTrader"]
