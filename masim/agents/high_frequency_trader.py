"""high-frequency-trader — HFT momentum amplifier with ultra-short lookback.

Canonical implementation of the ``high-frequency-trader`` archetype
documented in ``masim/agents/defines/finance/high-frequency-trader.md``.
Computes short-window momentum and amplifies it with a speed-advantage
multiplier; clamped to a hard ±60-unit ceiling.

Theoretical basis:
    Kirilenko, Kyle, Samadi & Tuzun (2017) — The Flash Crash: HFT in an
    electronic market.
    De Long, Shleifer, Summers & Waldmann (1990) — Positive feedback
    investment strategies and destabilising rational speculation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Append price to internal ``price_history`` each round.
    If ``len(price_history) >= lookback``:
        recent = price_history[-lookback:]
        short_momentum = (recent[-1] - recent[0]) / recent[0]
    Else:
        short_momentum = state.price_change  (single-tick return fallback)
    signal = short_momentum * momentum_sensitivity
    raw_quantity = signal * base_position_size * speed_advantage
    quantity = clamp(raw_quantity, -max_quantity, +max_quantity)
    Positive → buy; negative → sell; zero → hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``            : int — momentum window (default 2).
    * ``momentum_sensitivity``: float — signal scaling (default 3.0).
    * ``base_position_size``  : float — base sizing (default 40.0).
    * ``speed_advantage``     : float — HFT speed edge (default 1.5).
    * ``max_quantity``        : int — hard clamp (default 60).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHighFrequencyTrader(CanonicalRulePlayer):
    STRATEGY = "high-frequency-trader"
    DISPLAY_NAME = "High-Frequency Momentum Trader"
    SUMMARY = (
        "Amplifies ultra-short-window momentum with a speed-advantage "
        "multiplier (Kirilenko et al. 2017; De Long et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["lookback"] = int(extras.get("lookback", 2))
        cs["momentum_sensitivity"] = float(extras.get("momentum_sensitivity", 3.0))
        cs["base_position_size"] = float(extras.get("base_position_size", 40.0))
        cs["speed_advantage"] = float(extras.get("speed_advantage", 1.5))
        cs["max_quantity"] = int(extras.get("max_quantity", 60))
        cs["hft_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["hft_price_history"]
        try:
            history.append(float(market_data["price"]))
        except (KeyError, TypeError, ValueError):
            return

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        lookback = cs["lookback"]
        sensitivity = cs["momentum_sensitivity"]
        base = cs["base_position_size"]
        speed = cs["speed_advantage"]
        cap = cs["max_quantity"]
        history: List[float] = cs["hft_price_history"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.price) or state.price <= 0:
            return hold

        if len(history) >= lookback and lookback > 0:
            recent = history[-lookback:]
            first = recent[0]
            if first <= 0:
                short_momentum = state.price_change
            else:
                short_momentum = (recent[-1] - first) / first
        else:
            short_momentum = state.price_change

        signal = short_momentum * sensitivity
        raw_quantity = signal * base * speed
        quantity = max(-float(cap), min(raw_quantity, float(cap)))

        if quantity > 0:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if quantity < 0:
            return InvestorOrder.sell(
                quantity=abs(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMHighFrequencyTrader(CanonicalLLMPlayer):
    STRATEGY = "high-frequency-trader"
    DEFAULT_SYS_PROMPT = """\
You are a high-frequency momentum trader with a speed advantage. You
compute the short-window return over the last few rounds and buy or
sell aggressively in that direction, amplified by your speed edge. You
never provide liquidity and never mean-revert — you only ride the
freshest momentum signal.

Output format:
<analysis>state the short momentum and your amplified stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade in the direction of the short-window momentum with speed edge.
"""


__all__ = ["RuleHighFrequencyTrader", "LLMHighFrequencyTrader"]
