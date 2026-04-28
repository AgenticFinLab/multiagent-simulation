"""EchoChamber - Rule-based Echo Chamber Polarization Simulation

Phenomenon: Echo Chamber Polarization
    Like-minded individuals reinforce each other's views through homophilic
    interaction, producing group polarization — where group members converge
    on positions more extreme than any individual initially held.

Theoretical Foundation:
    - Sunstein (2001): Echo Chambers — deliberative enclaves drive polarization
    - Pariser (2011): Filter Bubble — algorithmic curation reinforces beliefs
    - Moscovici & Zavalloni (1969): Group polarization after discussion
    - Isenberg (1986): Persuasive arguments + social comparison drive extremity

Key Dynamics:
    1. Initial moderate opinions distributed across the spectrum
    2. Homophily: agents preferentially interact with similar others
    3. In-group reinforcement pushes opinions toward extremes
    4. Cross-cutting exposure is reduced (selective exposure)
    5. Critical thinkers and bridge builders resist polarization
    6. Over time, population splits into polarized clusters

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("EchoChamber")


# =============================================================================
# OpinionEnvironment — Coordinator with Polarization Dynamics
# =============================================================================


class OpinionEnvironment(GeneralPlayer):
    """
    Central opinion environment tracking polarization dynamics.

    Opinion Dynamics Model:
        P(t+1) = P(t) + alpha * NetPolarization + beta * CentripetalForce + epsilon

    Where:
        - P(t): Population polarization index (variance of opinions)
        - alpha: Polarization impact coefficient (agent actions' effect)
        - beta: Centripetal force (moderate center-pull, typically weak)
        - epsilon: Random noise in opinion dynamics

    Additional State Variables:
        - mean_opinion: Population average opinion [-1, 1]
        - cluster_separation: Distance between left and right cluster means
        - cross_cutting_exposure: Fraction of interactions across groups

    Key Parameters:
        - polarization_impact: How strongly agent actions shift polarization
        - centripetal_force: Moderate center-pull rate (usually weak)
        - noise_std: Random perturbation in opinion dynamics
        - initial_polarization: Starting polarization level

    All parameters configured via extras in players.yml.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "polarization" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["polarization"] = extras["initial_polarization"]
            self.state.custom_state["mean_opinion"] = 0.0
            self.state.custom_state["cluster_separation"] = 0.0
            self.state.custom_state["cross_cutting_exposure"] = 0.5

            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["polarization_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "polarization"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["mean_opinion_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "mean_opinion"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["cluster_separation_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "cluster_separation"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["polarize_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "polarize_count"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["depolarize_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "depolarize_count"),
                entry_limit=custom_state_hot_limit,
            )

        actions = []
        if observation.inbounds:
            for inb in observation.inbounds:
                action = inb.payload
                actions.append(
                    {
                        "agent_id": inb.sender_id,
                        "action_type": action["action_type"],
                        "intensity": action["intensity"],
                        "agent_role": action["agent_role"],
                        "opinion": action["opinion"],
                    }
                )
        self.state.custom_state["actions"] = actions

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_polarization = self.state.custom_state["polarization"]
        actions = self.state.custom_state["actions"]

        # Aggregate agent actions
        polarize_actions = [a for a in actions if a["action_type"] == "polarize"]
        depolarize_actions = [a for a in actions if a["action_type"] == "depolarize"]
        neutral_actions = [a for a in actions if a["action_type"] == "neutral"]

        total_polarize = sum(a["intensity"] for a in polarize_actions)
        total_depolarize = sum(a["intensity"] for a in depolarize_actions)
        net_polarization = total_polarize - total_depolarize

        # Collect submitted opinions for aggregation
        submitted_opinions = [a["opinion"] for a in actions if a["opinion"] is not None]

        # Polarization dynamics
        polarization_impact = extras["polarization_impact"]
        centripetal_force = extras["centripetal_force"]
        noise_std = extras["noise_std"]

        # Update polarization: agent actions push it, center-pull resists
        action_effect = polarization_impact * net_polarization
        # Centripetal force: weak pull toward moderate center
        center_pull = centripetal_force * (0.3 - current_polarization)
        noise = random.gauss(0, noise_std)

        new_polarization = max(
            0.0, min(1.0, current_polarization + action_effect + center_pull + noise)
        )

        # Compute mean opinion from submitted agent opinions
        if submitted_opinions:
            new_mean_opinion = sum(submitted_opinions) / len(submitted_opinions)
        else:
            new_mean_opinion = self.state.custom_state["mean_opinion"]

        # Compute cluster separation (distance between extremes)
        if submitted_opinions:
            left_opinions = [o for o in submitted_opinions if o < 0]
            right_opinions = [o for o in submitted_opinions if o >= 0]
            left_mean = (
                sum(left_opinions) / len(left_opinions) if left_opinions else 0.0
            )
            right_mean = (
                sum(right_opinions) / len(right_opinions) if right_opinions else 0.0
            )
            new_cluster_separation = right_mean - left_mean
        else:
            new_cluster_separation = self.state.custom_state["cluster_separation"]

        # Cross-cutting exposure: fraction of actions from agents near center
        center_agents = sum(1 for a in actions if abs(a["opinion"] or 0) < 0.3)
        total_agents = max(len(actions), 1)
        new_cross_cutting = center_agents / total_agents

        # Update state
        self.state.custom_state["polarization"] = new_polarization
        self.state.custom_state["mean_opinion"] = new_mean_opinion
        self.state.custom_state["cluster_separation"] = new_cluster_separation
        self.state.custom_state["cross_cutting_exposure"] = new_cross_cutting

        self.state.custom_state["polarization_history"].append(new_polarization)
        self.state.custom_state["mean_opinion_history"].append(new_mean_opinion)
        self.state.custom_state["cluster_separation_history"].append(
            new_cluster_separation
        )
        self.state.custom_state["polarize_count_history"].append(len(polarize_actions))
        self.state.custom_state["depolarize_count_history"].append(
            len(depolarize_actions)
        )

        # Log
        logger.debug("\n%s", "=" * 70)
        logger.debug("[OpinionEnv] Round %d", round_num)
        logger.debug(
            "  Polarization: %.3f -> %.3f", current_polarization, new_polarization
        )
        logger.debug("  Mean Opinion: %.3f", new_mean_opinion)
        logger.debug("  Cluster Separation: %.3f", new_cluster_separation)
        logger.debug(
            "  Polarizers: %d, Depolarizers: %d",
            len(polarize_actions),
            len(depolarize_actions),
        )
        logger.debug("  Net Polarization Intensity: %+.3f", net_polarization)
        logger.debug("  Cross-cutting Exposure: %.3f", new_cross_cutting)

        env_data = {
            "polarization": new_polarization,
            "prev_polarization": current_polarization,
            "polarization_change": new_polarization - current_polarization,
            "mean_opinion": new_mean_opinion,
            "cluster_separation": new_cluster_separation,
            "cross_cutting_exposure": new_cross_cutting,
            "num_polarizers": len(polarize_actions),
            "num_depolarizers": len(depolarize_actions),
            "net_polarization_intensity": net_polarization,
            "round": round_num,
        }

        return {
            "env_data": env_data,
            "outbound_messages": [
                {"payload": env_data, "content_type": "environment_update"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="environment_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Base Social Agent
# =============================================================================


class BaseSocialAgent(GeneralPlayer):
    """
    Base class for echo chamber simulation social agents.

    Each agent holds a personal opinion in [-1, 1] and interacts with
    the opinion environment by submitting actions (polarize, depolarize,
    or neutral) along with their current opinion.

    All parameters configured via extras in players.yml:
        - initial_opinion, custom_state_hot_limit
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "my_opinion" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["my_opinion"] = extras["initial_opinion"]
            self.state.custom_state["opinion_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "opinion"),
                entry_limit=extras["custom_state_hot_limit"],
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["opinion_history"].append(
                    self.state.custom_state["my_opinion"]
                )

    def _apply_intensity_constraints(self, intensity: float) -> float:
        """Clamp intensity to valid range [0, 1]."""
        return max(0.0, min(1.0, intensity))

    def _clamp_opinion(self, opinion: float) -> float:
        """Clamp opinion to valid range [-1, 1]."""
        return max(-1.0, min(1.0, opinion))

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="social_action",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Ideologue — Destabilizing: Strongly held views, amplifies in-group consensus
# =============================================================================


class Ideologue(BaseSocialAgent):
    """
    Ideologue who holds strong views and amplifies in-group consensus.

    Theory: simulation-bases.md §4.1 — Ideologue
    Theoretical basis: Sunstein (2001) echo chamber amplification; group polarization
    occurs when like-minded individuals discuss shared concerns, driving opinions extreme.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        mean_opinion = env_data["mean_opinion"]
        my_opinion = self.state.custom_state["my_opinion"]

        in_group_weight = extras["in_group_weight"]
        extremity_boost = extras["extremity_boost"]
        out_group_discount = extras["out_group_discount"]
        spread_eagerness = extras["spread_eagerness"]

        # Determine if mean opinion is in-group (same sign) or out-group
        if my_opinion * mean_opinion > 0:
            # In-group signal: amplify and push toward extreme
            group_signal = mean_opinion * extremity_boost
            opinion_update = in_group_weight * (group_signal - my_opinion)
        else:
            # Out-group signal: heavily discount opposing views
            opinion_update = out_group_discount * (mean_opinion - my_opinion)

        my_opinion += opinion_update
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        # Polarize when opinion is strong
        if abs(my_opinion) > 0.3:
            intensity = abs(my_opinion) * spread_eagerness
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "polarize"
        else:
            intensity = 0.0
            action_type = "neutral"

        strategy_name = "ideologue"
        logger.debug(
            "[%-25s] R%s (%-20s): A=%-10s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# Conformist — Destabilizing: Adopts prevailing group opinion
# =============================================================================


class Conformist(BaseSocialAgent):
    """
    Conformist who adopts prevailing group opinion, reinforcing homophily.

    Theory: simulation-bases.md §4.2 — Conformist
    Theoretical basis: Asch (1951) conformity; Sunstein (2001) group polarization;
    conformists amplify existing group tendencies by adopting the prevailing opinion.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        mean_opinion = env_data["mean_opinion"]
        my_opinion = self.state.custom_state["my_opinion"]

        conformity = extras["conformity"]
        conformity_eagerness = extras["conformity_eagerness"]
        group_proximity_threshold = extras["group_proximity_threshold"]

        # Conform to the nearest group mean
        # Determine local group: same sign as current opinion
        local_group_mean = mean_opinion
        if my_opinion < 0 and mean_opinion >= 0:
            # Conformist leans left but mean is right: pulled toward left cluster
            local_group_mean = mean_opinion - abs(mean_opinion) * 0.5
        elif my_opinion >= 0 and mean_opinion < 0:
            local_group_mean = mean_opinion + abs(mean_opinion) * 0.5

        opinion_update = conformity * (local_group_mean - my_opinion)
        my_opinion += opinion_update
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        # Polarize if opinion is strong enough
        if abs(my_opinion) > group_proximity_threshold:
            intensity = abs(my_opinion) * conformity_eagerness
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "polarize"
        else:
            intensity = 0.0
            action_type = "neutral"

        strategy_name = "conformist"
        logger.debug(
            "[%-25s] R%s (%-20s): A=%-10s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# CriticalThinker — Stabilizing: Evaluates evidence, resists group pressure
# =============================================================================


class CriticalThinker(BaseSocialAgent):
    """
    Critical thinker who evaluates evidence and resists group pressure.

    Theory: simulation-bases.md §4.3 — CriticalThinker
    Theoretical basis: Isenberg (1986) persuasive arguments vs social comparison;
    critical thinkers resist social proof and move opinion slowly on merit alone.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        polarization = env_data["polarization"]
        mean_opinion = env_data["mean_opinion"]
        my_opinion = self.state.custom_state["my_opinion"]

        critical_weight = extras["critical_weight"]
        critical_eagerness = extras["critical_eagerness"]
        evidence_sensitivity = extras["evidence_sensitivity"]

        # Critical thinkers move toward center when polarization is high
        # Evidence signal: moderate center, stronger when polarization is high
        evidence_signal = -my_opinion * evidence_sensitivity * polarization
        opinion_update = critical_weight * (evidence_signal - my_opinion * 0.1)
        # Small movement: critical thinkers change slowly
        opinion_update *= 0.3
        my_opinion += opinion_update
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        # Depolarize: pull toward center when polarization is high
        if polarization > 0.3:
            intensity = abs(my_opinion - 0.0) * critical_eagerness
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "depolarize"
        else:
            intensity = 0.0
            action_type = "neutral"

        strategy_name = "critical_thinker"
        logger.debug(
            "[%-25s] R%s (%-20s): A=%-10s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# BridgeBuilder — Stabilizing: Engages across groups, reduces polarization
# =============================================================================


class BridgeBuilder(BaseSocialAgent):
    """
    Bridge builder who actively engages across groups to reduce polarization.

    Theory: simulation-bases.md §4.4 — BridgeBuilder
    Theoretical basis: Sunstein (2001) deliberative democracy; Pariser (2011) serendipity
    by design; bridge builders increase cross-cutting exposure and find common ground.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        cluster_separation = env_data["cluster_separation"]
        my_opinion = self.state.custom_state["my_opinion"]

        bridge_weight = extras["bridge_weight"]
        bridge_strength = extras["bridge_strength"]
        centering_tendency = extras["centering_tendency"]

        # Pull toward moderate center
        opinion_update = bridge_weight * (0.0 - my_opinion) * centering_tendency
        my_opinion += opinion_update
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        # Depolarize more intensely when clusters are far apart
        if cluster_separation > 0.5:
            intensity = bridge_strength * min(cluster_separation, 1.0)
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "depolarize"
        elif cluster_separation > 0.2:
            intensity = bridge_strength * cluster_separation * 0.5
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "depolarize"
        else:
            intensity = 0.0
            action_type = "neutral"

        strategy_name = "bridge_builder"
        logger.debug(
            "[%-25s] R%s (%-20s): A=%-10s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# PassiveFollower — Neutral: Low engagement, occasional alignment
# =============================================================================


class PassiveFollower(BaseSocialAgent):
    """
    Passive follower with low engagement and occasional group alignment.

    Theory: simulation-bases.md §4.5 — PassiveFollower
    Theoretical basis: Lazarsfeld & Merton (1954) mass communication; passive followers
    drift toward whichever group they are closest to, providing background population mass.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        mean_opinion = env_data["mean_opinion"]
        my_opinion = self.state.custom_state["my_opinion"]

        engagement_probability = extras["engagement_probability"]
        drift_rate = extras["drift_rate"]
        alignment_strength = extras["alignment_strength"]

        # Small drift toward population mean
        drift = drift_rate * (mean_opinion - my_opinion)
        my_opinion += drift
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        # Random engagement
        if random.random() < engagement_probability:
            if abs(my_opinion) > 0.3:
                intensity = abs(my_opinion) * alignment_strength
                intensity = self._apply_intensity_constraints(intensity)
                action_type = "polarize"
            else:
                intensity = random.uniform(0.05, 0.2)
                action_type = "neutral"
        else:
            intensity = 0.0
            action_type = "neutral"

        strategy_name = "passive_follower"
        logger.debug(
            "[%-25s] R%s (%-20s): A=%-10s I=%.3f opinion=%.3f",
            self.identity,
            round_num,
            strategy_name,
            action_type,
            intensity,
            my_opinion,
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "opinion": my_opinion,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


__all__ = [
    "OpinionEnvironment",
    "Ideologue",
    "Conformist",
    "CriticalThinker",
    "BridgeBuilder",
    "PassiveFollower",
]
