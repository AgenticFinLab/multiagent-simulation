"""volatility-trader — Volatility-targeting regime trader.

Canonical implementation of the ``volatility-trader`` archetype
documented in ``examples/AGENT_POOL/finance/volatility-trader.md``.
Mechanically reduces exposure when realized volatility is high relative
to its own moving average, and rebuilds exposure when volatility is low
— a discrete-threshold approximation of the Moreira & Muir (2017)
volatility-managed portfolio rule that feeds the GARCH broadcast back
into order flow.

Theoretical basis:
    Engle (1982) — Autoregressive Conditional Heteroskedasticity.
    Bollerslev (1986) — Generalized ARCH.
    Moreira & Muir (2017) — Volatility-Managed Portfolios.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain a rolling ``vol_history`` of length ``vol_lookback``.

    If ``len(vol_history) < vol_lookback``:
        avg_vol   = current volatility          (graceful degradation)
    Else:
        avg_vol   = mean(vol_history[-lookback:])
    vol_ratio     = volatility / avg_vol        (=1.0 when avg_vol<=0)

    If ``vol_ratio > high_vol_threshold``:
        quantity  = clamp(base * (vol_ratio - 1.0), 0, max_quantity)  → sell
    Elif ``vol_ratio < low_vol_threshold``:
        quantity  = clamp(base * (1.0 - vol_ratio), 0, max_quantity)  → buy
    Else: hold.

    Base cash/position clipping is applied by the canonical order layer.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``vol_lookback``       : int   — MA window length (default 5).
    * ``high_vol_threshold`` : float — sell trigger ratio (default 1.5).
    * ``low_vol_threshold``  : float — buy trigger ratio  (default 0.7).
    * ``base_position_size`` : float — proportional sizing (default 15.0).
    * ``max_quantity``       : float — |quantity| clamp   (default 20.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleVolatilityTrader(CanonicalRulePlayer):
    STRATEGY = "volatility-trader"
    DISPLAY_NAME = "Volatility-Targeting Regime Trader"
    SUMMARY = (
        "Sells in high-vol regimes and buys in low-vol regimes, "
        "creating vol-to-flow feedback (Engle 1982; Bollerslev 1986; "
        "Moreira & Muir 2017)."
    )
    REQUIRES_FEATURES: tuple = ("volatility",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["vol_lookback"] = int(
            extras.get("vol_lookback", 5)
        )
        self.state.custom_state["high_vol_threshold"] = float(
            extras.get("high_vol_threshold", 1.5)
        )
        self.state.custom_state["low_vol_threshold"] = float(
            extras.get("low_vol_threshold", 0.7)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 15.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 20.0)
        )
        self.state.custom_state["vol_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Track a rolling volatility history sized to vol_lookback. The
        # current tick's volatility is appended here and the moving
        # average in decide_order is computed over the last lookback
        # entries (which includes the current tick).
        window = self.state.custom_state["vol_lookback"]
        history = self.state.custom_state["vol_history"]
        vol = market_data.get("volatility")
        if vol is None:
            return
        history.append(float(vol))
        if len(history) > window:
            self.state.custom_state["vol_history"] = history[-window:]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.volatility is None:
            return hold

        window = self.state.custom_state["vol_lookback"]
        history = self.state.custom_state["vol_history"]

        # Graceful degradation: with insufficient history, treat current
        # vol as the baseline → vol_ratio = 1.0 → hold.
        if len(history) < window:
            avg_vol = float(state.volatility)
        else:
            avg_vol = sum(history[-window:]) / window

        if avg_vol <= 0:
            vol_ratio = 1.0
        else:
            vol_ratio = float(state.volatility) / avg_vol

        high = self.state.custom_state["high_vol_threshold"]
        low = self.state.custom_state["low_vol_threshold"]
        base = self.state.custom_state["base_position_size"]
        cap = self.state.custom_state["max_quantity"]

        if vol_ratio > high:
            quantity = min(cap, base * (vol_ratio - 1.0))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if vol_ratio < low:
            quantity = min(cap, base * (1.0 - vol_ratio))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMVolatilityTrader(CanonicalLLMPlayer):
    STRATEGY = "volatility-trader"
    DEFAULT_SYS_PROMPT = """\
You are a volatility-targeting regime trader running a risk-parity
overlay. You do not trade on price direction or fundamentals; you react
only to realized volatility. When current volatility runs hot relative
to its recent moving average you cut exposure (sell); when it runs cool
you rebuild exposure (buy). Between thresholds you stand aside.

Output format:
<analysis>describe the volatility regime relative to its recent average.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade on volatility regime alone: sell when volatility is elevated
versus its recent average, buy when it is depressed, hold when the
regime is neutral.
"""


__all__ = ["RuleVolatilityTrader", "LLMVolatilityTrader"]
