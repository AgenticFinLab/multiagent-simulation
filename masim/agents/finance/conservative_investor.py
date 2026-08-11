"""conservative-investor — CRRA risk-averse utility maximiser.

Canonical implementation of the ``conservative-investor`` archetype
documented in ``masim/agents/defines/finance/conservative-investor.md``.
Buys when the certainty equivalent (expected return net of variance
penalty) exceeds a hurdle and the market trades below fundamental;
takes profit when the market trades meaningfully above fundamental.

Theoretical basis:
    Pratt (1964) / Arrow (1965) — CRRA / risk aversion.
    Bliss & Panigirtzoglou (2004) — option-implied risk aversion.
    Mehra & Prescott (1985) — equity risk premium.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    ER  = (fundamental - price) / price
    var = var(price_history) / mean(price_history)^2
    CE  = ER - 0.5 * gamma * var

    IF CE > hurdle_rate AND price < fundamental:
        q = min(max_allocation * cash / price,
                base_size * CE * sizing_scale / price)
        BUY q
    ELIF price > fundamental * (1 + sell_premium):
        excess = (price - fundamental * (1 + sell_premium)) / price
        q = min(position, base_size * excess * sizing_scale)
        SELL q
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gamma``          : float > 0 — CRRA coefficient (default 4.0).
    * ``hurdle_rate``    : float > 0 — minimum CE to trigger buy
                            (default 0.02).
    * ``max_allocation`` : float in [0, 1] — cash-fraction cap per trade
                            (default 0.10).
    * ``sell_premium``   : float > 0 — overvaluation trigger for sell
                            (default 0.05).
    * ``base_size``      : float > 0 — base order-size multiplier
                            (default 300.0).
    * ``sizing_scale``   : float > 0 — CE/excess sizing scale
                            (default 5000.0).
    * ``history_window`` : int > 0 — rolling window length (default 5).
"""

from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _variance(seq: List[float]) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    m = sum(seq) / n
    return sum((x - m) ** 2 for x in seq) / (n - 1)


class RuleConservativeInvestor(CanonicalRulePlayer):
    STRATEGY = "conservative-investor"
    DISPLAY_NAME = "CRRA Conservative Investor"
    SUMMARY = (
        "Risk-averse CRRA utility maximiser — buys when certainty "
        "equivalent clears the hurdle, sells at generous premiums "
        "(Pratt 1964; Bliss & Panigirtzoglou 2004)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gamma"] = float(extras.get("gamma", 4.0))
        self.state.custom_state["hurdle_rate"] = float(
            extras.get("hurdle_rate", 0.02)
        )
        self.state.custom_state["max_allocation"] = float(
            extras.get("max_allocation", 0.10)
        )
        self.state.custom_state["sell_premium"] = float(
            extras.get("sell_premium", 0.05)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 300.0))
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["history_window"] = int(
            extras.get("history_window", 5)
        )
        self.state.custom_state["price_window"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        window = int(self.state.custom_state["history_window"])
        buf: List[float] = self.state.custom_state["price_window"]
        buf.append(float(market_data["price"]))
        if len(buf) > window:
            del buf[: len(buf) - window]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        gamma = self.state.custom_state["gamma"]
        hurdle = self.state.custom_state["hurdle_rate"]
        max_alloc = self.state.custom_state["max_allocation"]
        sell_premium = self.state.custom_state["sell_premium"]
        base = self.state.custom_state["base_size"]
        sizing = self.state.custom_state["sizing_scale"]

        window: List[float] = self.state.custom_state["price_window"]
        if len(window) >= 2:
            m = mean(window)
            var = _variance(window) / (m * m) if m > 0 else 0.0
        else:
            var = 0.0

        expected_return = (state.fundamental - state.price) / state.price
        ce = expected_return - 0.5 * gamma * var

        if ce > hurdle and state.price < state.fundamental:
            q_alloc = max_alloc * state.cash / state.price
            q_signal = base * ce * sizing / state.price
            qty = min(max(q_alloc, 0.0), max(q_signal, 0.0))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.price > state.fundamental * (1.0 + sell_premium):
            excess = (state.price - state.fundamental * (1.0 + sell_premium)) / state.price
            q_signal = base * excess * sizing
            qty = min(max(state.position, 0.0), max(q_signal, 0.0))
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMConservativeInvestor(CanonicalLLMPlayer):
    STRATEGY = "conservative-investor"
    DEFAULT_SYS_PROMPT = """\
You are a conservative CRRA-style investor. You buy only when the
expected return, penalised for recent price variance, clears a firm
hurdle AND the market is below fundamental. You take profit only when
the market trades comfortably above fundamental by the sell-premium
margin. Your allocations are capped as a fraction of cash.

Output format:
<analysis>state expected return, variance penalty, and whether you buy, sell, or hold.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy only when the certainty-equivalent return clears the hurdle and the
market is below fundamental; sell only when price exceeds fundamental
by the sell premium; hold otherwise.
"""


__all__ = ["RuleConservativeInvestor", "LLMConservativeInvestor"]
