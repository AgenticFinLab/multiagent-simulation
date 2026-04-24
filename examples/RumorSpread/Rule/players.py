"""RumorSpread - Rule-based Rumor Propagation Simulation

Phenomenon: Rumor Spread
    Rumors propagate through populations via serial transmission, with each
    retelling introducing distortion and amplification. Belief in unverified
    information spreads faster than corrections, producing collective error.

Theoretical Foundation:
    - Allport & Postman (1947): Psychology of Rumor — leveling, sharpening,
      and assimilation in serial transmission
    - Bordia & Rosnow (1998): Rumor as communication — content analysis approach
    - DiFonzo & Bordia (2007): Rumor psychology — how rumors help make sense
    - Shibutani (1966): Improvised news — rumor as collective problem-solving

Key Dynamics:
    1. Initial rumor seed introduced → some agents believe and relay
    2. Leveling: details lost in retelling → simplified narrative
    3. Sharpening: salient details exaggerated → more dramatic version
    4. Assimilation: distorted to fit pre-existing biases
    5. Skeptical agents resist → but corrections spread slower than rumors
    6. Belief converges on distorted version unless fact-checking is strong

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

logger = logging.getLogger("RumorSpread")


# =============================================================================
# InformationEnvironment — Coordinator with Rumor Dynamics
# =============================================================================


class InformationEnvironment(GeneralPlayer):
    """
    Central information environment tracking rumor spread dynamics.

    Rumor Belief Model:
        B(t+1) = B(t) + alpha * NetSpread + beta * (Truth - B(t)) + epsilon

    Where:
        - B(t): Average population belief in the rumor [0, 1]
        - alpha: Spread impact coefficient (how much agent actions change belief)
        - beta: Truth correction rate (how fast truth corrects belief)
        - Truth: Ground truth value (0 = false, 1 = true)
        - epsilon: Random noise in information transmission

    Key Parameters:
        - spread_impact: How strongly agent actions shift belief
        - truth_correction: Rate of truth-based correction
        - rumor_truth_value: 0.0 = completely false, 1.0 = true
        - initial_belief: Starting belief level
        - leveling_rate: Rate of detail loss (Allport & Postman)
        - sharpening_rate: Rate of exaggeration (Allport & Postman)

    All parameters configured via extras in players.yml.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "belief" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["belief"] = extras["initial_belief"]
            self.state.custom_state["distortion"] = 0.0
            self.state.custom_state["truth_value"] = extras["rumor_truth_value"]

            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["belief_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "belief"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["distortion_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "distortion"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["spread_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "spread_count"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["correction_count_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "correction_count"),
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
                    }
                )
        self.state.custom_state["actions"] = actions

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_belief = self.state.custom_state["belief"]
        current_distortion = self.state.custom_state["distortion"]
        truth_value = self.state.custom_state["truth_value"]
        actions = self.state.custom_state["actions"]

        # Aggregate agent actions
        spread_actions = [a for a in actions if a["action_type"] == "spread"]
        correct_actions = [a for a in actions if a["action_type"] == "correct"]
        ignore_actions = [a for a in actions if a["action_type"] == "ignore"]

        total_spread = sum(a["intensity"] for a in spread_actions)
        total_correction = sum(a["intensity"] for a in correct_actions)
        net_spread = total_spread - total_correction

        # Belief dynamics
        spread_impact = extras["spread_impact"]
        truth_correction = extras["truth_correction"]
        leveling_rate = extras["leveling_rate"]
        sharpening_rate = extras["sharpening_rate"]
        noise_std = extras["noise_std"]

        # Update belief: spread pushes up, correction pushes toward truth
        spread_effect = spread_impact * net_spread
        truth_effect = truth_correction * (truth_value - current_belief)
        noise = random.gauss(0, noise_std)

        new_belief = max(
            0.0, min(1.0, current_belief + spread_effect + truth_effect + noise)
        )

        # Distortion dynamics (Allport & Postman leveling + sharpening)
        # Leveling reduces distortion slowly; sharpening increases it
        num_spreaders = len(spread_actions)
        leveling = leveling_rate * current_distortion
        sharpening = sharpening_rate * num_spreaders * (1.0 - truth_value)

        new_distortion = max(0.0, min(1.0, current_distortion - leveling + sharpening))

        # Update state
        self.state.custom_state["belief"] = new_belief
        self.state.custom_state["distortion"] = new_distortion
        self.state.custom_state["belief_history"].append(new_belief)
        self.state.custom_state["distortion_history"].append(new_distortion)
        self.state.custom_state["spread_count_history"].append(len(spread_actions))
        self.state.custom_state["correction_count_history"].append(len(correct_actions))

        # Log
        logger.debug(f"\n{'='*70}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"[InfoEnv] Round {round_num}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Belief: {current_belief:.3f} → {new_belief:.3f}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Distortion: {current_distortion:.3f} → {new_distortion:.3f}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Truth Value: {truth_value:.3f}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Spreaders: {len(spread_actions)}, Correctors: {len(correct_actions)}"
        )
        logger.debug(f"  Net Spread Intensity: {net_spread:+.3f}")  # pylint: disable=logging-fstring-interpolation

        env_data = {
            "belief": new_belief,
            "prev_belief": current_belief,
            "belief_change": new_belief - current_belief,
            "distortion": new_distortion,
            "truth_value": truth_value,
            "num_spreaders": len(spread_actions),
            "num_correctors": len(correct_actions),
            "net_spread_intensity": net_spread,
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
    Base class for rumor simulation social agents.

    All parameters configured via extras in players.yml:
        - initial_belief, initial_credibility, custom_state_hot_limit
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "my_belief" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["my_belief"] = extras["initial_belief"]
            self.state.custom_state["credibility"] = extras["initial_credibility"]
            self.state.custom_state["belief_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "belief"),
                entry_limit=extras["custom_state_hot_limit"],
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["belief_history"].append(env_data["belief"])

    def _apply_intensity_constraints(self, intensity: float) -> float:
        """Clamp intensity to valid range."""
        return max(0.0, min(1.0, intensity))

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="social_action",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# GullibleSpreader — Destabilizing: Easily believes and actively spreads rumors
# =============================================================================


class GullibleSpreader(BaseSocialAgent):
    """
    Gullible rumor spreader who readily believes and amplifies unverified claims.

    Theory: Allport & Postman (1947) — Leveling
        Uncritical transmitters simplify and spread information without verification.
        They are the primary channel through which rumor content spreads.

    Behavior:
        - High credulity: believes information at face value
        - Spreads actively with high intensity
        - Updates belief strongly toward population belief
        - Amplifies distortion through uncritical retransmission

    Effect: STRONGLY DESTABILIZING — Primary rumor amplifier

    Formula:
        belief_update = credulity * (env_belief - my_belief)
        spread_intensity = my_belief * spread_eagerness

    Parameters from config extras:
        - credulity, spread_eagerness, distortion_amplification
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        env_belief = env_data["belief"]
        my_belief = self.state.custom_state["my_belief"]
        distortion = env_data["distortion"]

        credulity = extras["credulity"]
        spread_eagerness = extras["spread_eagerness"]
        distortion_amplification = extras["distortion_amplification"]

        # Update personal belief: move toward population belief with high credulity
        my_belief += credulity * (env_belief - my_belief)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        # Spread if belief exceeds threshold
        if my_belief > 0.2:
            intensity = (
                my_belief
                * spread_eagerness
                * (1.0 + distortion_amplification * distortion)
            )
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "spread"
        else:
            intensity = 0.0
            action_type = "ignore"

        strategy_name = "gullible_spreader"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# DistortingRelayer — Destabilizing: Exaggerates and simplifies when relaying
# =============================================================================


class DistortingRelayer(BaseSocialAgent):
    """
    Distorting relayer who introduces systematic errors during retransmission.

    Theory: Allport & Postman (1947) — Sharpening and Assimilation
        Serial transmission introduces leveling (detail loss), sharpening
        (salient detail exaggeration), and assimilation (bias-driven distortion).

    Behavior:
        - Moderate credulity but distorts content during relay
        - Amplifies dramatic or anxiety-provoking elements (sharpening)
        - Drops nuanced details (leveling)
        - Adapts rumor to personal worldview (assimilation)

    Effect: DESTABILIZING — Increases distortion while spreading

    Formula:
        belief_update = credulity * (env_belief + sharpening_bias - my_belief)
        spread_intensity = my_belief * relay_eagerness
        contributed_distortion = sharpening_factor * my_belief

    Parameters from config extras:
        - credulity, relay_eagerness, sharpening_factor, leveling_factor
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        env_belief = env_data["belief"]
        my_belief = self.state.custom_state["my_belief"]
        distortion = env_data["distortion"]

        credulity = extras["credulity"]
        relay_eagerness = extras["relay_eagerness"]
        sharpening_factor = extras["sharpening_factor"]
        leveling_factor = extras["leveling_factor"]

        # Update belief with sharpening bias (overweights dramatic elements)
        sharpening_bias = sharpening_factor * distortion
        my_belief += credulity * (env_belief + sharpening_bias - my_belief)
        # Leveling: reduce belief nuance
        my_belief = (
            my_belief * (1.0 - leveling_factor) + round(my_belief) * leveling_factor
        )
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        # Relay with distortion
        if my_belief > 0.25:
            intensity = my_belief * relay_eagerness
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "spread"
        else:
            intensity = 0.0
            action_type = "ignore"

        strategy_name = "distorting_relayer"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f} sharp={sharpening_bias:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# SkepticalEvaluator — Stabilizing: Critically evaluates before believing
# =============================================================================


class SkepticalEvaluator(BaseSocialAgent):
    """
    Skeptical evaluator who critically assesses information before accepting.

    Theory: Bordia & Rosnow (1998) — Rumor as communication
        Skeptical agents serve as informational gatekeepers. They evaluate
        source credibility, cross-check claims, and resist social pressure.

    Behavior:
        - Low credulity: demands evidence before believing
        - Updates belief slowly, weighted toward ground truth
        - Spreads corrections when confident rumor is false
        - Resists social proof — does not follow majority uncritically

    Effect: STABILIZING — Reduces rumor belief through critical evaluation

    Formula:
        belief_update = skepticism * (truth_value - my_belief) + (1-skepticism) * small_social_effect
        correction_intensity = (1 - my_belief) * correction_eagerness  if my_belief < threshold

    Parameters from config extras:
        - skepticism, correction_eagerness, belief_threshold
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        env_belief = env_data["belief"]
        truth_value = env_data["truth_value"]
        my_belief = self.state.custom_state["my_belief"]

        skepticism = extras["skepticism"]
        correction_eagerness = extras["correction_eagerness"]
        belief_threshold = extras["belief_threshold"]

        # Update belief: strong anchor to truth, weak social influence
        truth_pull = skepticism * (truth_value - my_belief)
        social_pull = (1.0 - skepticism) * 0.1 * (env_belief - my_belief)
        my_belief += truth_pull + social_pull
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        # Correct if confident rumor is false
        if my_belief < belief_threshold:
            intensity = (1.0 - my_belief) * correction_eagerness
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "correct"
        else:
            intensity = 0.0
            action_type = "ignore"

        strategy_name = "skeptical_evaluator"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# FactChecker — Stabilizing: Actively investigates and debunks false claims
# =============================================================================


class FactChecker(BaseSocialAgent):
    """
    Fact-checker who actively investigates claims and broadcasts corrections.

    Theory: DiFonzo & Bordia (2004, 2007) — Rumor correction and denial
        Effective rumor control requires active, credible denial. Fact-checking
        reduces belief by providing verified counter-information. However,
        corrections travel slower than rumors (the "implied truth effect").

    Behavior:
        - Very low credulity: requires verified evidence
        - Actively corrects misinformation with high credibility
        - Corrections are less contagious than rumors (slower spread)
        - More effective when distortion is high (obvious falsehoods)

    Effect: STRONGLY STABILIZING — Primary correction mechanism

    Formula:
        belief_update = strong_skepticism * (truth_value - my_belief)
        correction_intensity = fact_check_strength * (1 - belief) * (1 + distortion_bonus)
        correction_effectiveness = intensity * credibility_discount

    Parameters from config extras:
        - fact_check_strength, credibility_discount, distortion_sensitivity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        truth_value = env_data["truth_value"]
        my_belief = self.state.custom_state["my_belief"]
        distortion = env_data["distortion"]

        fact_check_strength = extras["fact_check_strength"]
        credibility_discount = extras["credibility_discount"]
        distortion_sensitivity = extras["distortion_sensitivity"]

        # Update belief: very strong anchor to truth
        my_belief += 0.8 * (truth_value - my_belief)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        # Actively correct when belief in rumor is high
        env_belief = env_data["belief"]
        if env_belief > 0.3:
            # Correction is stronger when distortion is high (easy to debunk)
            distortion_bonus = distortion_sensitivity * distortion
            raw_intensity = (
                fact_check_strength * (1.0 - my_belief) * (1.0 + distortion_bonus)
            )
            # Credibility discount: corrections travel slower than rumors
            intensity = raw_intensity * credibility_discount
            intensity = self._apply_intensity_constraints(intensity)
            action_type = "correct"
        else:
            intensity = 0.0
            action_type = "ignore"

        strategy_name = "fact_checker"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f} env_belief={env_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }


# =============================================================================
# UninformedBystander — Neutral: Random participation providing baseline
# =============================================================================


class UninformedBystander(BaseSocialAgent):
    """
    Uninformed bystander with random, low-engagement participation.

    Theory: Shibutani (1966) — Rumor as collective problem-solving
        Many people in a rumor's path are minimally engaged. They neither
        actively spread nor correct, but occasionally participate based on
        ambient social cues rather than deliberate evaluation.

    Behavior:
        - Low and random engagement
        - Occasionally spreads or ignores based on mood
        - Provides baseline activity level
        - Neither confirms nor denies systematically

    Effect: NEUTRAL — Provides background noise in information dynamics

    Parameters from config extras:
        - engagement_probability, spread_probability
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        env_belief = env_data["belief"]
        my_belief = self.state.custom_state["my_belief"]

        engagement_probability = extras["engagement_probability"]
        spread_probability = extras["spread_probability"]

        # Small social influence
        my_belief += 0.1 * (env_belief - my_belief)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        # Random engagement
        if random.random() < engagement_probability:
            if random.random() < spread_probability:
                intensity = random.uniform(0.1, 0.4) * my_belief
                action_type = "spread"
            else:
                intensity = random.uniform(0.1, 0.3)
                action_type = "ignore"
        else:
            intensity = 0.0
            action_type = "ignore"

        strategy_name = "uninformed_bystander"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }

__all__ = [
    "InformationEnvironment",
    "BaseSocialAgent",
    "GullibleSpreader",
    "DistortingRelayer",
    "SkepticalEvaluator",
    "FactChecker",
    "UninformedBystander",
]
