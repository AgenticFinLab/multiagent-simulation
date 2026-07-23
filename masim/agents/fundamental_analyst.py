"""fundamental-analyst — Conservative fundamental analyst.

Canonical implementation of the ``fundamental-analyst`` archetype documented
in ``examples/AGENT_POOL/finance/fundamental-analyst.md``. Gradually learns
the fundamental via exponential smoothing — captures the *conservatism* bias
in belief updating, in contrast to ``rational-updater`` which trusts the
fundamental broadcast immediately.

Theoretical basis:
    Barberis, Shleifer & Vishny (1998) — a model of investor sentiment
    (conservatism and representativeness).
    Shleifer & Vishny (1997) — the limits of arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    belief_{t} = (1 - learning_rate) * belief_{t-1} + learning_rate * F
    dev        = (price - belief_{t}) / belief_{t}

    If ``dev > +threshold``:  sell — price is above the belief.
    If ``dev < -threshold``:  buy  — price is below the belief.
    Otherwise: hold.

    ``belief`` is initialised to the first observed market price (i.e. the
    analyst starts biased toward the observed reality and slowly moves
    toward the true fundamental).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``learning_rate``       : float in (0, 1] — smoothing weight on the
                                 fundamental signal each round (default 0.05).
    * ``threshold``           : float in [0, 1] — no-trade band (default 0.02).
    * ``base_position_size``  : float > 0 — order-size cap (default 25.0).
    * ``sizing_scale``        : float > 0 — deviation→quantity factor
                                 (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalAnalyst(CanonicalRulePlayer):
    STRATEGY = "fundamental-analyst"
    DISPLAY_NAME = "Conservative Fundamental Analyst"
    SUMMARY = (
        "Learns the fundamental via exponential smoothing; captures the "
        "conservatism bias in belief updating (Barberis-Shleifer-Vishny 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["learning_rate"] = float(
            extras.get("learning_rate", 0.05)
        )
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 25.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 1000.0)
        )
        self.state.custom_state["belief"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Seed the belief to the first-observed price so the analyst starts
        # biased toward reality and only slowly moves toward the fundamental.
        if self.state.custom_state.get("belief") is None:
            self.state.custom_state["belief"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        learning_rate = self.state.custom_state["learning_rate"]
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]
        belief = self.state.custom_state.get("belief") or state.price

        # Update belief toward fundamental via exponential smoothing.
        belief = (1.0 - learning_rate) * belief + learning_rate * state.fundamental
        self.state.custom_state["belief"] = belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if belief <= 0:
            return hold
        dev = (state.price - belief) / belief

        if abs(dev) <= threshold:
            return hold

        quantity = min(base, abs(dev) * sizing)
        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMFundamentalAnalyst(CanonicalLLMPlayer):
    STRATEGY = "fundamental-analyst"
    DEFAULT_SYS_PROMPT = """\
You are a conservative fundamental analyst. You update your view of
"fair value" slowly: even when a new fundamental estimate arrives you
only move your belief part of the way toward it. You trade when price
is far from your current belief, not from the just-published number.

Output format:
<analysis>state your current belief of fair value and how price compares.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide against your slowly-updating belief of fair value: buy if price
is well below belief, sell if well above, otherwise hold.
"""


__all__ = ["RuleFundamentalAnalyst", "LLMFundamentalAnalyst"]
