"""hot-money-funder — Short-horizon foreign creditor / crisis initiator.

Canonical implementation of the ``hot-money-funder`` archetype documented in
``examples/AGENT_POOL/finance/hot-money-funder.md``. Fast balance-sheet
protection: pulls a large fraction of the position at the first sign of
FX/asset stress, then dips a toe back in when conditions normalise.

Theoretical basis:
    Radelet & Sachs (1998) — hot-money reversal in emerging-market crises.
    Calvo (1998) — sudden stops and phased re-entry of foreign capital.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    deviation = state.deviation  (or state.raw['deviation'])

    If deviation < -theta_reversal: sell phi_sell * position (stress exit).
    Elif deviation >  theta_reversal: buy  phi_buy  * cash / price (re-entry).
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_reversal`` : float — stress threshold |deviation| (default 0.02).
    * ``phi_sell``       : float in [0,1] — fraction of position sold on stress
                            (default 0.60, Radelet & Sachs 1998).
    * ``phi_buy``        : float in [0,1] — fraction of cash re-deployed on
                            recovery (default 0.30, Calvo 1998).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHotMoneyFunder(CanonicalRulePlayer):
    STRATEGY = "hot-money-funder"
    DISPLAY_NAME = "Hot-Money Foreign Creditor"
    SUMMARY = (
        "Short-horizon foreign funder that dumps exposure on stress and "
        "cautiously re-enters on recovery (Radelet & Sachs 1998; Calvo 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_reversal"] = float(
            extras.get("theta_reversal", 0.02)
        )
        self.state.custom_state["phi_sell"] = float(extras.get("phi_sell", 0.60))
        self.state.custom_state["phi_buy"] = float(extras.get("phi_buy", 0.30))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        theta = self.state.custom_state["theta_reversal"]
        phi_sell = self.state.custom_state["phi_sell"]
        phi_buy = self.state.custom_state["phi_buy"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        if deviation < -theta:
            qty = phi_sell * state.position
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation > theta:
            qty = phi_buy * state.cash / state.price
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMHotMoneyFunder(CanonicalLLMPlayer):
    STRATEGY = "hot-money-funder"
    DEFAULT_SYS_PROMPT = """\
You are a short-horizon foreign creditor supplying hot money to an
emerging market. You do not care about long-run fundamentals — only
about protecting your balance sheet on short notice. At the first sign
of currency stress (mildly negative deviation) you dump a large fraction
of your position. When the market has recovered (positive deviation) you
cautiously redeploy a portion of your cash. Otherwise you sit still.

Output format:
<analysis>state the current stress signal and your funding stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Protect capital: sell aggressively into stress, re-enter cautiously on
recovery, hold otherwise.
"""


__all__ = ["RuleHotMoneyFunder", "LLMHotMoneyFunder"]
