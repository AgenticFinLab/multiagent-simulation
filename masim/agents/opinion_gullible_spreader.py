"""opinion-gullible-spreader — Gullible rumor spreader (opinion domain).

Canonical implementation of the ``gullible-spreader`` archetype documented in
``examples/AGENT_POOL/opinion/gullible-spreader.md``. Models a social media
user who accepts and relays unverified claims without scrutiny whenever the
emotional salience of a message exceeds a low gullibility threshold — the
classical Vosoughi/Roy/Aral (2018) mechanism by which false news diffuses
farther, faster, and more broadly than true news.

Domain projection (opinion-diffusion → InvestorOrder):
    The native decision space is {ignore, share-uncritically}. Since the
    canonical order schema only exposes {buy, sell, hold}, we project the
    sign of the current rumor belief onto trades:

        * ``ignore`` (salience below threshold, or share draw fails) → ``hold``
        * ``share``  →
              ``buy``  if ``my_belief > 0.5`` (bullish rumor bias),
              ``sell`` if ``my_belief < 0.5`` (bearish rumor bias),
              ``hold`` at ``my_belief == 0.5``.
        Quantity = ``p_share * base_size`` — full share intensity when
        the salience gate fires.

    Emotional-salience and env-belief signals are read from ``state.raw``.

Theoretical basis:
    Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false
    news online. *Science*, 359(6380), 1146-1151.
    https://doi.org/10.1126/science.aap9559

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    # Absorb the rumor uncritically (high adoption rate).
    my_belief         = clamp(my_belief + (env_belief - my_belief), 0, 1)
    # Share when emotional content clears personal gullibility threshold.
    if emotional_salience <= theta_gull:  hold
    # Bernoulli share draw with probability p_share.
    if u >= p_share:                       hold
    action = "share"   # projected as buy/sell by belief sign

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_gull``       : float, [0.10, 0.50] — gullibility threshold on
                              emotional salience (default 0.30).
    * ``p_share``          : float, [0.20, 0.80] — Bernoulli share probability
                              once the salience gate is cleared (default 0.50).
    * ``initial_belief``   : float, [0, 1] — starting ``my_belief`` (default 0.5).
    * ``base_size``        : float — order quantity at full share intensity
                              (default 100.0).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleOpinionGullibleSpreader(CanonicalRulePlayer):
    STRATEGY = "opinion-gullible-spreader"
    DISPLAY_NAME = "Gullible Rumor Spreader (Opinion)"
    SUMMARY = (
        "Shares unverified claims whenever emotional salience clears a low "
        "gullibility threshold (Vosoughi, Roy & Aral 2018)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "emotional_salience")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_gull"] = float(extras.get("theta_gull", 0.30))
        self.state.custom_state["p_share"] = float(extras.get("p_share", 0.50))
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.5)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        theta_gull = cs["theta_gull"]
        p_share = cs["p_share"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        emotional_salience = state.raw_require("emotional_salience", cast=float)

        # Gullible adoption: fully assimilate env_belief each tick.
        my_belief = float(cs.get("my_belief", 0.5))
        my_belief = _clamp(my_belief + (env_belief - my_belief), 0.0, 1.0)
        cs["my_belief"] = my_belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        # Salience gate.
        if emotional_salience <= theta_gull:
            return hold
        # Bernoulli share draw.
        if random.random() >= p_share:
            return hold

        quantity = p_share * base_size
        if quantity <= 0:
            return hold

        if my_belief > 0.5:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if my_belief < 0.5:
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMOpinionGullibleSpreader(CanonicalLLMPlayer):
    STRATEGY = "opinion-gullible-spreader"
    DEFAULT_SYS_PROMPT = """\
You are a gullible social media user. You accept and relay unverified claims
without scrutiny whenever the emotional salience of a message clears a low
personal threshold. You do not fact-check. When you share, you project your
current rumor belief onto the market: bullish rumor → buy, bearish rumor →
sell. Otherwise hold. False and emotionally charged news is exactly what
propagates farthest through your behaviour (Vosoughi, Roy & Aral 2018).

Output format:
<analysis>note salience vs threshold and current belief direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If the message is emotionally salient enough for you, share it (buy/sell by
belief sign); otherwise hold.
"""


__all__ = ["RuleOpinionGullibleSpreader", "LLMOpinionGullibleSpreader"]
