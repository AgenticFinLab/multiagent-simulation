"""RumorSpreadRuleLLM - Hybrid Rule+LLM Rumor Propagation Simulation

Design:
    - InformationEnvironment coordinator: identical rule-based dynamics as RumorSpread
    - Social agents: LLM-powered, but each agent's system prompt embeds the explicit
      quantitative rules (formulas, thresholds) from the rule-based counterpart,
      alongside a rich persona/profile description.

This hybrid lets LLM agents exercise natural language reasoning while remaining
grounded in the same social science principles as the rule-based simulation.

All parameters are configured via players.yml config file.

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("RumorSpreadRuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# Reuse the same InformationEnvironment from Rule variant
from examples.RumorSpread.Rule.players import InformationEnvironment


class RuleLLMSocialAgent(GeneralPlayer):
    """
    Base class for hybrid Rule+LLM social agents.

    Each subclass uses a system prompt that encodes BOTH:
    - Persona description (who the agent is, behavioral traits)
    - Quantitative decision rules in text form (from rule-based)

    Parameters from config extras:
        - initial_belief, initial_credibility, custom_state_hot_limit, record_path
        - llm: sys_message, user_message, lm_name, generation_config
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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["my_belief"] = extras["initial_belief"]
            self.state.custom_state["credibility"] = extras["initial_credibility"]
            self.state.custom_state["belief_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "belief"),
                entry_limit=custom_state_hot_limit,
            )

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

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["belief_history"].append(env_data["belief"])

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
        """Build user prompt with current environment state."""
        my_belief = self.state.custom_state["my_belief"]
        round_num = self.state.custom_state["round"]

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                round=round_num,
                belief=env_data["belief"],
                prev_belief=env_data["prev_belief"],
                belief_change=env_data["belief_change"],
                distortion=env_data["distortion"],
                truth_value=env_data["truth_value"],
                num_spreaders=env_data["num_spreaders"],
                num_correctors=env_data["num_correctors"],
                net_spread_intensity=env_data["net_spread_intensity"],
                my_belief=my_belief,
            )

        return f"""
Round: {round_num}
Population Belief: {env_data['belief']:.3f} | Distortion: {env_data['distortion']:.3f} | Truth: {env_data['truth_value']:.3f}
Spreaders: {env_data['num_spreaders']} | Correctors: {env_data['num_correctors']}
Your Belief: {my_belief:.3f}

Respond with ONLY valid JSON:
{{"action_type": "spread"|"ignore"|"correct", "intensity": <0-1>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections."""
        return parse_llm_response_with_thinking(response_text)

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
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed (attempt {attempt+1}), retrying..."
                    )

        if decision is None:
            logger.warning(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}. Skipping."
            )
            action = {
                "action_type": "ignore",
                "intensity": 0.0,
                "agent_role": strategy_name,
                "agent_id": self.identity,
                "reasoning": "LLM parse failed",
                "analysis": "",
            }
            return {
                **action,
                "outbound_messages": [
                    {"payload": action, "content_type": "social_action"}
                ],
            }

        action_type = decision.get("action_type", "ignore")
        intensity = float(decision.get("intensity", 0.0))
        intensity = max(0.0, min(1.0, intensity))

        my_belief = self.state.custom_state["my_belief"]
        if action_type == "spread":
            my_belief = max(my_belief, env_data["belief"] * 0.5 + my_belief * 0.5)
        elif action_type == "correct":
            my_belief = min(my_belief, env_data["truth_value"] * 0.5 + my_belief * 0.5)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:25s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
            "reasoning": decision.get("reasoning", "")[:120],
            "analysis": decision.get("analysis", ""),
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


class RuleLLMGullibleSpreader(RuleLLMSocialAgent):
    """Hybrid: Allport & Postman leveling rules + LLM gullible reasoning."""

    pass


class RuleLLMDistortingRelayer(RuleLLMSocialAgent):
    """Hybrid: Sharpening + assimilation rules + LLM distorting reasoning."""

    pass


class RuleLLMSkepticalEvaluator(RuleLLMSocialAgent):
    """Hybrid: Critical evaluation + correction threshold + LLM skeptical reasoning."""

    pass


class RuleLLMFactChecker(RuleLLMSocialAgent):
    """Hybrid: Active denial + credibility discount + LLM fact-checking reasoning."""

    pass


class RuleLLMUninformedBystander(RuleLLMSocialAgent):
    """Hybrid: Random engagement rule + LLM casual reasoning."""

    pass
