"""house-money-trader — Outcome-dependent risk-taker.

Canonical implementation of the ``house-money-trader`` archetype documented
in ``examples/AGENT_POOL/finance/house-money-trader.md``. Position sizing
depends on whether the agent is up or down against its entry price:
"playing with house money" after gains -> doubles size; "snake-bit" after
losses -> halves size. Direction itself is contrarian on the single-tick
return.

Theoretical basis:
    Thaler & Johnson (1990) — house-money / snake-bit effects.
    Barberis & Huang (2001) — narrow framing of gains and losses.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    On first market data: entry_price <- observed price.

    pnl        = (price - entry_price) / entry_price
    risk_factor = gain_risk_multiplier if pnl > 0 else loss_risk_multiplier
    deviation  = (price - prev_price) / prev_price   [state.price_change]

    If |deviation| < deviation_threshold: hold.
    Else:
        quantity = int(base_size * risk_factor)
        deviation > 0 -> sell (contrarian: fade the up-tick)
        deviation < 0 -> buy  (contrarian: fade the down-tick)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gain_risk_multiplier`` : float — sizing multiplier after gains
                                  (default 2.0, Thaler & Johnson 1990).
    * ``loss_risk_multiplier`` : float — sizing multiplier after losses
                                  (default 0.5, Thaler & Johnson 1990).
    * ``base_size``            : float — base quantity before scaling
                                  (default 400).
    * ``deviation_threshold``  : float — |single-tick return| trigger
                                  (default 0.02).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHouseMoneyTrader(CanonicalRulePlayer):
    STRATEGY = "house-money-trader"
    DISPLAY_NAME = "House-Money / Snake-Bit Trader"
    SUMMARY = (
        "Contrarian trader whose position size expands after gains and "
        "shrinks after losses (Thaler & Johnson 1990; Barberis & Huang 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gain_risk_multiplier"] = float(
            extras.get("gain_risk_multiplier", 2.0)
        )
        self.state.custom_state["loss_risk_multiplier"] = float(
            extras.get("loss_risk_multiplier", 0.5)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 400.0))
        self.state.custom_state["deviation_threshold"] = float(
            extras.get("deviation_threshold", 0.02)
        )
        self.state.custom_state["entry_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("entry_price") is None:
            self.state.custom_state["entry_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        gain_mult = self.state.custom_state["gain_risk_multiplier"]
        loss_mult = self.state.custom_state["loss_risk_multiplier"]
        base_size = self.state.custom_state["base_size"]
        threshold = self.state.custom_state["deviation_threshold"]
        entry_price = self.state.custom_state.get("entry_price") or state.price

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if entry_price <= 0:
            return hold

        pnl = (state.price - entry_price) / entry_price
        risk_factor = gain_mult if pnl > 0 else loss_mult

        # single-tick return; state.price_change is already this quantity
        deviation = state.price_change
        if abs(deviation) < threshold:
            return hold

        qty = float(int(base_size * risk_factor))
        if qty <= 0:
            return hold

        # Contrarian: sell on up-tick, buy on down-tick.
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMHouseMoneyTrader(CanonicalLLMPlayer):
    STRATEGY = "house-money-trader"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian trader whose sizing depends on your recent P&L. When
you are up against your entry price you feel like you are playing with
house money and double your usual size; when you are down you feel
snake-bit and halve it. Direction is contrarian: you fade the last
tick — buy the dip, sell the rip — but the size you take is dictated by
your gain/loss framing.

Output format:
<analysis>state your current pnl framing (house money vs snake-bit) and
the direction of the last tick.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Fade the tick with outcome-dependent sizing: buy dips, sell rallies, hold
inside the dead zone.
"""


__all__ = ["RuleHouseMoneyTrader", "LLMHouseMoneyTrader"]
