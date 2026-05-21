"""EchoChamberLLM - LLM-based Echo Chamber Polarization Simulation

LLM agents with different opinion-environment personalities:
    - Ideologue: Strong opinion holder
    - Conformist: Group opinion adopter
    - Critical Thinker: Evidence evaluator
    - Bridge Builder: Cross-group engager
    - Passive Bystander: Low-engagement participant

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "EchoChamberLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/EchoChamber/LLM/run_echo_chamber_llm.py \
       -c configs/EchoChamber/LLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import logging
import os
import json
import random
import re
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

from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking

logger = logging.getLogger("EchoChamberLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class OpinionEnvironment(GeneralPlayer):
    """
    Central opinion environment with polarization dynamics.

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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["polarization"] = extras["initial_polarization"]
            self.state.custom_state["mean_opinion"] = 0.0
            self.state.custom_state["cluster_separation"] = 0.0
            self.state.custom_state["cross_cutting_exposure"] = 0.5

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

        polarize_actions = [a for a in actions if a["action_type"] == "polarize"]
        depolarize_actions = [a for a in actions if a["action_type"] == "depolarize"]

        total_polarize = sum(a["intensity"] for a in polarize_actions)
        total_depolarize = sum(a["intensity"] for a in depolarize_actions)
        net_polarization = total_polarize - total_depolarize

        submitted_opinions = [a["opinion"] for a in actions if a["opinion"] is not None]

        polarization_impact = extras["polarization_impact"]
        centripetal_force = extras["centripetal_force"]
        noise_std = extras["noise_std"]

        action_effect = polarization_impact * net_polarization
        center_pull = centripetal_force * (0.3 - current_polarization)
        noise = random.gauss(0, noise_std)

        new_polarization = max(
            0.0, min(1.0, current_polarization + action_effect + center_pull + noise)
        )

        if submitted_opinions:
            new_mean_opinion = sum(submitted_opinions) / len(submitted_opinions)
        else:
            new_mean_opinion = self.state.custom_state["mean_opinion"]

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

        center_agents = sum(1 for a in actions if abs(a["opinion"] or 0) < 0.3)
        total_agents = max(len(actions), 1)
        new_cross_cutting = center_agents / total_agents

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

        logger.debug("\n%s", "=" * 70)
        logger.debug("[OpinionEnv] Round %d", round_num)
        logger.debug(
            "  Polarization: %.3f -> %.3f", current_polarization, new_polarization
        )
        logger.debug("  Mean Opinion: %.3f", new_mean_opinion)
        logger.debug("  Cluster Separation: %.3f", new_cluster_separation)
        if actions:
            logger.debug("  LLM Actions (%d):", len(actions))
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


class LLMSocialAgent(GeneralPlayer):
    """
    Base class for LLM-powered opinion agents.

    Parameters from config extras:
        - initial_opinion, custom_state_hot_limit, record_path, llm config
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

            self.state.custom_state["my_opinion"] = extras["initial_opinion"]

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
        """Build user prompt with current opinion environment data."""
        my_opinion = self.state.custom_state["my_opinion"]
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

        return f"""
Current Opinion Environment (Round {env_data['round']}):
- Polarization Index: {env_data['polarization']:.3f}
- Mean Opinion: {env_data['mean_opinion']:.3f}
- Cluster Separation: {env_data['cluster_separation']:.3f}
- Your Personal Opinion: {my_opinion:.3f}

Respond with ONLY valid JSON:
{{"action_type": "polarize"|"neutral"|"depolarize", "intensity": <float 0-1>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections.

        EchoChamber expects: {"action_type": ..., "intensity": ..., "reasoning": ...}
        The shared ``parse_llm_response_with_thinking`` validates for financial
        trading fields, so we do our own field validation here.
        """
        analysis = ""
        decision_json = None

        # Extract analysis from <analysis>...</analysis> or <think>...</think>
        analysis_match = re.search(
            r"<analysis>(.*?)</analysis>", response_text, re.DOTALL
        )
        if not analysis_match:
            analysis_match = re.search(
                r"<think>(.*?)</think>", response_text, re.DOTALL
            )
        if analysis_match:
            analysis = analysis_match.group(1).strip()

        # Extract decision from <decision>...</decision>
        decision_match = re.search(
            r"<decision>(.*?)</decision>", response_text, re.DOTALL
        )
        if decision_match:
            decision_json = decision_match.group(1).strip()

        # Fallback: code block or raw JSON
        if not decision_json:
            code_match = re.search(
                r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL
            )
            if code_match:
                decision_json = code_match.group(1).strip()
            else:
                json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
                if json_match:
                    decision_json = json_match.group(0)

        if not decision_json:
            raise ValueError(
                f"No decision JSON found in response: {response_text[:100]}"
            )

        try:
            parsed = json.loads(decision_json)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse decision JSON: {decision_json[:100]}")

        # Validate EchoChamber-specific fields
        required_fields = ["action_type", "intensity", "reasoning"]
        missing = [f for f in required_fields if f not in parsed or parsed[f] is None]
        if missing:
            raise ValueError(f"Fields missing or null in LLM response: {missing}")
        action_type = str(parsed["action_type"]).lower()
        if action_type not in {"polarize", "neutral", "depolarize"}:
            raise ValueError(f"Invalid action_type: {parsed['action_type']!r}")
        try:
            intensity = float(parsed["intensity"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid intensity: {parsed['intensity']!r}") from exc
        reasoning = str(parsed["reasoning"]).strip()
        if not reasoning:
            raise ValueError("Empty reasoning")

        parsed["action_type"] = action_type
        parsed["intensity"] = max(0.0, min(1.0, intensity))
        parsed["reasoning"] = reasoning
        parsed["analysis"] = analysis
        return parsed

    def _clamp_opinion(self, opinion: float) -> float:
        """Clamp opinion to valid range [-1, 1]."""
        return max(-1.0, min(1.0, opinion))

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        llm_client = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(env_data)

        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        max_retries = 3
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
                    logger.debug("[%s] LLM decision failed, retrying...", self.identity)

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        action_type = decision["action_type"]
        intensity = float(decision["intensity"])
        reasoning = str(decision.pop("reasoning"))[:100]
        analysis = str(decision.pop("analysis"))

        # Update opinion based on LLM action
        my_opinion = self.state.custom_state["my_opinion"]
        if action_type == "polarize":
            my_opinion += 0.05 * (1 if my_opinion >= 0 else -1)
        elif action_type == "depolarize":
            my_opinion *= 0.95
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


class LLMIdeologue(LLMSocialAgent):
    """LLM-driven ideologue — amplifies in-group consensus, rejects out-group information. Theory: simulation-bases.md §4.1."""


class LLMConformist(LLMSocialAgent):
    """LLM-driven conformist — adopts prevailing group opinion, reinforcing homophily. Theory: simulation-bases.md §4.2."""


class LLMCriticalThinker(LLMSocialAgent):
    """LLM-driven critical thinker — evaluates evidence independently, resists social proof. Theory: simulation-bases.md §4.3."""


class LLMBridgeBuilder(LLMSocialAgent):
    """LLM-driven bridge builder — engages across groups, depolarizes by finding common ground. Theory: simulation-bases.md §4.4."""


class LLMPassiveBystander(LLMSocialAgent):
    """LLM-driven passive bystander — low engagement, occasional group alignment, background mass. Theory: simulation-bases.md §4.5."""


__all__ = [
    "OpinionEnvironment",
    "LLMSocialAgent",
    "LLMIdeologue",
    "LLMConformist",
    "LLMCriticalThinker",
    "LLMBridgeBuilder",
    "LLMPassiveBystander",
]
