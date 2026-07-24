"""passive-follower — Herding-driven consensus follower.

Canonical implementation of the ``passive-follower`` archetype documented
in ``examples/AGENT_POOL/finance/passive-follower.md``. An uninformed
conformist that observes the majority action and majority-fraction of
peers in a lookback window and mirrors the herd when consensus is strong
enough, sizing its trade proportional to consensus intensity.

Theoretical basis:
    Banerjee (1992) — simple model of herd behaviour.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Read ``majority_action`` (buy/sell/hold) and ``majority_fraction`` in
    [0, 1] from ``state.raw``.

    If ``majority_fraction <= 0.5 + consensus_threshold``: hold.
    Else:
        intensity = (majority_fraction - 0.5) / 0.5
        resource  = cash / price   if action == buy
        resource  = position       if action == sell
        quantity  = follow_fraction * intensity * resource * (1 + eps)
        with ``eps ~ N(0, noise_sigma)``, floored to zero.
        Emit ``action = majority_action`` if buy or sell; hold otherwise.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``consensus_threshold`` : float — excess above 0.5 to fire
                                 (default 0.10).
    * ``follow_fraction``     : float — resource fraction per action
                                 (default 0.15).
    * ``noise_sigma``         : float — sizing noise stddev (default 0.05).
    * ``lookback``            : int — peer observation window (default 10).
    * ``seed``                : optional int — RNG seed.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePassiveFollower(CanonicalRulePlayer):
    STRATEGY = "passive-follower"
    DISPLAY_NAME = "Passive Consensus Follower"
    SUMMARY = (
        "Uninformed conformist that mirrors the herd when peer consensus "
        "is strong, sized by consensus intensity (Banerjee 1992)."
    )
    # Reads majority_action / majority_fraction from state.raw.
    REQUIRES_FEATURES: tuple = ("majority_action", "majority_fraction")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["consensus_threshold"] = float(
            extras.get("consensus_threshold", 0.10)
        )
        self.state.custom_state["follow_fraction"] = float(
            extras.get("follow_fraction", 0.15)
        )
        self.state.custom_state["noise_sigma"] = float(
            extras.get("noise_sigma", 0.05)
        )
        self.state.custom_state["lookback"] = int(extras.get("lookback", 10))
        seed = extras.get("seed")
        self.state.custom_state["rng"] = random.Random(seed)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        consensus_th = self.state.custom_state["consensus_threshold"]
        follow_fraction = self.state.custom_state["follow_fraction"]
        sigma = self.state.custom_state["noise_sigma"]
        rng: random.Random = self.state.custom_state["rng"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        majority_action = state.raw_require("majority_action", cast=str)
        majority_fraction = state.raw_require("majority_fraction", cast=float)

        if majority_fraction <= 0.5 + consensus_th:
            return hold
        # Intensity in [0, 1] as (fraction - 0.5) / 0.5.
        intensity = max(0.0, (majority_fraction - 0.5) / 0.5)

        action = str(majority_action).lower()
        noise = rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        multiplier = max(0.0, 1.0 + noise)

        if action == "buy" and state.cash > 0 and state.price > 0:
            resource = state.cash / state.price
            quantity = follow_fraction * intensity * resource * multiplier
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if action == "sell" and state.position > 0:
            resource = state.position
            quantity = follow_fraction * intensity * resource * multiplier
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPassiveFollower(CanonicalLLMPlayer):
    STRATEGY = "passive-follower"
    DEFAULT_SYS_PROMPT = """\
You are a passive conformist. You have no independent information; you
simply watch what the majority of other traders are doing. When
consensus is strong (well past a bare majority), you follow — with your
position size scaling to how strong the consensus is. When peers are
split, you hold.

Output format:
<analysis>describe the peer consensus and your follow-on stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Follow the herd: buy or sell with the majority when consensus is well
past bare majority; hold when peers are split.
"""


__all__ = ["RulePassiveFollower", "LLMPassiveFollower"]
