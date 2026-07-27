"""myopic-loss-averse-investor — Standard myopic loss-averse investor.

Canonical implementation of the ``myopic-loss-averse-investor`` archetype
documented in ``examples/AGENT_POOL/finance/myopic-loss-averse-investor.md``.
Same prospect-theory mechanism as the ``myopic-loss-averse`` archetype but
with a longer evaluation period, milder loss aversion, more moderate
sell/buy fractions, and a lower re-entry threshold — matching the standard
Benartzi–Thaler calibration.

Theoretical basis:
    Benartzi & Thaler (1995) — myopic loss aversion and the equity premium.
    Tversky & Kahneman (1992) — prospect theory value function.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Only act on evaluation ticks (``round % evaluation_period == 0``).

    R = (price - price_at_last_eval) / price_at_last_eval
    V(R) = R ** alpha                 if R >= 0
    V(R) = -loss_aversion * (-R)**beta if R < 0

    If V < 0:
        sell — quantity = position * sell_fraction.
    Elif V > gain_threshold:
        buy  — quantity = cash * buy_fraction / price.
    Otherwise: hold.

    After every evaluation tick, reset ``price_at_last_eval`` to the
    current price.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``evaluation_period`` : int > 0 — ticks between evaluations (default 20).
    * ``loss_aversion``     : float — lambda in prospect theory (default 2.25).
    * ``alpha``             : float in (0,1] — gain curvature (default 0.88).
    * ``beta``              : float in (0,1] — loss curvature (default 0.88).
    * ``sell_fraction``     : float in [0,1] — fraction sold on loss
                              (default 0.50).
    * ``buy_fraction``      : float in [0,1] — fraction of cash used on
                              re-entry (default 0.20).
    * ``gain_threshold``    : float — minimum prospect value for re-entry
                              (default 0.03).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _prospect_value(r: float, alpha: float, beta: float, lam: float) -> float:
    if r >= 0:
        return r ** alpha if r > 0 else 0.0
    return -lam * ((-r) ** beta)


class RuleMyopicLossAverseInvestor(CanonicalRulePlayer):
    STRATEGY = "myopic-loss-averse-investor"
    DISPLAY_NAME = "Myopic Loss-Averse Investor (Standard)"
    SUMMARY = (
        "Standard-calibration MLA investor: evaluates every 20 ticks, "
        "trims on any loss, re-enters after modest gains "
        "(Benartzi & Thaler 1995; Tversky & Kahneman 1992)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["evaluation_period"] = int(
            extras.get("evaluation_period", 20)
        )
        self.state.custom_state["loss_aversion"] = float(
            extras.get("loss_aversion", 2.25)
        )
        self.state.custom_state["alpha"] = float(extras.get("alpha", 0.88))
        self.state.custom_state["beta"] = float(extras.get("beta", 0.88))
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.50)
        )
        self.state.custom_state["buy_fraction"] = float(
            extras.get("buy_fraction", 0.20)
        )
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.03)
        )
        self.state.custom_state["price_at_last_eval"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("price_at_last_eval") is None:
            self.state.custom_state["price_at_last_eval"] = float(
                market_data["price"]
            )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        period = self.state.custom_state["evaluation_period"]
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if period <= 0 or state.round % period != 0:
            return hold

        anchor = self.state.custom_state.get("price_at_last_eval") or state.price
        if anchor <= 0:
            self.state.custom_state["price_at_last_eval"] = state.price
            return hold

        alpha = self.state.custom_state["alpha"]
        beta = self.state.custom_state["beta"]
        lam = self.state.custom_state["loss_aversion"]
        sell_fraction = self.state.custom_state["sell_fraction"]
        buy_fraction = self.state.custom_state["buy_fraction"]
        gain_th = self.state.custom_state["gain_threshold"]

        r = (state.price - anchor) / anchor
        v = _prospect_value(r, alpha, beta, lam)

        # Reset anchor for next evaluation window.
        self.state.custom_state["price_at_last_eval"] = state.price

        if v < 0:
            quantity = max(state.position, 0.0) * sell_fraction
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if v > gain_th and state.price > 0:
            quantity = state.cash * buy_fraction / state.price
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMMyopicLossAverseInvestor(CanonicalLLMPlayer):
    STRATEGY = "myopic-loss-averse-investor"
    DEFAULT_SYS_PROMPT = """\
You are a standard-calibration myopic loss-averse investor. Roughly every
20 ticks you evaluate your portfolio against your anchor price. Losses
hurt you about twice as much as equivalent gains, so any loss at the
evaluation tick prompts you to trim about half your position. You
re-enter with a moderate cash fraction after clear gains. Between
evaluation ticks you hold.

Output format:
<analysis>state whether this is an evaluation tick, the return since your anchor, and your prospect-theory read.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide under standard loss aversion: trim on losses at the evaluation
tick, re-enter after clear gains, otherwise hold.
"""


__all__ = ["RuleMyopicLossAverseInvestor", "LLMMyopicLossAverseInvestor"]
