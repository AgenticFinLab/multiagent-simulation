"""creditor-panicker — Diamond-Dybvig style panicking creditor.

Canonical implementation of the ``creditor-panicker`` archetype documented
in ``examples/AGENT_POOL/finance/creditor-panicker.md``. When the
price-vs-fundamental stress signal breaches a panic threshold, the agent
liquidates a fraction of its position aggressively; once stress subsides
below a recovery threshold, it cautiously rebuilds toward a fraction of
its initial position.

Theoretical basis:
    Diamond & Dybvig (1983) — coordination-failure bank runs.
    Gorton & Metrick (2012); Iyer & Puri (2012) — run intensity data.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    stress_signal = (fundamental - price) / fundamental

    If stress_signal > panic_threshold and position > 0:
        q = min(position, position * liquidation_rate)               → sell
    Elif stress_signal < recovery_threshold and
         position < initial_position * recovery_target:
        q = min(base_size, cash / price)                              → buy
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``panic_threshold``    : float — stress level triggering panic sell
                               (default 0.05).
    * ``liquidation_rate``   : float in (0, 1] — fraction of position sold
                               per panic tick (default 0.80).
    * ``recovery_threshold`` : float — stress level below which re-entry
                               begins (default 0.01).
    * ``recovery_target``    : float — fraction of initial_position below
                               which re-entry is considered (default 0.50).
    * ``base_size``          : float — base re-entry order (default 200.0).
    * ``initial_position``   : float — reference position for recovery
                               logic (default 1000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCreditorPanicker(CanonicalRulePlayer):
    STRATEGY = "creditor-panicker"
    DISPLAY_NAME = "Panicking Creditor"
    SUMMARY = (
        "Aggressively liquidates on stress, cautiously re-enters on calm "
        "(Diamond & Dybvig 1983; Iyer & Puri 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["panic_threshold"] = float(
            extras.get("panic_threshold", 0.05)
        )
        self.state.custom_state["liquidation_rate"] = float(
            extras.get("liquidation_rate", 0.80)
        )
        self.state.custom_state["recovery_threshold"] = float(
            extras.get("recovery_threshold", 0.01)
        )
        self.state.custom_state["recovery_target"] = float(
            extras.get("recovery_target", 0.50)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 200.0))
        # initial_position defaults to the agent's actual starting position
        # if the scenario configured one, otherwise the profile default 1000.
        init_pos = float(
            extras.get(
                "initial_position",
                extras.get("initial_position", 1000.0),
            )
        )
        self.state.custom_state["initial_position_ref"] = init_pos

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental <= 0:
            return hold

        cs = self.state.custom_state
        panic_threshold = cs["panic_threshold"]
        liquidation_rate = cs["liquidation_rate"]
        recovery_threshold = cs["recovery_threshold"]
        recovery_target = cs["recovery_target"]
        base_size = cs["base_size"]
        initial_position_ref = cs["initial_position_ref"]

        stress_signal = (state.fundamental - state.price) / state.fundamental

        if stress_signal > panic_threshold and state.position > 0:
            quantity = min(state.position, state.position * liquidation_rate)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if (
            stress_signal < recovery_threshold
            and state.position < initial_position_ref * recovery_target
            and state.price > 0
        ):
            quantity = min(base_size, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCreditorPanicker(CanonicalLLMPlayer):
    STRATEGY = "creditor-panicker"
    DEFAULT_SYS_PROMPT = """\
You are an uninsured creditor prone to panic. When the price falls
meaningfully below fundamental, you interpret it as a run signal and
dump most of your position quickly — first-mover advantage matters.
Once stress subsides and you are well below your original allocation,
you cautiously rebuild in small steps. You never take large risks
during stress.

Output format:
<analysis>state stress signal vs panic threshold and your posture.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Panic-sell aggressively if stress is high; cautiously rebuild when calm
returns and you are well below your prior allocation.
"""


__all__ = ["RuleCreditorPanicker", "LLMCreditorPanicker"]
