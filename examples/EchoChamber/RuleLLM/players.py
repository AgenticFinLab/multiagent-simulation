"""EchoChamberRuleLLM - Hybrid Rule+LLM Echo Chamber Polarization Simulation

Design:
    - OpinionEnvironment: identical rule-based polarization dynamics as EchoChamber.Rule
    - Social agents: LLM-powered, but each agent's system prompt embeds the explicit
      quantitative rules (formulas, thresholds) from the rule-based counterpart,
      alongside a rich persona/profile description.

This hybrid lets LLM agents exercise natural language reasoning while remaining
grounded in the same social-psychological principles as the rule-based simulation,
enabling meaningful comparison across three variants:
    EchoChamber       - pure rule-based
    EchoChamberLLM    - pure LLM (persona only)
    EchoChamberRuleLLM - hybrid (persona + explicit rules in prompt)

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "EchoChamberRuleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/EchoChamber/RuleLLM/run_echo_chamber_rulellm.py \
       -c configs/EchoChamber/RuleLLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import logging
import os
import json as _json
import math
import random
import re as _re
import sys
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Add examples directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from masim.utils.llm_utils import is_retryable_llm_error

logger = logging.getLogger("EchoChamberRuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# OpinionEnvironment — Rule-Based Coordinator (identical to EchoChamber.Rule)
# =============================================================================


class OpinionEnvironment(GeneralPlayer):
    """
    Central opinion environment tracking polarization dynamics.

    Opinion Dynamics Model (rule-based, unchanged from EchoChamber.Rule):
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

    Parameters from config extras:
        - initial_polarization, polarization_impact, centripetal_force
        - noise_std, custom_state_hot_limit, record_path
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
            self.state.custom_state["mean_opinion"] = extras["initial_mean_opinion"]
            self.state.custom_state["cluster_separation"] = extras[
                "initial_cluster_separation"
            ]
            self.state.custom_state["cross_cutting_exposure"] = extras[
                "initial_cross_cutting_exposure"
            ]

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
                        "reasoning": action["reasoning"],
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
        valid_action_types = {"polarize", "neutral", "depolarize"}
        for action in actions:
            if action["action_type"] not in valid_action_types:
                raise ValueError(f"Invalid social action type: {action['action_type']}")
            if not 0.0 <= action["intensity"] <= 1.0:
                raise ValueError(f"Action intensity outside [0, 1]: {action['intensity']}")
            if not -1.0 <= action["opinion"] <= 1.0:
                raise ValueError(f"Opinion outside [-1, 1]: {action['opinion']}")

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
        center_pull = centripetal_force * (
            extras["polarization_equilibrium"] - current_polarization
        )
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
        if actions:
            threshold = extras["moderate_opinion_threshold"]
            center_agents = sum(
                1 for action in actions if abs(action["opinion"]) < threshold
            )
            new_cross_cutting = center_agents / len(actions)
        else:
            new_cross_cutting = self.state.custom_state["cross_cutting_exposure"]

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
        if actions:
            logger.debug("  RuleLLM Actions (%d):", len(actions))
            for a in actions:
                logger.debug(
                    "    %s [%s]: A=%s I=%.3f",
                    a["agent_id"],
                    a["agent_role"],
                    a["action_type"],
                    a["intensity"],
                )
                if a["reasoning"]:
                    logger.debug("      -> %s...", a["reasoning"][:80])

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
# Base RuleLLM Social Agent
# =============================================================================


