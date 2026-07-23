"""risk-averse-saver — Precautionary saver with volatility panic exits.

Canonical implementation of the ``risk-averse-saver`` archetype documented
in ``examples/AGENT_POOL/finance/risk-averse-saver.md``. Panics out of the
market when volatility spikes, restores a cash buffer when the ratio drops,
and only buys when the market is heavily discounted below fair value.

Theoretical basis:
    Carroll (1997) — Buffer-stock saving model.
    Kahneman & Tversky (1979) — Loss aversion (λ ≈ 2.25).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    volatility = stddev of recent log returns (local window)
    cash_ratio = cash / max(1e-6, portfolio_value)

    IF volatility > vol_threshold AND position > 0:
        sell = full position (panic exit).
    ELIF cash_ratio < cash_target_ratio AND position > 0:
        sell = min(position, restore_quantity).
    ELIF price < fair_value * (1 - discount_required)
         AND cash_ratio >= cash_target_ratio:
        buy = min(cash / price, cautious_size).
    ELSE: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``cash_target_ratio``  : float (default 0.80).
    * ``vol_threshold``      : float (default 0.25).
    * ``discount_required``  : float (default 0.30).
    * ``cautious_size``      : float (default 50.0).
    * ``restore_quantity``   : float (default 100.0).
    * ``fair_value``         : float (default 100.0).
    * ``vol_lookback``       : int   (default 10) — local volatility window.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


def _returns_std(prices: List[float]) -> float:
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


class RuleRiskAverseSaver(CanonicalRulePlayer):
    STRATEGY = "risk-averse-saver"
    DISPLAY_NAME = "Precautionary Risk-Averse Saver"
    SUMMARY = (
        "Precautionary saver — panic-exits on volatility, restores a cash "
        "buffer, and only buys at a large fair-value discount (Carroll 1997; "
        "Kahneman & Tversky 1979)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["cash_target_ratio"] = float(
            extras.get("cash_target_ratio", 0.80)
        )
        self.state.custom_state["vol_threshold"] = float(
            extras.get("vol_threshold", 0.25)
        )
        self.state.custom_state["discount_required"] = float(
            extras.get("discount_required", 0.30)
        )
        self.state.custom_state["cautious_size"] = float(
            extras.get("cautious_size", 50.0)
        )
        self.state.custom_state["restore_quantity"] = float(
            extras.get("restore_quantity", 100.0)
        )
        self.state.custom_state["fair_value"] = float(
            extras.get("fair_value", 100.0)
        )
        self.state.custom_state["vol_lookback"] = int(
            extras.get("vol_lookback", 10)
        )
        self.state.custom_state["local_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["local_price_history"]
        history.append(float(market_data["price"]))
        cap = max(self.state.custom_state["vol_lookback"] * 4, 40)
        if len(history) > cap:
            del history[: len(history) - cap]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        history: List[float] = cs["local_price_history"]
        window = history[-cs["vol_lookback"] :]
        volatility = _returns_std(window)

        pv = state.portfolio_value
        cash_ratio = state.cash / max(1e-6, pv) if pv > 0 else 1.0

        # Branch 1: volatility panic — dump full position.
        if volatility > cs["vol_threshold"] and state.position > 0:
            return InvestorOrder.sell(
                quantity=float(state.position),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # Branch 2: rebuild cash buffer.
        if cash_ratio < cs["cash_target_ratio"] and state.position > 0:
            quantity = min(state.position, cs["restore_quantity"])
            if quantity > 0:
                return InvestorOrder.sell(
                    quantity=float(quantity),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )

        # Branch 3: deep-discount cautious buy.
        buy_trigger_price = cs["fair_value"] * (1.0 - cs["discount_required"])
        if state.price < buy_trigger_price and cash_ratio >= cs["cash_target_ratio"]:
            affordable = state.cash / state.price if state.price > 0 else 0.0
            quantity = min(affordable, cs["cautious_size"])
            if quantity > 0:
                return InvestorOrder.buy(
                    quantity=float(quantity),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )

        return hold


class LLMRiskAverseSaver(CanonicalLLMPlayer):
    STRATEGY = "risk-averse-saver"
    DEFAULT_SYS_PROMPT = """\
You are a precautionary saver. You care primarily about protecting your
cash buffer. When volatility spikes you dump your equity holdings; when
your cash-to-portfolio ratio drifts below target you sell to restore it;
and you only buy when the market is deeply discounted relative to your
perceived fair value AND your cash buffer is already healthy.

Output format:
<analysis>state your cash ratio, perceived volatility, and buffer stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Protect the cash buffer first: exit on volatility spikes, sell to restore
the buffer if it thins, buy only at a large discount when the buffer is
already healthy.
"""


__all__ = ["RuleRiskAverseSaver", "LLMRiskAverseSaver"]
