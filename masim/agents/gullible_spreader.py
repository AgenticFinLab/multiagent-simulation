"""gullible-spreader — Credulous rumor spreader (non-market agent).

Canonical implementation of the ``gullible-spreader`` archetype documented
in ``examples/AGENT_POOL/finance/gullible-spreader.md``. Belongs to an
opinion-dynamics / rumor-spreading domain rather than an investor market;
its native action space is ``{spread, ignore}`` with a spread intensity.

Adaptation to the ``InvestorOrder`` framework (per Golden Rule 6 —
faithful reproduction of the mechanism, not fabrication of a market
order): the agent maintains ``my_belief`` in ``custom_state`` and updates
it every round via credulous convergence toward ``env_belief``; it also
computes a ``spread_intensity`` for downstream analytics.  It always
emits ``InvestorOrder.hold`` because the underlying archetype does not
buy or sell an asset. Scenarios wanting to observe the belief/intensity
dynamics can inspect ``self.state.custom_state``.

Theoretical basis:
    Allport & Postman (1947) — The Psychology of Rumor.
    Buckner (1965) — A theory of rumor transmission.
    Vosoughi, Roy & Aral (2018) — The spread of true and false news
    online.

Decision rule (from AGENT_POOL profile §Behavioral Framework — belief
update reproduced verbatim; market order always ``hold`` because the
archetype has no InvestorOrder to emit):

    gap = env_belief - my_belief
    my_belief = clamp(my_belief + credulity * gap, 0.0, 1.0)
    if my_belief > spread_threshold:
        raw_intensity = my_belief * spread_eagerness
                        * (1 + distortion_amplification * distortion)
        spread_intensity = clamp(raw_intensity, 0.0, 1.0)
    else:
        spread_intensity = 0.0

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``credulity``               : float — adoption rate (default 0.8).
    * ``spread_eagerness``        : float — intensity multiplier (default 0.9).
    * ``distortion_amplification``: float — distortion boost (default 0.3).
    * ``initial_belief``          : float — starting belief (default 0.3).
    * ``spread_threshold``        : float — spread cut-off (default 0.2).

Scenario-specific inputs (via ``state.raw``, declared through
``REQUIRES_FEATURES``): ``env_belief``, ``distortion``. Both default to
0.0 when not broadcast.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleGullibleSpreader(CanonicalRulePlayer):
    STRATEGY = "gullible-spreader"
    DISPLAY_NAME = "Gullible Rumor Spreader"
    SUMMARY = (
        "Credulous spreader converging to environmental belief and "
        "propagating rumors (Allport & Postman 1947; Vosoughi et al. 2018)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "distortion")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["credulity"] = float(extras.get("credulity", 0.8))
        cs["spread_eagerness"] = float(extras.get("spread_eagerness", 0.9))
        cs["distortion_amplification"] = float(
            extras.get("distortion_amplification", 0.3)
        )
        cs["initial_belief"] = float(extras.get("initial_belief", 0.3))
        cs["spread_threshold"] = float(extras.get("spread_threshold", 0.2))
        cs["my_belief"] = cs["initial_belief"]
        cs["spread_intensity"] = 0.0

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        credulity = cs["credulity"]
        eagerness = cs["spread_eagerness"]
        distortion_amp = cs["distortion_amplification"]
        threshold = cs["spread_threshold"]

        env_belief = state.raw_require("env_belief", cast=float)
        distortion = state.raw_require("distortion", cast=float)

        # Step 1-2 — credulous belief update.
        my_belief = cs["my_belief"]
        gap = env_belief - my_belief
        my_belief = max(0.0, min(1.0, my_belief + credulity * gap))
        cs["my_belief"] = my_belief

        # Step 3-5 — spread intensity computation (recorded for scenario
        # analytics; no InvestorOrder direction is emitted because this
        # archetype is not an asset trader).
        if my_belief > threshold:
            raw_intensity = my_belief * eagerness * (1.0 + distortion_amp * distortion)
            cs["spread_intensity"] = max(0.0, min(1.0, raw_intensity))
        else:
            cs["spread_intensity"] = 0.0

        return InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )


class LLMGullibleSpreader(CanonicalLLMPlayer):
    STRATEGY = "gullible-spreader"
    DEFAULT_SYS_PROMPT = """\
You are a credulous rumor spreader. You quickly adopt the majority view
of your environment (env_belief) and, once you cross a minimum
conviction threshold, you propagate the rumor eagerly — especially in
distorted information environments. You do not trade assets; you only
adjust your belief and spread it.

Output format:
<analysis>state your belief update and whether you are spreading.</analysis>
<decision>{"action": "hold", "quantity": 0.0,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}. Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Update your belief toward the environmental view and spread if you
have crossed the conviction threshold. You do not trade.
"""


__all__ = ["RuleGullibleSpreader", "LLMGullibleSpreader"]
