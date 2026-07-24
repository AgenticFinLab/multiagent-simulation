"""institutional-investor — Weakened-disposition professional trader.

Canonical implementation of the ``institutional-investor`` archetype
documented in ``examples/AGENT_POOL/finance/institutional-investor.md``.
Models a professional portfolio manager exhibiting the disposition effect at
attenuated strength: wider gain threshold (holds winners longer) and tighter
loss threshold (cuts losers faster) than the retail disposition trader.

Theoretical basis:
    Locke & Mann (2005) — Professional trader discipline and trade
    disposition.
    Kahneman & Tversky (1979) — Prospect Theory (with institutional
    discipline moderating loss aversion).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gain_pct = (price - cost_basis) / cost_basis

    If ``gain_pct > gain_threshold``: sell ``sell_fraction * position``.
    If ``gain_pct < -loss_threshold``: sell ``sell_fraction * position``.
    Otherwise: hold.

    Cost basis seeds from the first observed price and updates on buys via
    VWAP (though this archetype only sells).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gain_threshold``  : float > 0 — profit level that triggers delayed
                             profit-taking (default 0.25).
    * ``loss_threshold``  : float > 0 — loss level that triggers the
                             disciplined cut (default 0.15).
    * ``sell_fraction``   : float in (0, 1] — fraction of position sold on
                             trigger (default 0.40).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInstitutionalInvestor(CanonicalRulePlayer):
    STRATEGY = "institutional-investor"
    DISPLAY_NAME = "Institutional Weakened-Disposition Investor"
    SUMMARY = (
        "Professional portfolio manager with attenuated disposition bias — "
        "holds winners longer, cuts losers faster (Locke & Mann 2005)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.25)
        )
        self.state.custom_state["loss_threshold"] = float(
            extras.get("loss_threshold", 0.15)
        )
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.40)
        )
        self.state.custom_state["cost_basis"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") is None:
            self.state.custom_state["cost_basis"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cost_basis = self.state.custom_state.get("cost_basis") or state.price
        gain_threshold = self.state.custom_state["gain_threshold"]
        loss_threshold = self.state.custom_state["loss_threshold"]
        sell_fraction = self.state.custom_state["sell_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if cost_basis <= 0 or state.position <= 0:
            return hold
        gain_pct = (state.price - cost_basis) / cost_basis

        if gain_pct > gain_threshold or gain_pct < -loss_threshold:
            sell_qty = min(sell_fraction * state.position, state.position)
            if sell_qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=sell_qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold

    async def act(self, decision_payload):  # type: ignore[override]
        """Extend base ``act`` to VWAP-update the cost basis on buys."""
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
        return await super().act(decision_payload)


class LLMInstitutionalInvestor(CanonicalLLMPlayer):
    STRATEGY = "institutional-investor"
    DEFAULT_SYS_PROMPT = """\
You are a professional portfolio manager (mutual/hedge/pension fund).
You exhibit a weakened form of the disposition effect: institutional
discipline compresses your bias so you hold winners longer (large gain
threshold) but cut losers faster (tight loss threshold). You do not
consult fundamentals — you trade only on gain/loss vs your cost basis.

Output format:
<analysis>report current gain/loss vs cost basis and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade with professional discipline: sell part of your position only when
gains exceed the wide gain threshold or losses breach the tight loss
threshold; otherwise hold.
"""


__all__ = ["RuleInstitutionalInvestor", "LLMInstitutionalInvestor"]
