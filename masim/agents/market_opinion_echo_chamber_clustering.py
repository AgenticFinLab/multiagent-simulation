"""Opinion echo-chamber clustering — canonical market coordinator.

Profile: masim/agents/defines/market/opinion-echo-chamber-clustering.md
Mechanism: Linear polarization dynamics with centripetal moderation, cluster
           geometry derived from submitted opinions, and Gaussian noise
           (DeGroot 1974 + Sunstein 2001 + Del Vicario et al. 2016).
Broadcast: 10 fields — polarization, prev_polarization, polarization_change,
           mean_opinion, cluster_separation, cross_cutting_exposure,
           num_polarizers, num_depolarizers, net_polarization_intensity, round.

Transition equation:
    P(t+1) = clip(P(t) + alpha * NetPolarization + beta * (p* - P(t)) + eps, 0, 1)
    eps ~ N(0, sigma^2)
    NetPolarization = sum(intensity_i for polarize) - sum(intensity_i for depolarize)
    cluster_separation = mean(opinions[opinions >= 0]) - mean(opinions[opinions < 0])
    cross_cutting_exposure = |{i : |opinion_i| < threshold}| / |actions|
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional

from masim.agents._coordinator_base import CanonicalMarketCoordinator
from masim.format.broadcast import get_coordinator_action_types

logger = logging.getLogger("masim.agents.coordinator.opinion")

_VALID_ACTION_TYPES = get_coordinator_action_types("opinion-echo-chamber-clustering")


class MarketOpinionEchoChamberClustering(CanonicalMarketCoordinator):
    """Population-level opinion field with echo-chamber clustering dynamics.

    Theoretical basis:
      - DeGroot (1974): linear opinion-influence aggregation (alpha term).
      - Sunstein (2001) / Moscovici & Zavalloni (1969): centripetal
        moderation toward equilibrium p* (beta term).
      - Del Vicario et al. (2016): cluster geometry and cross-cutting
        exposure as derived observables.
      - Friedkin & Johnsen (1990): Gaussian residual noise.
    """

    STRATEGY = "opinion-echo-chamber-clustering"
    DISPLAY_NAME = "Echo-Chamber Clustering Opinion Field"
    SUMMARY = (
        "Linear polarization dynamics with centripetal moderation, "
        "cluster geometry, and Gaussian noise."
    )
    BROADCAST_FIELDS = (
        "polarization",
        "prev_polarization",
        "polarization_change",
        "mean_opinion",
        "cluster_separation",
        "cross_cutting_exposure",
        "num_polarizers",
        "num_depolarizers",
        "net_polarization_intensity",
        "round",
    )

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Initialize opinion-field state from extras.

        Required extras (raises KeyError on missing):
            initial_polarization, polarization_equilibrium (p*),
            polarization_impact (alpha), centripetal_force (beta),
            noise_std (sigma), moderate_opinion_threshold,
            record_path, custom_state_hot_limit.
        """
        # --- Required extras (KeyError propagates on missing) ---
        # Per profile §Lifecycle Mapping and §4.7.1.A, ALL of these are
        # REQUIRED and MUST raise KeyError when missing — no defaults.
        initial_polarization = extras["initial_polarization"]
        initial_mean_opinion = extras["initial_mean_opinion"]
        initial_cluster_separation = extras["initial_cluster_separation"]
        initial_cross_cutting_exposure = extras["initial_cross_cutting_exposure"]
        polarization_equilibrium = extras["polarization_equilibrium"]
        polarization_impact = extras["polarization_impact"]
        centripetal_force = extras["centripetal_force"]
        noise_std = extras["noise_std"]
        moderate_opinion_threshold = extras["moderate_opinion_threshold"]
        _ = extras["record_path"]
        _ = extras["custom_state_hot_limit"]

        # --- Write initial state ---
        cs = self.state.custom_state
        cs["polarization"] = float(initial_polarization)
        cs["prev_polarization"] = float(initial_polarization)
        cs["polarization_equilibrium"] = float(polarization_equilibrium)
        cs["polarization_impact"] = float(polarization_impact)
        cs["centripetal_force"] = float(centripetal_force)
        cs["noise_std"] = float(noise_std)
        cs["moderate_opinion_threshold"] = float(moderate_opinion_threshold)
        cs["mean_opinion"] = float(initial_mean_opinion)
        cs["cluster_separation"] = float(initial_cluster_separation)
        cs["cross_cutting_exposure"] = float(initial_cross_cutting_exposure)

        # --- History buffers ---
        cs["polarization_history"] = self._make_history_buffer("polarization")
        cs["mean_opinion_history"] = self._make_history_buffer("mean_opinion")
        cs["cluster_separation_history"] = self._make_history_buffer(
            "cluster_separation"
        )
        cs["polarize_count_history"] = self._make_history_buffer("polarize_count")
        cs["depolarize_count_history"] = self._make_history_buffer("depolarize_count")

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's polarization transition and return 10-field broadcast.

        Steps:
          1. Validate and aggregate inbound actions.
          2. Draw noise epsilon ~ N(0, sigma^2).
          3. Compute raw polarization transition.
          4. Clip to [0, 1].
          5. Derive mean_opinion, cluster_separation, cross_cutting_exposure.
          6. Write state atomically.
          7. Return broadcast dict.
        """
        cs = self.state.custom_state

        # Read current state
        polarization_t = cs["polarization"]
        p_star = cs["polarization_equilibrium"]
        alpha = cs["polarization_impact"]
        beta = cs["centripetal_force"]
        sigma = cs["noise_std"]
        threshold = cs["moderate_opinion_threshold"]

        # 1. Aggregate inbound actions
        total_polarize = 0.0
        total_depolarize = 0.0
        num_polarizers = 0
        num_depolarizers = 0
        submitted_opinions: List[float] = []

        for action in orders:
            if "action_type" not in action:
                raise ValueError(
                    f"Investor order missing required 'action_type' field: {action!r}"
                )
            action_type = action["action_type"]
            if action_type not in _VALID_ACTION_TYPES:
                raise ValueError(
                    f"Unknown action_type {action_type!r} for opinion-echo-chamber-clustering "
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

            # 'opinion' is optional per the coordinator profile — agents may
            # withhold their opinion.  BUT if present, it MUST be numeric.
            opinion: Optional[float] = None
            if "opinion" in action and action["opinion"] is not None:
                try:
                    opinion = float(action["opinion"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Investor order has non-numeric opinion "
                        f"{action['opinion']!r}: {action!r}"
                    ) from exc

            # Aggregate intensity by action type (zero-intensity polarize /
            # depolarize is a documented no-op — "wanted to act, had no
            # effect" — distinct from action='neutral').
            if action_type == "polarize" and intensity > 0:
                total_polarize += intensity
                num_polarizers += 1
            elif action_type == "depolarize" and intensity > 0:
                total_depolarize += intensity
                num_depolarizers += 1

            # Collect opinion for moment computation regardless of action_type
            if opinion is not None:
                submitted_opinions.append(opinion)

        net_polarization = total_polarize - total_depolarize

        # 2. Draw noise
        eps = random.gauss(0, sigma) if sigma > 0 else 0.0

        # 3. Compute raw polarization transition
        p_raw = (
            polarization_t
            + alpha * net_polarization
            + beta * (p_star - polarization_t)
            + eps
        )

        # 4. Clip to [0, 1]
        new_polarization = max(0.0, min(1.0, p_raw))

        # 5. Derive moment observables
        if submitted_opinions:
            new_mean_opinion = sum(submitted_opinions) / len(submitted_opinions)
            # Clip mean_opinion to [-1, 1] for safety
            new_mean_opinion = max(-1.0, min(1.0, new_mean_opinion))

            # Cluster separation: mean(right) - mean(left)
            right_opinions = [o for o in submitted_opinions if o >= 0]
            left_opinions = [o for o in submitted_opinions if o < 0]

            right_mean = (
                sum(right_opinions) / len(right_opinions) if right_opinions else 0.0
            )
            left_mean = (
                sum(left_opinions) / len(left_opinions) if left_opinions else 0.0
            )
            new_cluster_separation = right_mean - left_mean

            # Cross-cutting exposure: fraction with |opinion| < threshold
            center_count = sum(
                1 for o in submitted_opinions if abs(o) < threshold
            )
            new_cross_cutting_exposure = center_count / len(submitted_opinions)
        else:
            # Zero inbound actions: carry forward from previous state
            new_mean_opinion = cs["mean_opinion"]
            new_cluster_separation = cs["cluster_separation"]
            new_cross_cutting_exposure = cs["cross_cutting_exposure"]

        # Compute polarization change
        polarization_change = new_polarization - polarization_t

        # 6. Write state atomically (prev_polarization first for invariant #1)
        cs["prev_polarization"] = polarization_t
        cs["polarization"] = new_polarization
        cs["mean_opinion"] = new_mean_opinion
        cs["cluster_separation"] = new_cluster_separation
        cs["cross_cutting_exposure"] = new_cross_cutting_exposure

        # Append to history buffers
        cs["polarization_history"].append(new_polarization)
        cs["mean_opinion_history"].append(new_mean_opinion)
        cs["cluster_separation_history"].append(new_cluster_separation)
        cs["polarize_count_history"].append(num_polarizers)
        cs["depolarize_count_history"].append(num_depolarizers)

        # 7. Return broadcast dict
        return {
            "polarization": new_polarization,
            "prev_polarization": polarization_t,
            "polarization_change": polarization_change,
            "mean_opinion": new_mean_opinion,
            "cluster_separation": new_cluster_separation,
            "cross_cutting_exposure": new_cross_cutting_exposure,
            "num_polarizers": num_polarizers,
            "num_depolarizers": num_depolarizers,
            "net_polarization_intensity": net_polarization,
            "round": round_num,
        }


__all__ = ["MarketOpinionEchoChamberClustering"]
