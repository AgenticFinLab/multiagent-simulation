"""periphery-bond-seller — Peripheral-sovereign bond seller under contagion.

Canonical implementation of the ``periphery-bond-seller`` archetype
documented in ``examples/AGENT_POOL/finance/periphery-bond-seller.md``.
The agent sells peripheral-sovereign bonds when its effective spread
(observed spread plus a contagion loading) crosses a stress threshold,
and re-accumulates opportunistically when stress fades.

Theoretical basis:
    Arghyrou & Kontonikas (2012) — sovereign contagion during the
    eurozone crisis: peripheral yields spike beyond fundamentals when
    core-country risk premia widen.
    Missio & Watzka (2011) — spillovers in sovereign CDS spreads.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    eff_spread = spread + contagion_weight * contagion_signal

    If ``eff_spread > stress_threshold`` AND holdings > 0:
        sell = sell_fraction * position * min((eff-stress)/stress, 1.0).
    If ``eff_spread <= calm_threshold`` AND cash > 0:
        buy = recovery_fraction * cash / price.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``stress_threshold``   : float — bp threshold triggering forced
                                selling (default 200, Arghyrou & Kontonikas
                                2012).
    * ``calm_threshold``     : float — bp level for cautious buy-back
                                (default 80).
    * ``sell_fraction``      : float — fraction of position offloaded
                                per stress event (default 0.10).
    * ``recovery_fraction``  : float — fraction of cash redeployed per
                                calm event (default 0.05).
    * ``contagion_weight``   : float — sensitivity to the contagion signal
                                (default 0.30).

``spread`` and ``contagion_signal`` are read from ``state.raw``; the
scenario coordinator must broadcast them.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePeripheryBondSeller(CanonicalRulePlayer):
    STRATEGY = "periphery-bond-seller"
    DISPLAY_NAME = "Periphery Bond Seller"
    SUMMARY = (
        "Sells peripheral-sovereign bonds when spread widens through "
        "contagion; re-enters opportunistically when calm returns "
        "(Arghyrou & Kontonikas 2012)."
    )
    REQUIRES_FEATURES: tuple = ("spread", "contagion_signal")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["stress_threshold"] = float(
            extras.get("stress_threshold", 200.0)
        )
        self.state.custom_state["calm_threshold"] = float(
            extras.get("calm_threshold", 80.0)
        )
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.10)
        )
        self.state.custom_state["recovery_fraction"] = float(
            extras.get("recovery_fraction", 0.05)
        )
        self.state.custom_state["contagion_weight"] = float(
            extras.get("contagion_weight", 0.30)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        spread = float(state.raw.get("spread", 0.0) or 0.0)
        contagion = float(state.raw.get("contagion_signal", 0.0) or 0.0)
        cw = self.state.custom_state["contagion_weight"]
        eff_spread = spread + cw * contagion

        stress = self.state.custom_state["stress_threshold"]
        calm = self.state.custom_state["calm_threshold"]
        sf = self.state.custom_state["sell_fraction"]
        rf = self.state.custom_state["recovery_fraction"]

        if eff_spread > stress and state.position > 0:
            intensity = min((eff_spread - stress) / max(stress, 1e-9), 1.0)
            quantity = sf * state.position * intensity
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if eff_spread <= calm and state.cash > 0:
            quantity = rf * state.cash / state.price
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPeripheryBondSeller(CanonicalLLMPlayer):
    STRATEGY = "periphery-bond-seller"
    DEFAULT_SYS_PROMPT = """\
You hold peripheral-sovereign bonds during a euro-style contagion episode.
When the effective spread — the observed spread inflated by contagion
from the core countries — pierces your stress threshold, you dump a
fraction of your book to lock in liquidity. When the effective spread
falls back to calm levels, you cautiously redeploy a small slice of cash.
Otherwise you sit still.

Output format:
<analysis>state effective spread, your stress/calm regime, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Manage your peripheral-bond exposure: sell aggressively under contagion
stress, re-buy modestly when the effective spread calms.
"""


__all__ = ["RulePeripheryBondSeller", "LLMPeripheryBondSeller"]
