"""prime-broker-first-mover — Fast prime-broker liquidator (creditor run).

Canonical implementation of the ``prime-broker-first-mover`` archetype
documented in ``examples/AGENT_POOL/finance/prime-broker-first-mover.md``.
The first-mover creditor pulls collateral / liquidates positions the
moment a stress threshold is breached, exploiting the first-mover
advantage during a creditor run.

Theoretical basis:
    Gorton & Metrick (2012) — securitized banking and the run on repo.
    Bernardo & Welch (2004) — liquidity crises with strategic runs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``deviation < liquidation_threshold`` (i.e. dev < -0.10) AND
    position > 0:
        sell = min(position, position * liquidation_sell_ratio)
        at market price (no penalty — first-mover captures full price).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``liquidation_threshold``  : float — deviation at which the run is
                                    triggered (default -0.10).
    * ``liquidation_sell_ratio`` : float — fraction of book dumped in one
                                    tick (default 0.40).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePrimeBrokerFirstMover(CanonicalRulePlayer):
    STRATEGY = "prime-broker-first-mover"
    DISPLAY_NAME = "Prime Broker (First Mover)"
    SUMMARY = (
        "Creditor who exits at the first sign of stress and captures full "
        "market price (Gorton & Metrick 2012; Bernardo & Welch 2004)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["liquidation_threshold"] = float(
            extras.get("liquidation_threshold", -0.10)
        )
        self.state.custom_state["liquidation_sell_ratio"] = float(
            extras.get("liquidation_sell_ratio", 0.40)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        threshold = self.state.custom_state["liquidation_threshold"]
        ratio = self.state.custom_state["liquidation_sell_ratio"]

        if state.deviation < threshold and state.position > 0:
            quantity = min(state.position, state.position * ratio)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPrimeBrokerFirstMover(CanonicalLLMPlayer):
    STRATEGY = "prime-broker-first-mover"
    DEFAULT_SYS_PROMPT = """\
You are a first-mover prime broker running a creditor-run playbook. The
moment the market breaches your stress line you liquidate a large slice
of collateral immediately, at the going market price — you never wait for
the herd. Outside that stress trigger you sit still.

Output format:
<analysis>state whether the stress line is breached and your stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Run the first-mover playbook: liquidate hard on stress, hold otherwise.
"""


__all__ = ["RulePrimeBrokerFirstMover", "LLMPrimeBrokerFirstMover"]
