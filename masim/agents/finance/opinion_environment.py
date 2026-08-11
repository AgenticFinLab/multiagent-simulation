"""opinion-environment — Non-trading opinion signal generator.

Canonical implementation of the ``opinion-environment`` archetype documented
in ``masim/agents/defines/finance/opinion-environment.md``. This is a
non-trading environment agent: it maintains an autoregressive opinion
state driven by price momentum and Gaussian shocks, and broadcasts it
without ever placing a trade.

Theoretical basis:
    DeGroot (1974) — weighted-average opinion dynamics.
    Hegselmann & Krause (2002) — bounded-confidence opinion models.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    epsilon ~ N(0, shock_sigma)
    raw = alpha * opinion + beta * price_momentum
          + (1 - alpha - beta) * epsilon
    opinion = clip(raw, -1, 1)
    action = hold, quantity = 0 (always).

    ``price_momentum`` uses the single-tick return exposed by
    ``StandardMarketState.price_change``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``alpha``          : float in [0,1] — autoregressive persistence
                            (default 0.70).
    * ``beta``           : float in [0,1] — momentum sensitivity
                            (default 0.20).
    * ``shock_sigma``    : float >= 0 — noise stddev (default 0.05).
    * ``initial_opinion``: float in [-1,1] — starting opinion (default 0.0).
    * ``seed``           : optional int — RNG seed.

Notes: The base clipper only touches quantity>0 orders, so a pure hold
always passes through unchanged. The evolving ``opinion`` value is stored
in ``custom_state["opinion"]`` so downstream tooling can inspect it.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleOpinionEnvironment(CanonicalRulePlayer):
    STRATEGY = "opinion-environment"
    DISPLAY_NAME = "Opinion Environment (Non-Trading)"
    SUMMARY = (
        "Non-trading environment agent broadcasting an autoregressive "
        "opinion signal driven by price momentum (DeGroot 1974)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["alpha"] = float(extras.get("alpha", 0.70))
        self.state.custom_state["beta"] = float(extras.get("beta", 0.20))
        self.state.custom_state["shock_sigma"] = float(
            extras.get("shock_sigma", 0.05)
        )
        self.state.custom_state["opinion"] = float(
            extras.get("initial_opinion", 0.0)
        )
        seed = extras.get("seed")
        self.state.custom_state["rng"] = random.Random(seed)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        alpha = self.state.custom_state["alpha"]
        beta = self.state.custom_state["beta"]
        sigma = self.state.custom_state["shock_sigma"]
        opinion = float(self.state.custom_state["opinion"])
        rng: random.Random = self.state.custom_state["rng"]

        momentum = state.price_change if state.price_change == state.price_change else 0.0
        epsilon = rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        residual_weight = max(0.0, 1.0 - alpha - beta)
        raw = alpha * opinion + beta * momentum + residual_weight * epsilon
        # Clamp to [-1, 1] as required by the profile.
        new_opinion = max(-1.0, min(1.0, raw))
        self.state.custom_state["opinion"] = new_opinion

        # Non-trading agent — always emit a hold.
        return InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )


class LLMOpinionEnvironment(CanonicalLLMPlayer):
    STRATEGY = "opinion-environment"
    DEFAULT_SYS_PROMPT = """\
You are the opinion environment. You do not trade — your job is to
maintain and broadcast a scalar sentiment signal in [-1, 1] that
evolves as a weighted mix of its own persistence, current market
momentum, and small random shocks. Every round you emit a hold order
and update the sentiment.

Output format:
<analysis>describe how sentiment is evolving with market momentum.</analysis>
<decision>{"action": "hold", "quantity": 0.0,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}).
Emit a hold order; internally update the opinion state using price
momentum and mean-reverting persistence.
"""


__all__ = ["RuleOpinionEnvironment", "LLMOpinionEnvironment"]
