"""leverage-trader — Leveraged convergence trader with margin discipline.

Canonical implementation of the ``leverage-trader`` archetype documented in
``masim/agents/defines/finance/leverage-trader.md``. Uses balance-sheet
leverage to buy into meaningful discounts vs fundamental, but is forced to
delever when equity falls below the margin threshold.

Theoretical basis:
    Geanakoplos (2010) — Leverage cycle and margin-driven position sizing.
    Brunnermeier & Pedersen (2009) — Margin calls and forced liquidation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    equity              = cash + position * price
    leverage_exposure   = |position * price| / leverage_ratio
    margin_threshold    = leverage_exposure * margin_call_threshold

    If ``equity < margin_threshold`` AND ``position > 0``:
        sell ``max(1, int(position * 0.30))``   (forced deleveraging)
    Elif ``deviation < -convergence_threshold``:
        leveraged_cash = cash * leverage_ratio
        qty = min(int(leveraged_cash * |deviation| / price),
                  int(leveraged_cash / price))
        if qty > 0: buy
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``leverage_ratio``          : float > 1 — capital multiplier
                                     (default 25.0, Geanakoplos 2010).
    * ``margin_call_threshold``   : float > 0 — equity/exposure ratio
                                     triggering forced sell (default 0.04,
                                     Adrian & Shin 2010).
    * ``convergence_threshold``   : float > 0 — deviation cut-off for
                                     entering the convergence trade
                                     (default 0.03).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeverageTrader(CanonicalRulePlayer):
    STRATEGY = "leverage-trader"
    DISPLAY_NAME = "Leveraged Convergence Trader"
    SUMMARY = (
        "Leveraged convergence trader: buys discounts, force-sells on "
        "margin (Geanakoplos 2010; Brunnermeier & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["leverage_ratio"] = float(
            extras.get("leverage_ratio", 25.0)
        )
        self.state.custom_state["margin_call_threshold"] = float(
            extras.get("margin_call_threshold", 0.04)
        )
        self.state.custom_state["convergence_threshold"] = float(
            extras.get("convergence_threshold", 0.03)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lev = self.state.custom_state["leverage_ratio"]
        margin = self.state.custom_state["margin_call_threshold"]
        conv = self.state.custom_state["convergence_threshold"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        equity = state.cash + state.position * state.price
        exposure = abs(state.position * state.price) / lev if lev > 0 else 0.0
        threshold_value = exposure * margin

        # 1) Margin-call branch takes priority.
        if state.position > 0 and equity < threshold_value:
            forced_qty = max(1.0, math.floor(state.position * 0.30))
            forced_qty = min(forced_qty, state.position)
            if forced_qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(forced_qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # 2) Convergence buy on material discount.
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        deviation = state.deviation
        if deviation < -conv:
            leveraged_cash = state.cash * lev
            if leveraged_cash <= 0 or state.price <= 0:
                return hold
            raw_qty = math.floor(leveraged_cash * abs(deviation) / state.price)
            cap_qty = math.floor(leveraged_cash / state.price)
            qty = min(raw_qty, cap_qty)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLeverageTrader(CanonicalLLMPlayer):
    STRATEGY = "leverage-trader"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged convergence trader. Under calm conditions you use
substantial balance-sheet leverage to buy assets that trade at a discount
to fundamental. Under stress, however, a margin-call rule forces you to
liquidate part of your position regardless of view. The margin check
takes priority over any convergence signal.

Output format:
<analysis>report equity vs margin threshold, then the convergence signal.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Check equity vs margin threshold first (force-sell if breached); otherwise
leveraged-buy on material discount to fundamental, else hold.
"""


__all__ = ["RuleLeverageTrader", "LLMLeverageTrader"]
