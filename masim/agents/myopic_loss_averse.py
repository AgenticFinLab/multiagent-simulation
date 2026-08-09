"""myopic-loss-averse — Myopic-loss-averse trader (fast evaluation).

Canonical implementation of the ``myopic-loss-averse`` archetype documented
in ``masim/agents/defines/finance/myopic-loss-averse.md``. Evaluates
portfolio performance every few ticks against an anchor price, applies
prospect-theory utility with heightened loss aversion, and sells a large
fraction of its position whenever the utility turns negative. Re-enters
very cautiously only after strong gains.

Theoretical basis:
    Benartzi & Thaler (1995) — myopic loss aversion and the equity premium.
    Tversky & Kahneman (1992) — prospect theory value function.
    Gneezy & Potters (1997) — frequent evaluation reduces risk taking.

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
    * ``evaluation_period`` : int > 0 — ticks between evaluations (default 5).
    * ``loss_aversion``     : float — lambda in prospect theory (default 3.0).
    * ``alpha``             : float in (0,1] — gain curvature (default 0.88).
    * ``beta``              : float in (0,1] — loss curvature (default 0.88).
    * ``sell_fraction``     : float in [0,1] — fraction sold on loss
                              (default 0.70).
    * ``buy_fraction``      : float in [0,1] — fraction of cash used on
                              re-entry (default 0.05).
    * ``gain_threshold``    : float — minimum prospect value for re-entry
                              (default 0.05).
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


class RuleMyopicLossAverse(CanonicalRulePlayer):
    STRATEGY = "myopic-loss-averse"
    DISPLAY_NAME = "Myopic Loss-Averse Trader (Fast Evaluation)"
    SUMMARY = (
        "Evaluates P&L every few ticks under prospect theory with heightened "
        "loss aversion; de-risks aggressively on any loss "
        "(Benartzi & Thaler 1995; Tversky & Kahneman 1992)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["evaluation_period"] = int(
            extras.get("evaluation_period", 5)
        )
        self.state.custom_state["loss_aversion"] = float(
            extras.get("loss_aversion", 3.0)
        )
        self.state.custom_state["alpha"] = float(extras.get("alpha", 0.88))
        self.state.custom_state["beta"] = float(extras.get("beta", 0.88))
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.70)
        )
        self.state.custom_state["buy_fraction"] = float(
            extras.get("buy_fraction", 0.05)
        )
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.05)
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
        # Non-evaluation ticks: hold, do not update anchor.
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

        # Reset anchor for the next evaluation window regardless of decision.
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


class LLMMyopicLossAverse(CanonicalLLMPlayer):
    STRATEGY = "myopic-loss-averse"
    DEFAULT_SYS_PROMPT = """\
You are an anxious myopic loss-averse trader. You check your portfolio
every few ticks against your anchor price. Losses hurt you far more than
equivalent gains delight you, so any red print between checks triggers a
large de-risking sale. You only re-enter after clear, meaningful gains,
and even then only cautiously. You do not trade between evaluation checks.

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
Decide under loss aversion: sell a large fraction on any loss at the
evaluation tick, buy cautiously only after strong gains, otherwise hold.
"""


__all__ = ["RuleMyopicLossAverse", "LLMMyopicLossAverse"]
