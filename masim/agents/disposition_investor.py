"""disposition-investor — Prospect-theory disposition investor.

Canonical implementation of the ``disposition-investor`` archetype
documented in ``examples/AGENT_POOL/finance/disposition-investor.md``.
Realises gains too early (sells winners) and averages down on losers
(buys losers) — the disposition effect.

Theoretical basis:
    Shefrin & Statman (1985) — the disposition effect.
    Odean (1998) — PGR/PLR asymmetry in retail brokerage data.
    Kahneman & Tversky (1979); Tversky & Kahneman (1992) — Prospect Theory.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gain_pct = (price - cost_basis) / cost_basis

    If gain_pct >  gain_threshold:
        q = min(sell_fraction_gain * position, position)          → sell
    Elif gain_pct < -loss_threshold:
        q = min(avg_down_fraction * (cash / price), cash / price) → buy
                (VWAP update of cost_basis on fill.)
    Else: hold.

Cost basis is bootstrapped from the first observed market price and
updated via VWAP on buys.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gain_threshold``     : float — gain fraction triggering sale
                               (default 0.03).
    * ``loss_threshold``     : float — loss fraction triggering
                               averaging-down (default 0.10).
    * ``sell_fraction_gain`` : float in (0, 1] — fraction of position
                               sold on gain (default 0.50).
    * ``avg_down_fraction``  : float in (0, 1] — fraction of cash used
                               to average down (default 0.15).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDispositionInvestor(CanonicalRulePlayer):
    STRATEGY = "disposition-investor"
    DISPLAY_NAME = "Disposition-Effect Investor"
    SUMMARY = (
        "Realises small gains, averages down on losers — the disposition "
        "effect (Shefrin & Statman 1985; Odean 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.03)
        )
        self.state.custom_state["loss_threshold"] = float(
            extras.get("loss_threshold", 0.10)
        )
        self.state.custom_state["sell_fraction_gain"] = float(
            extras.get("sell_fraction_gain", 0.50)
        )
        self.state.custom_state["avg_down_fraction"] = float(
            extras.get("avg_down_fraction", 0.15)
        )
        self.state.custom_state["cost_basis"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") is None:
            self.state.custom_state["cost_basis"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cs = self.state.custom_state
        cost_basis = cs.get("cost_basis") or state.price
        gain_threshold = cs["gain_threshold"]
        loss_threshold = cs["loss_threshold"]
        sell_fraction_gain = cs["sell_fraction_gain"]
        avg_down_fraction = cs["avg_down_fraction"]

        if cost_basis <= 0 or state.price <= 0:
            return hold
        gain_pct = (state.price - cost_basis) / cost_basis

        if gain_pct > gain_threshold:
            quantity = min(sell_fraction_gain * state.position, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if gain_pct < -loss_threshold:
            budget = state.cash / state.price
            quantity = min(avg_down_fraction * budget, budget)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold

    async def act(self, decision_payload):  # type: ignore[override]
        """Extend base ``act`` to VWAP-update the cost basis on buys."""
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        bid_price = float(decision_payload.get("bid_price") or 0.0)
        market_data = self.state.custom_state.get("market_data") or {}
        fill_price = (
            bid_price if bid_price > 0 else float(market_data.get("price", 0.0))
        )

        if action == "buy" and quantity > 0:
            old_pos = float(self.state.custom_state["position"])
            old_cost = float(self.state.custom_state.get("cost_basis") or fill_price)
            new_pos = old_pos + quantity
            if new_pos > 0:
                self.state.custom_state["cost_basis"] = (
                    old_cost * old_pos + fill_price * quantity
                ) / new_pos
        return await super().act(decision_payload)


class LLMDispositionInvestor(CanonicalLLMPlayer):
    STRATEGY = "disposition-investor"
    DEFAULT_SYS_PROMPT = """\
You are a disposition-effect investor with a Prospect-Theory reference
point anchored at your average cost. Locking in a small profit feels
disproportionately good, and realising a loss feels disproportionately
painful. So you sell winners early and, rather than cutting losers, you
average down when they slide.

Output format:
<analysis>compare price to cost basis and pick the disposition side.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Sell a fraction of winners quickly; average down on losers rather than
cutting them; otherwise hold.
"""


__all__ = ["RuleDispositionInvestor", "LLMDispositionInvestor"]
