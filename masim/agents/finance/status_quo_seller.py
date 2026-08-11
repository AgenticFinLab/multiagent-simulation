"""status-quo-seller — Reference-dependent status-quo bias trader.

Canonical implementation of the ``status-quo-seller`` archetype documented
in ``masim/agents/defines/finance/status-quo-seller.md``. Prefers to hold
inventory (status-quo bias) but capitulates once the drawdown from the
observed peak — combined with any external social pressure — exceeds
the pressure threshold.

Theoretical basis:
    Samuelson & Zeckhauser (1988) — status-quo bias in decision making.
    Kahneman, Knetsch & Thaler (1991) — endowment effect and reference
    dependence.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    peak_price       <- running max of price
    drawdown         =  max(0, (peak - price) / peak)
    external         =  state.raw_require("external_pressure", cast=float)
    pressure         =  max(drawdown, external)

    if pressure > pressure_threshold and position > 0:
        sell sell_quantity
    elif position == 0 and price < re_entry_price:
        buy re_entry_quantity
    else:
        hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``pressure_threshold`` : float — pressure trigger (default 0.40).
    * ``sell_quantity``      : float — capitulation size (default 200.0).
    * ``re_entry_price``     : float — bargain price for re-entry
                               (default 60.0).
    * ``re_entry_quantity``  : float — re-entry size (default 50.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleStatusQuoSeller(CanonicalRulePlayer):
    STRATEGY = "status-quo-seller"
    DISPLAY_NAME = "Status-Quo Seller"
    SUMMARY = (
        "Holds by default but capitulates on large drawdowns or external "
        "pressure (Samuelson-Zeckhauser 1988; Kahneman-Knetsch-Thaler "
        "1991)."
    )
    REQUIRES_FEATURES: tuple = ("external_pressure",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["pressure_threshold"] = float(
            extras.get("pressure_threshold", 0.40)
        )
        self.state.custom_state["sell_quantity"] = float(
            extras.get("sell_quantity", 200.0)
        )
        self.state.custom_state["re_entry_price"] = float(
            extras.get("re_entry_price", 60.0)
        )
        self.state.custom_state["re_entry_quantity"] = float(
            extras.get("re_entry_quantity", 50.0)
        )
        self.state.custom_state["peak_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        try:
            price = float(market_data["price"])
        except (KeyError, TypeError, ValueError):
            return
        peak = self.state.custom_state.get("peak_price")
        if peak is None or price > peak:
            self.state.custom_state["peak_price"] = price

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        peak = self.state.custom_state.get("peak_price") or state.price
        if peak <= 0:
            return hold
        drawdown = max(0.0, (peak - state.price) / peak)

        external = state.raw_require("external_pressure", cast=float)

        pressure = max(drawdown, external)

        threshold = self.state.custom_state["pressure_threshold"]
        sell_q = self.state.custom_state["sell_quantity"]
        entry_price = self.state.custom_state["re_entry_price"]
        entry_q = self.state.custom_state["re_entry_quantity"]

        if pressure > threshold and state.position > 0:
            quantity = min(sell_q, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.position == 0 and state.price < entry_price and entry_q > 0:
            return InvestorOrder.buy(
                quantity=entry_q,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMStatusQuoSeller(CanonicalLLMPlayer):
    STRATEGY = "status-quo-seller"
    DEFAULT_SYS_PROMPT = """\
You are a status-quo investor. You prefer to keep your position exactly
where it is. You only capitulate and sell when the drawdown from the
recent peak — combined with any external social pressure — becomes
large enough to override your inertia. You re-enter modestly only when
price reaches an obvious bargain.

Output format:
<analysis>state the drawdown, external pressure, and your inertia call.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Capitulate only when pressure exceeds your threshold; re-enter at a
clear bargain; otherwise hold.
"""


__all__ = ["RuleStatusQuoSeller", "LLMStatusQuoSeller"]
