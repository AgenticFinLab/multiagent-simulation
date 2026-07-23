"""disposition-trader — Disposition-effect retail trader.

Canonical implementation of the ``disposition-trader`` archetype documented
in ``examples/AGENT_POOL/finance/disposition-trader.md``. Sells winners too
early and holds losers too long — the classic Prospect-Theory asymmetry.

Theoretical basis:
    Shefrin & Statman (1985) — the disposition effect.
    Kahneman & Tversky (1979) — Prospect Theory; loss aversion.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gain_pct        = (price - cost_basis) / cost_basis
    loss_threshold  = -(gain_threshold / loss_aversion_mult)

    If ``gain_pct > gain_threshold``: sell — lock in the winner.
    If ``gain_pct < loss_threshold``: buy  — average down on the loser.
    Otherwise: hold.

    Cost basis is initialised from the first observed market price and
    updated on every buy via VWAP.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gain_threshold``      : float > 0 — profit level that triggers
                                 selling (default 0.04).
    * ``loss_aversion_mult``  : float > 0 — factor by which the loss-side
                                 threshold is tighter than the gain-side
                                 threshold (default 2.5, i.e. losers can run
                                 2.5× further than winners before action).
    * ``base_position_size``  : float > 0 — order-size cap (default 15.0).
    * ``sizing_scale``        : float > 0 — gain→quantity factor
                                 (default 500.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDispositionTrader(CanonicalRulePlayer):
    STRATEGY = "disposition-trader"
    DISPLAY_NAME = "Disposition-Effect Retail Trader"
    SUMMARY = (
        "Sells winners too early, holds losers too long "
        "(Shefrin & Statman 1985; Kahneman & Tversky 1979)."
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
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 500.0)
        )
        self.state.custom_state["cost_basis"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") is None:
            self.state.custom_state["cost_basis"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cost_basis = self.state.custom_state.get("cost_basis") or state.price
        gain_threshold = self.state.custom_state["gain_threshold"]
        loss_aversion_mult = self.state.custom_state["loss_aversion_mult"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if cost_basis <= 0:
            return hold
        gain_pct = (state.price - cost_basis) / cost_basis
        loss_threshold = -(gain_threshold / loss_aversion_mult)

        if gain_pct > gain_threshold:
            # Sell — disposition profit-taking.
            quantity = min(base, abs(gain_pct) * sizing)
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if gain_pct < loss_threshold:
            # Buy — average down (loser held / doubled down).
            quantity = min(base, abs(gain_pct) * sizing)
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold

    async def act(self, decision_payload):  # type: ignore[override]
        """Extend the base ``act`` to VWAP-update the cost basis on buys."""
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        bid_price = float(decision_payload.get("bid_price") or 0.0)
        market_data = self.state.custom_state.get("market_data") or {}
        fill_price = (
            bid_price if bid_price > 0 else float(market_data.get("price", 0.0))
        )

        if action == "buy" and quantity > 0:
            old_pos = float(self.state.custom_state["position"])
            old_cost = float(self.state.custom_state.get("cost_basis") or fill_price)
            new_pos = old_pos + quantity
            if new_pos > 0:
                self.state.custom_state["cost_basis"] = (
                    old_cost * old_pos + fill_price * quantity
                ) / new_pos

        # Delegate the normal cash / position bookkeeping.
        return await super().act(decision_payload)


class LLMDispositionTrader(CanonicalLLMPlayer):
    STRATEGY = "disposition-trader"
    DEFAULT_SYS_PROMPT = """\
You are a disposition-effect retail trader. Realising a small gain feels
much better than watching a paper loss deepen, but you also hate crystallising
losses — you sell winners quickly and hold losers hoping they recover.

Output format:
<analysis>report the current gain/loss vs cost basis and your inclination.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade with a disposition bias: lock in modest gains quickly; hold or
average-down on losers rather than cutting.
"""


__all__ = ["RuleDispositionTrader", "LLMDispositionTrader"]
