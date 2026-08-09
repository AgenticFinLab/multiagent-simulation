"""flash-market-maker — High-frequency market maker with flash-crash withdrawal.

Canonical implementation of the ``flash-market-maker`` archetype documented in
``masim/agents/defines/finance/flash-market-maker.md``. Provides two-sided
liquidity in calm markets and withdraws when realized volatility exceeds a
threshold, amplifying flash-crash dynamics.

Theoretical basis:
    Menkveld (2013) — High-frequency trading and the new market makers.
    Kirilenko, Kyle, Samadi & Tuzun (2017) — The flash crash: HFT in an
    electronic market.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``volatility >= vol_threshold``: hold (withdraw all quotes).
    Elif ``order_flow_imbalance > imbalance_threshold``: buy
        ``min(cash / price, quote_size, max_inventory - position)``.
    Elif ``order_flow_imbalance < -imbalance_threshold``: sell
        ``min(position, quote_size)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``vol_threshold``       : float — withdrawal trigger (default 0.04).
    * ``imbalance_threshold`` : float — OFI trigger (default 0.1).
    * ``quote_size``          : float — base quote depth (default 1000.0).
    * ``max_inventory``       : float — long/short cap (default 5000.0).

Scenario-specific inputs read via ``state.raw`` (declared through
``REQUIRES_FEATURES``): ``volatility``, ``order_flow_imbalance``.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFlashMarketMaker(CanonicalRulePlayer):
    STRATEGY = "flash-market-maker"
    DISPLAY_NAME = "Flash Market Maker"
    SUMMARY = (
        "Provides two-sided liquidity in calm markets and withdraws under "
        "high volatility (Menkveld 2013; Kirilenko et al. 2017)."
    )
    REQUIRES_FEATURES: tuple = ("volatility", "order_flow_imbalance")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["vol_threshold"] = float(extras.get("vol_threshold", 0.04))
        self.state.custom_state["imbalance_threshold"] = float(
            extras.get("imbalance_threshold", 0.1)
        )
        self.state.custom_state["quote_size"] = float(extras.get("quote_size", 1000.0))
        self.state.custom_state["max_inventory"] = float(
            extras.get("max_inventory", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        vol_threshold = cs["vol_threshold"]
        imb_threshold = cs["imbalance_threshold"]
        quote_size = cs["quote_size"]
        max_inv = cs["max_inventory"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        volatility = state.volatility
        if volatility is None:
            volatility = state.raw_require("volatility", cast=float)
        ofi = state.raw_require("order_flow_imbalance", cast=float)

        if math.isnan(volatility) or math.isnan(ofi):
            return hold

        if volatility >= vol_threshold:
            return hold

        if state.price <= 0:
            return hold

        if ofi > imb_threshold:
            capacity = max(0.0, max_inv - state.position)
            quantity = min(state.cash / state.price, quote_size, capacity)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if ofi < -imb_threshold:
            quantity = min(max(state.position, 0.0), quote_size)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        return hold


class LLMFlashMarketMaker(CanonicalLLMPlayer):
    STRATEGY = "flash-market-maker"
    DEFAULT_SYS_PROMPT = """\
You are a high-frequency market maker. When volatility is calm you post
two-sided quotes and lean into whichever side of the order flow is
dominant. When volatility spikes you withdraw all quotes immediately to
protect capital.

Output format:
<analysis>state the volatility regime and order-flow direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Quote both sides when volatility is calm; withdraw when volatility is
stressed.
"""


__all__ = ["RuleFlashMarketMaker", "LLMFlashMarketMaker"]
