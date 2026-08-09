"""endowed-holder — Endowment-effect long-term holder.

Canonical implementation of the ``endowed-holder`` archetype documented
in ``masim/agents/defines/finance/endowed-holder.md``. The agent refuses
to sell unless the price exceeds a large multiple of its purchase price
(WTA >> WTP); it buys only at a deep discount below purchase price.

Theoretical basis:
    Thaler (1980) — endowment effect.
    Kahneman, Knetsch & Thaler (1990) — experimental WTA/WTP asymmetry.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If price > purchase_price * endowment_multiplier and position > 0:
        q = sell_fraction * position                          → sell
    Elif price < purchase_price * buy_discount and cash > 0:
        q = min(cash / price, buy_size)                       → buy
    Else: hold.

``purchase_price`` is bootstrapped from the first observed market price
and VWAP-updated on subsequent buys.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``endowment_multiplier`` : float — WTA/WTP ratio (default 2.0).
    * ``sell_fraction``        : float in (0, 1] — fraction sold when
                                 endowment threshold met (default 0.25).
    * ``buy_size``             : float — re-entry buy quantity
                                 (default 300.0).
    * ``buy_discount``         : float in (0, 1) — price / cost fraction
                                 required to re-buy (default 0.8).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleEndowedHolder(CanonicalRulePlayer):
    STRATEGY = "endowed-holder"
    DISPLAY_NAME = "Endowment-Effect Holder"
    SUMMARY = (
        "Refuses to sell without a large premium above cost; buys only "
        "at deep discount (Thaler 1980; Kahneman et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["endowment_multiplier"] = float(
            extras.get("endowment_multiplier", 2.0)
        )
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.25)
        )
        self.state.custom_state["buy_size"] = float(extras.get("buy_size", 300.0))
        self.state.custom_state["buy_discount"] = float(
            extras.get("buy_discount", 0.8)
        )
        self.state.custom_state["purchase_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("purchase_price") is None:
            self.state.custom_state["purchase_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cs = self.state.custom_state
        purchase_price = cs.get("purchase_price") or state.price
        endowment_multiplier = cs["endowment_multiplier"]
        sell_fraction = cs["sell_fraction"]
        buy_size = cs["buy_size"]
        buy_discount = cs["buy_discount"]

        if purchase_price <= 0 or state.price <= 0:
            return hold

        endowment_threshold = purchase_price * endowment_multiplier
        buy_threshold = purchase_price * buy_discount

        if state.price > endowment_threshold and state.position > 0:
            quantity = sell_fraction * state.position
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.price < buy_threshold and state.cash > 0:
            quantity = min(state.cash / state.price, buy_size)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold

    def on_fill(
        self, action: str, quantity: float, bid_price: float
    ) -> None:
        """VWAP-update the endowment anchor (``purchase_price``) on buys.

        Runs after :func:`_apply_fill_and_emit_action` has validated
        the wire-format contract and mutated ``position`` / ``cash``.
        ``bid_price`` is guaranteed positive for BUY; the pre-fill
        position is recovered as ``new_pos - quantity``.
        """
        if action != "buy" or quantity <= 0:
            return
        new_pos = float(self.state.custom_state["position"])
        old_pos = new_pos - quantity
        old_cost = float(
            self.state.custom_state.get("purchase_price") or bid_price
        )
        if new_pos > 0:
            self.state.custom_state["purchase_price"] = (
                old_cost * old_pos + bid_price * quantity
            ) / new_pos


class LLMEndowedHolder(CanonicalLLMPlayer):
    STRATEGY = "endowed-holder"
    DEFAULT_SYS_PROMPT = """\
You are an endowment-biased long-term holder. Because of the endowment
effect, you would only give up your position if paid substantially more
than what it is "worth" — you refuse to sell until price exceeds a
large multiple of your cost basis. You are willing to buy more only if
price falls to a deep discount below cost. Otherwise you hold.

Output format:
<analysis>compare current price to cost basis and endowment threshold.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Sell a fraction only if price is above cost times the endowment
multiplier; buy only at deep discount below cost; otherwise hold.
"""


__all__ = ["RuleEndowedHolder", "LLMEndowedHolder"]
