"""risk-parity-fund — Volatility-targeting risk-parity fund.

Canonical implementation of the ``risk-parity-fund`` archetype documented in
``examples/AGENT_POOL/finance/risk-parity-fund.md``. Scales its position
inversely with realised volatility (target-vol targeting) and force-cuts on
volatility spikes — creating procyclical selling in stress episodes.

Theoretical basis:
    Moreira & Muir (2017) — Volatility-managed portfolios.
    Barroso & Santa-Clara (2015) — Momentum has its moments.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    returns[i]  = (p[i] - p[i-1]) / p[i-1]
    current_vol = stddev(returns[-vol_lookback:])
    vol_ratio   = target_volatility / current_vol
    target_pos  = base_position * min(vol_ratio, 2.0)

    IF current_vol > 2 * target_volatility:
        target_pos = position * 0.7                # forced 30% deleveraging

    raw_qty = (target_pos - position) * rebalance_speed
    qty     = clip(raw_qty, -50, +30)

    qty > 0 → buy; qty < 0 → sell |qty|; else hold.

Cold-start guard: hold until we have vol_lookback+1 price observations.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_volatility`` : float (default 2.0).
    * ``rebalance_speed``   : float (default 0.3).
    * ``base_position``     : float (default 50.0).
    * ``vol_lookback``      : int   (default 5).
    * ``buy_clip``          : float (default 30.0).
    * ``sell_clip``         : float (default 50.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


def _vol(prices: List[float]) -> float:
    if len(prices) < 2:
        return 0.0
    returns = []
    for i in range(1, len(prices)):
        prev = prices[i - 1]
        if prev <= 0:
            continue
        returns.append((prices[i] - prev) / prev)
    n = len(returns)
    if n < 2:
        return 0.0
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / n
    return math.sqrt(max(var, 0.0))


class RuleRiskParityFund(CanonicalRulePlayer):
    STRATEGY = "risk-parity-fund"
    DISPLAY_NAME = "Volatility-Targeting Risk-Parity Fund"
    SUMMARY = (
        "Volatility-targeting fund — scales inversely with realised vol and "
        "force-deleverages during vol spikes (Moreira & Muir 2017; "
        "Barroso & Santa-Clara 2015)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_volatility"] = float(
            extras.get("target_volatility", 2.0)
        )
        self.state.custom_state["rebalance_speed"] = float(
            extras.get("rebalance_speed", 0.3)
        )
        self.state.custom_state["base_position"] = float(
            extras.get("base_position", 50.0)
        )
        self.state.custom_state["vol_lookback"] = int(
            extras.get("vol_lookback", 5)
        )
        self.state.custom_state["buy_clip"] = float(extras.get("buy_clip", 30.0))
        self.state.custom_state["sell_clip"] = float(
            extras.get("sell_clip", 50.0)
        )
        self.state.custom_state["local_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["local_price_history"]
        history.append(float(market_data["price"]))
        lookback = self.state.custom_state["vol_lookback"]
        cap = max(lookback * 4 + 2, lookback + 2)
        if len(history) > cap:
            del history[: len(history) - cap]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        history: List[float] = cs["local_price_history"]
        lookback = cs["vol_lookback"]
        # Need lookback+1 prices to yield `lookback` returns.
        if len(history) < lookback + 1:
            return hold

        window = history[-(lookback + 1) :]
        current_vol = _vol(window)
        target_vol = cs["target_volatility"]
        if current_vol <= 0.0:
            # Zero volatility — cap the ratio at 2 per profile.
            vol_ratio_capped = 2.0
        else:
            vol_ratio = target_vol / current_vol
            vol_ratio_capped = min(vol_ratio, 2.0)

        target_position = cs["base_position"] * vol_ratio_capped

        # Emergency deleveraging: shrink target to 70% of current.
        if current_vol > 2.0 * target_vol:
            target_position = state.position * 0.7

        position_gap = target_position - state.position
        raw_quantity = position_gap * cs["rebalance_speed"]
        buy_clip = cs["buy_clip"]
        sell_clip = cs["sell_clip"]
        if raw_quantity > buy_clip:
            raw_quantity = buy_clip
        elif raw_quantity < -sell_clip:
            raw_quantity = -sell_clip

        if raw_quantity > 0:
            return InvestorOrder.buy(
                quantity=float(raw_quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if raw_quantity < 0:
            return InvestorOrder.sell(
                quantity=float(-raw_quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRiskParityFund(CanonicalLLMPlayer):
    STRATEGY = "risk-parity-fund"
    DEFAULT_SYS_PROMPT = """\
You are a volatility-targeting risk-parity fund. Your target position is
inversely proportional to realised volatility: you scale up in calm
markets and cut exposure in volatile ones. When realised volatility spikes
to more than twice your target you force a large deleveraging cut — even
though this pushes prices further in the wrong direction.

Output format:
<analysis>state current vs target vol and your target position adjustment.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance partially toward a volatility-scaled target position; force a
sharp cut when realised volatility runs far above target.
"""


__all__ = ["RuleRiskParityFund", "LLMRiskParityFund"]
