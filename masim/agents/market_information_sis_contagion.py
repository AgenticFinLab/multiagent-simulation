"""Information SIS contagion — canonical market coordinator.

Profile: masim/agents/defines/market/information-sis-contagion.md
Mechanism: Linear SIS-style rumor contagion with truth-anchored correction,
           Allport-Postman leveling/sharpening distortion dynamics, and
           Gaussian noise (Daley-Kendall 1965 + Vosoughi-Roy-Aral 2018 +
           DiFonzo-Bordia 2007 + Allport-Postman 1947).
Broadcast: 9 fields — belief, prev_belief, belief_change, distortion,
           truth_value, num_spreaders, num_correctors, net_spread_intensity,
           round.

Transition equations:
    B(t+1) = clip(B(t) + alpha * NetSpread + beta * (Truth - B(t)) + eps, 0, 1)
    D(t+1) = clip(D(t) - l * D(t) + s * n_spreaders * (1 - Truth), 0, 1)
    eps ~ N(0, sigma^2)
    NetSpread = sum(intensity_i for spread) - sum(intensity_i for correct)
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator
from masim.format.broadcast import get_coordinator_action_types

logger = logging.getLogger("masim.agents.coordinator.information")

_VALID_ACTION_TYPES = get_coordinator_action_types("information-sis-contagion")


class MarketInformationSisContagion(CanonicalMarketCoordinator):
    """Population-level information field with SIS-style rumor contagion.

    Theoretical basis:
      - Daley & Kendall (1965) / Vosoughi, Roy & Aral (2018): SIS-style
        linear rumor contagion (alpha term — spread impact).
      - DiFonzo & Bordia (2007): truth-anchored correction force
        (beta term — pull toward ground truth).
      - Allport & Postman (1947): leveling (distortion decay) and
        sharpening (distortion growth per spreader per falsity gap).
      - Vosoughi-Roy-Aral (2018) / DeGroot (1974): Gaussian residual noise.
    """

    STRATEGY = "information-sis-contagion"
    DISPLAY_NAME = "SIS Rumor Contagion Information Field"
    SUMMARY = (
        "SIS-style belief contagion with truth-anchored correction, "
        "Allport-Postman distortion dynamics, and Gaussian noise."
    )
    BROADCAST_FIELDS = (
        "belief",
        "prev_belief",
        "belief_change",
        "distortion",
        "truth_value",
        "num_spreaders",
        "num_correctors",
        "net_spread_intensity",
        "round",
    )

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Initialize information-field state from extras.

        Required extras (raises KeyError on missing):
            initial_belief, rumor_truth_value (Truth), spread_impact (alpha),
            truth_correction (beta), leveling_rate (l), sharpening_rate (s),
            noise_std (sigma), initial_distortion, record_path,
            custom_state_hot_limit.
        """
        # --- Required extras (KeyError propagates on missing) ---
        initial_belief = extras["initial_belief"]
        rumor_truth_value = extras["rumor_truth_value"]
        spread_impact = extras["spread_impact"]
        truth_correction = extras["truth_correction"]
        leveling_rate = extras["leveling_rate"]
        sharpening_rate = extras["sharpening_rate"]
        noise_std = extras["noise_std"]
        initial_distortion = extras["initial_distortion"]
        _ = extras["record_path"]
        _ = extras["custom_state_hot_limit"]

        # --- Write initial state ---
        cs = self.state.custom_state
        cs["belief"] = float(initial_belief)
        cs["prev_belief"] = float(initial_belief)
        cs["distortion"] = float(initial_distortion)
        cs["truth_value"] = float(rumor_truth_value)
        cs["spread_impact"] = float(spread_impact)
        cs["truth_correction"] = float(truth_correction)
        cs["leveling_rate"] = float(leveling_rate)
        cs["sharpening_rate"] = float(sharpening_rate)
        cs["noise_std"] = float(noise_std)

        # --- History buffers ---
        cs["belief_history"] = self._make_history_buffer("belief")
        cs["distortion_history"] = self._make_history_buffer("distortion")
        cs["spread_count_history"] = self._make_history_buffer("spread_count")
        cs["correction_count_history"] = self._make_history_buffer("correction_count")

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's belief/distortion transition and return 9-field broadcast.

        Steps:
          1. Validate and aggregate inbound actions.
          2. Draw noise epsilon ~ N(0, sigma^2).
          3. Compute belief transition B(t+1).
          4. Compute distortion transition D(t+1).
          5. Clip both to [0, 1].
          6. Write state atomically.
          7. Return broadcast dict.
        """
        cs = self.state.custom_state

        # Read current state
        belief_t = cs["belief"]
        distortion_t = cs["distortion"]
        truth = cs["truth_value"]
        alpha = cs["spread_impact"]
        beta = cs["truth_correction"]
        leveling = cs["leveling_rate"]
        sharpening = cs["sharpening_rate"]
        sigma = cs["noise_std"]

        # 1. Aggregate inbound actions
        total_spread = 0.0
        total_correction = 0.0
        num_spreaders = 0
        num_correctors = 0

        for action in orders:
            if "action_type" not in action:
                raise ValueError(
                    f"Investor order missing required 'action_type' field: {action!r}"
                )
            action_type = action["action_type"]
            if action_type not in _VALID_ACTION_TYPES:
                raise ValueError(
                    f"Unknown action_type {action_type!r} for information-sis-contagion "
                    f"coordinator; valid actions are {sorted(_VALID_ACTION_TYPES)}."
                )

            if "intensity" not in action:
                raise ValueError(
                    f"Investor order missing required 'intensity' field: {action!r}"
                )
            try:
                intensity = float(action["intensity"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Investor order has non-numeric intensity "
                    f"{action['intensity']!r}: {action!r}"
                ) from exc
            if intensity < 0:
                raise ValueError(
                    f"Investor order has negative intensity {intensity}: {action!r}"
                )

            # Aggregate by action type (intensity == 0 with action != 'ignore'
            # is a semantic error caught above by intensity < 0 not applying;
            # zero-intensity spread/correct is a no-op which we allow because
            # it represents "attempted to act but had no effect", distinct
            # from 'ignore').
            if action_type == "spread" and intensity > 0:
                total_spread += intensity
                num_spreaders += 1
            elif action_type == "correct" and intensity > 0:
                total_correction += intensity
                num_correctors += 1

        net_spread = total_spread - total_correction

        # 2. Draw noise
        eps = random.gauss(0, sigma) if sigma > 0 else 0.0

        # 3. Compute belief transition
        b_raw = belief_t + alpha * net_spread + beta * (truth - belief_t) + eps

        # 4. Compute distortion transition (Allport-Postman leveling/sharpening)
        d_raw = (
            distortion_t
            - leveling * distortion_t
            + sharpening * num_spreaders * (1.0 - truth)
        )

        # 5. Clip to [0, 1]
        new_belief = max(0.0, min(1.0, b_raw))
        new_distortion = max(0.0, min(1.0, d_raw))

        # Compute belief change
        belief_change = new_belief - belief_t

        # 6. Write state atomically (prev_belief first for invariant #1)
        cs["prev_belief"] = belief_t
        cs["belief"] = new_belief
        cs["distortion"] = new_distortion

        # Append to history buffers
        cs["belief_history"].append(new_belief)
        cs["distortion_history"].append(new_distortion)
        cs["spread_count_history"].append(num_spreaders)
        cs["correction_count_history"].append(num_correctors)

        # 7. Return broadcast dict
        return {
            "belief": new_belief,
            "prev_belief": belief_t,
            "belief_change": belief_change,
            "distortion": new_distortion,
            "truth_value": truth,
            "num_spreaders": num_spreaders,
            "num_correctors": num_correctors,
            "net_spread_intensity": net_spread,
            "round": round_num,
        }


__all__ = ["MarketInformationSisContagion"]
