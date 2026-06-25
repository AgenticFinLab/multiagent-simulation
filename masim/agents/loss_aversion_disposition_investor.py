"""LossAversionDispositionInvestor — disposition effect, prospect theory asymmetry.

Theoretical basis: Shefrin & Statman (1985); Kahneman & Tversky (1979) —
Prospect Theory.

Decision rule:
    Track a running cost basis (initialised to first observed price).
    gain_pct = (price - cost_basis) / cost_basis
    If gain_pct >  gain_threshold:                       sell winners (lock in profit).
    If gain_pct < -(gain_threshold / loss_aversion_mult): buy losers (average down).
    Else: hold (the loss-aversion asymmetry holds losers longer than winners).

Parameters (read from ``extras``):
    * ``gain_threshold``: float — gain at which to take profit (default 0.04).
    * ``loss_aversion_mult``: float, ≥ 1 — λ; higher = more reluctance to realise
      losses (default 2.5; Tversky-Kahneman 1992 baseline ≈ 2.25).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleLossAversionDispositionInvestor(CanonicalRulePlayer):
    STRATEGY = "LossAversionDispositionInvestor"
    DISPLAY_NAME = "Loss-Aversion / Disposition Investor"
    SUMMARY = (
        "Sells winners early, holds losers too long; prospect-theory "
        "asymmetry (Shefrin-Statman 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.04)
        )
        self.state.custom_state["loss_aversion_mult"] = float(
            extras.get("loss_aversion_mult", 2.5)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 15.0)
        )
        self.state.custom_state["cost_basis"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") is None:
            self.state.custom_state["cost_basis"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        gain_threshold = self.state.custom_state["gain_threshold"]
        loss_mult = max(self.state.custom_state["loss_aversion_mult"], 1.0)
        base = self.state.custom_state["base_position_size"]
        cost_basis = self.state.custom_state.get("cost_basis") or state.price

        if cost_basis <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}
        gain_pct = (state.price - cost_basis) / cost_basis
        loss_threshold = -(gain_threshold / loss_mult)

        action = "hold"
        quantity = 0.0
        if gain_pct > gain_threshold:
            action = "sell"
            quantity = min(base, abs(gain_pct) * 500.0)
        elif gain_pct < loss_threshold:
            action = "buy"
            quantity = min(base, abs(gain_pct) * 500.0)

        return {"action": action, "quantity": quantity, "bid_price": state.price}

    async def act(self, decision_payload):
        # Update cost basis on buy (weighted average) before delegating.
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        if action == "buy" and quantity > 0:
            old_pos = self.state.custom_state.get("position", 0.0)
            old_cost = self.state.custom_state.get("cost_basis") or 0.0
            new_pos = old_pos + quantity
            price = float(decision_payload.get("bid_price") or 0.0)
            if new_pos > 0 and price > 0:
                self.state.custom_state["cost_basis"] = (
                    old_cost * old_pos + price * quantity
                ) / new_pos
        return await super().act(decision_payload)


class LLMLossAversionDispositionInvestor(CanonicalLLMPlayer):
    STRATEGY = "LossAversionDispositionInvestor"
    DEFAULT_SYS_PROMPT = """\
You are subject to the disposition effect (Shefrin-Statman 1985) and
loss aversion (Tversky-Kahneman 1992). When your unrealised gain
exceeds a moderate threshold, you take profit early. When you sit on
an unrealised loss, you hold much longer than is optimal — you only
capitulate when the loss becomes large. You may also average down on
deep losers.

Output format:
<analysis>state your gain/loss vs entry and which behavior applies</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}.
Your portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Apply disposition: sell winners early, hold losers; consider averaging
down on deep losers.
"""


__all__ = [
    "RuleLossAversionDispositionInvestor",
    "LLMLossAversionDispositionInvestor",
]
