"""minsky-borrower — Minsky financial-instability borrower.

Canonical implementation of the ``minsky-borrower`` archetype documented
in ``examples/AGENT_POOL/finance/minsky-borrower.md``. Escalates leverage
through hedge / speculative / Ponzi stages during a boom, then is forced
to fire-sell when refinancing costs exceed cash-flow (a Minsky-moment).

Theoretical basis:
    Minsky (1986, 1992) — Financial Instability Hypothesis and
    hedge/speculative/Ponzi taxonomy.
    Kindleberger & Aliber (2011) — Manias, Panics, and Crashes.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Read from ``state.raw`` (scenario feature-set):
        asset_return, refinancing_cost, boom_duration, debt, income.

    DSR = (debt * refinancing_cost) / income

    If ``DSR >= ponzi_threshold`` and ``asset_return < refinancing_cost``
    and ``position > 0``:
        forced-sell min(position, (debt*refi - income)/price) — the
        Minsky moment.
    Elif ``boom_duration > 0`` and ``DSR < ponzi_threshold``:
        leverage escalates during the boom:
            leverage_target = base_leverage * (1 + boom_duration * escalation_rate)
            buy min(int(leverage_target), int(cash/price)) - position.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``base_leverage``      : float — starting leverage target (default 3.0).
    * ``escalation_rate``    : float — leverage growth per boom-round
                                (default 0.10).
    * ``hedge_threshold``    : float — DSR < this ⇒ hedge stage (default 0.50).
    * ``ponzi_threshold``    : float — DSR ≥ this ⇒ Ponzi stage (default 1.00).

REQUIRES_FEATURES: reads scenario-specific fields via ``state.raw``.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMinskyBorrower(CanonicalRulePlayer):
    STRATEGY = "minsky-borrower"
    DISPLAY_NAME = "Minsky FIH Leverage Borrower"
    SUMMARY = (
        "Escalates leverage through hedge/speculative/Ponzi stages and "
        "fire-sells at the Minsky moment (Minsky 1986/1992)."
    )
    REQUIRES_FEATURES: tuple = (
        "asset_return",
        "refinancing_cost",
        "boom_duration",
        "debt",
        "income",
    )

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["base_leverage"] = float(
            extras.get("base_leverage", 3.0)
        )
        self.state.custom_state["escalation_rate"] = float(
            extras.get("escalation_rate", 0.10)
        )
        self.state.custom_state["hedge_threshold"] = float(
            extras.get("hedge_threshold", 0.50)
        )
        self.state.custom_state["ponzi_threshold"] = float(
            extras.get("ponzi_threshold", 1.00)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        base_lev = self.state.custom_state["base_leverage"]
        esc = self.state.custom_state["escalation_rate"]
        ponzi_th = self.state.custom_state["ponzi_threshold"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        asset_return = state.raw_require("asset_return", cast=float)
        refi = state.raw_require("refinancing_cost", cast=float)
        boom_duration = state.raw_require("boom_duration", cast=float)
        debt = state.raw_require("debt", cast=float)
        income = state.raw_require("income", cast=float)

        # Debt-service ratio — guard div-by-zero (no income == infinite DSR).
        if income > 0:
            dsr = (debt * refi) / income
        else:
            dsr = math.inf if (debt > 0 and refi > 0) else 0.0

        # Minsky moment: Ponzi stage + asset return below refinancing cost.
        if dsr >= ponzi_th and asset_return < refi and state.position > 0:
            shortfall = debt * refi - income
            if shortfall <= 0:
                shortfall = 0.0
            qty = min(state.position, shortfall / state.price if state.price > 0 else 0.0)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # Boom-phase leverage escalation (below Ponzi cliff).
        if boom_duration > 0 and dsr < ponzi_th:
            leverage_target = base_lev * (1.0 + boom_duration * esc)
            target_units = int(leverage_target)
            gap = target_units - int(state.position)
            affordable = int(state.cash / state.price) if state.price > 0 else 0
            qty = min(gap, max(affordable, 0))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMMinskyBorrower(CanonicalLLMPlayer):
    STRATEGY = "minsky-borrower"
    DEFAULT_SYS_PROMPT = """\
You are a Minsky-taxonomy borrower. During a boom your debt-service ratio
is comfortably below your income (hedge stage) and you steadily escalate
leverage as the boom lengthens (speculative stage). Once refinancing cost
exceeds cash flow you enter the Ponzi stage — at that point any adverse
turn in asset return forces you to fire-sell to meet debt service.

Output format:
<analysis>state your stage (hedge/speculative/Ponzi) and the trigger.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a Minsky borrower: escalate leverage during the boom, but
fire-sell at the Minsky moment when refi cost exceeds cash flow.
"""


__all__ = ["RuleMinskyBorrower", "LLMMinskyBorrower"]