class RuleLLMSocialAgent(GeneralPlayer):
    """
    Base class for hybrid Rule+LLM opinion agents.

    Each subclass uses a system prompt that encodes BOTH:
    - Persona description (who the agent is, behavioral traits)
    - Quantitative decision rules in text form (the exact formula from rule-based)

    The agent uses LLM reasoning to interpret opinion environment data and apply
    those rules, potentially deviating slightly when qualitative context warrants.

    Parameters from config extras:
        - initial_opinion, custom_state_hot_limit, record_path
        - llm: sys_message, user_message, lm_name, generation_config
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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            initial_opinion = extras["initial_opinion"]
            if extras["alternate_initial_sign"] and initial_opinion != 0.0:
                instance_number = int(self.identity.rsplit("_", 1)[1])
                if instance_number % 2 == 0:
                    initial_opinion = -initial_opinion
            self.state.custom_state["my_opinion"] = initial_opinion

            load_dotenv()
            llm_config = extras["llm"]
            lm_name = llm_config["lm_name"]
            generation_config = llm_config["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config

            llm_client = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["llm_client"] = llm_client

            self.state.custom_state["opinion_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "opinion"),
                entry_limit=custom_state_hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["opinion_history"].append(
                    self.state.custom_state["my_opinion"]
                )

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = state["state"].custom_state
            if "llm_client" in custom:
                custom = dict(custom)
                del custom["llm_client"]
                state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                llm_client = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )
                custom["llm_client"] = llm_client

    def _build_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build user prompt with current opinion environment data, including round number."""
        my_opinion = self.state.custom_state["my_opinion"]
        round_num = self.state.custom_state["round"]

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                round=env_data["round"],
                polarization=env_data["polarization"],
                prev_polarization=env_data["prev_polarization"],
                polarization_change=env_data["polarization_change"],
                mean_opinion=env_data["mean_opinion"],
                cluster_separation=env_data["cluster_separation"],
                cross_cutting_exposure=env_data["cross_cutting_exposure"],
                num_polarizers=env_data["num_polarizers"],
                num_depolarizers=env_data["num_depolarizers"],
                net_polarization_intensity=env_data["net_polarization_intensity"],
                my_opinion=my_opinion,
            )

        # Fallback inline template
        return f"""
Round: {round_num}
Polarization: {env_data['polarization']:.3f} | Mean Opinion: {env_data['mean_opinion']:.3f}
Cluster Separation: {env_data['cluster_separation']:.3f}
Cross-cutting Exposure: {env_data['cross_cutting_exposure']:.3f}
Polarizers: {env_data['num_polarizers']} | Depolarizers: {env_data['num_depolarizers']}
Your Opinion: {my_opinion:.3f}

Respond with ONLY valid JSON:
{{"action_type": "polarize"|"neutral"|"depolarize", "intensity": <float 0-1>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the canonical tagged EchoChamber decision contract.

        EchoChamber expects: {"action_type": ..., "intensity": ..., "reasoning": ...}
        Both tags are required so malformed output is retried rather than accepted
        through an undocumented fallback format.
        """
        analysis_match = _re.search(
            r"<analysis>(.*?)</analysis>", response_text, _re.DOTALL
        )
        decision_match = _re.search(
            r"<decision>(.*?)</decision>", response_text, _re.DOTALL
        )
        if analysis_match is None or not analysis_match.group(1).strip():
            raise ValueError("Missing or empty <analysis> section")
        if decision_match is None or not decision_match.group(1).strip():
            raise ValueError("Missing or empty <decision> section")

        analysis = analysis_match.group(1).strip()
        decision_json = decision_match.group(1).strip()
        try:
            parsed = _json.loads(decision_json)
        except _json.JSONDecodeError:
            raise ValueError(f"Failed to parse decision JSON: {decision_json[:100]}")

        required_fields = ["action_type", "intensity", "reasoning"]
        missing = [f for f in required_fields if f not in parsed or parsed[f] is None]
        if missing:
            raise ValueError(f"Fields missing or null in LLM response: {missing}")
        action_type = str(parsed["action_type"]).lower()
        if action_type not in {"polarize", "neutral", "depolarize"}:
            raise ValueError(f"Invalid action_type: {parsed['action_type']!r}")
        if isinstance(parsed["intensity"], bool):
            raise ValueError(f"Invalid intensity: {parsed['intensity']!r}")
        try:
            intensity = float(parsed["intensity"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid intensity: {parsed['intensity']!r}") from exc
        if not math.isfinite(intensity) or not 0.0 <= intensity <= 1.0:
            raise ValueError(f"Intensity outside [0, 1]: {intensity!r}")
        reasoning = str(parsed["reasoning"]).strip()
        if not reasoning:
            raise ValueError("Empty reasoning")

        parsed["action_type"] = action_type
        parsed["intensity"] = intensity
        parsed["reasoning"] = reasoning
        parsed["analysis"] = analysis
        return parsed

    def _clamp_opinion(self, opinion: float) -> float:
        """Clamp opinion to valid range [-1, 1]."""
        return max(-1.0, min(1.0, opinion))

    def _apply_intensity_constraints(self, intensity: float) -> float:
        """Clamp intensity to valid range [0, 1]."""
        return max(0.0, min(1.0, intensity))

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        llm_client = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(env_data)

        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        max_retries = int(llm_config["max_retries"])
        if max_retries < 1:
            raise ValueError("extras.llm.max_retries must be at least 1")
        decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if not parse_error and not retryable_api_error:
                    raise
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM decision failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        action_type = decision["action_type"]
        intensity = float(decision["intensity"])
        reasoning = str(decision.pop("reasoning"))
        analysis = str(decision.pop("analysis"))

        # Update opinion based on LLM-decided action type
        # Opinion shifts follow the same direction as the rule-based counterpart
        my_opinion = self.state.custom_state["my_opinion"]
        polarize_step = float(self.config.extras["polarize_opinion_step"])
        depolarize_step = float(self.config.extras["depolarize_opinion_step"])
        if action_type == "polarize":
            direction = 1 if my_opinion >= 0 else -1
            my_opinion += polarize_step * intensity * direction
        elif action_type == "depolarize":
            my_opinion *= 1.0 - depolarize_step * intensity
        my_opinion = self._clamp_opinion(my_opinion)
        self.state.custom_state["my_opinion"] = my_opinion

        logger.debug(
            "[%s] R%d (%s): A=%s I=%.3f opinion=%.3f",
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
            "reasoning": reasoning,
            "analysis": analysis,
        }

        return {
            **action,
            "outbound_messages": [{"payload": action, "content_type": "social_action"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="social_action",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete Hybrid Agent Types
# =============================================================================


class RuleLLMIdeologue(RuleLLMSocialAgent):
    """RuleLLM ideologue — in-group amplification formula + LLM reasoning on echo chamber dynamics. Theory: simulation-bases.md §4.1."""


class RuleLLMConformist(RuleLLMSocialAgent):
    """RuleLLM conformist — Asch conformity formula + LLM group alignment reasoning. Theory: simulation-bases.md §4.2."""


class RuleLLMCriticalThinker(RuleLLMSocialAgent):
    """RuleLLM critical thinker — Isenberg depolarization formula + LLM evidence evaluation. Theory: simulation-bases.md §4.3."""


class RuleLLMBridgeBuilder(RuleLLMSocialAgent):
    """RuleLLM bridge builder — centering formula + LLM cross-group engagement reasoning. Theory: simulation-bases.md §4.4."""


class RuleLLMPassiveFollower(RuleLLMSocialAgent):
    """RuleLLM passive follower — Lazarsfeld drift formula + LLM low-engagement reasoning. Theory: simulation-bases.md §4.5."""


__all__ = [
    "OpinionEnvironment",
    "RuleLLMSocialAgent",
    "RuleLLMIdeologue",
    "RuleLLMConformist",
    "RuleLLMCriticalThinker",
    "RuleLLMBridgeBuilder",
    "RuleLLMPassiveFollower",
]
