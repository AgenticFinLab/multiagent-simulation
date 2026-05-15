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
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer
from examples.llm_utils import parse_llm_response_with_thinking

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from ..Rule.players import InformationEnvironment
from .prompts import (
    RULELLM_GULLIBLE_SYS,
    RULELLM_DISTORTING_SYS,
    RULELLM_SKEPTICAL_SYS,
    RULELLM_FACTCHECKER_SYS,
    RULELLM_BYSTANDER_SYS,
)

logger = logging.getLogger("RumorSpreadRuleLLM")


class RuleLLMSocialAgent(GeneralPlayer):
    """Base class for hybrid Rule+LLM social agents in RumorSpread."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        llm_cfg = self.config.extras["llm"]
        self._llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        return self._llm

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

        if observation.inbounds:
            for inb in observation.inbounds:
                env_data = inb.payload
                self.state.custom_state["env_data"] = env_data
                self.state.custom_state["belief_history"].append(env_data["belief"])

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _build_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build user prompt with current environment state."""
        my_belief = self.state.custom_state["my_belief"]
        round_num = self.state.custom_state["round"]
        return (
            f"Round {round_num}\n"
            f"Population Belief: {env_data['belief']:.3f}  prev={env_data['prev_belief']:.3f}"
            f"  change={env_data['belief_change']:.3f}  distortion={env_data['distortion']:.3f}\n"
            f"Truth Value: {env_data['truth_value']:.3f}\n"
            f"Spreaders: {env_data['num_spreaders']}  Correctors: {env_data['num_correctors']}"
            f"  net_spread={env_data['net_spread_intensity']:.3f}\n"
            f"Your Personal Belief: {my_belief:.3f}\n"
            "Respond with <analysis>...</analysis> then "
            '<decision>{"action_type":"spread"|"ignore"|"correct","intensity":<0-1>,"reasoning":"..."}'
            "</decision>"
        )

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections."""
        return parse_llm_response_with_thinking(response_text)

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        env_data = self.state.custom_state["env_data"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(env_data)
        system_prompt = self._system_prompt
        llm_client = self._get_llm()

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

        action_type = decision["action_type"]
        intensity = float(decision["intensity"])
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
            "reasoning": decision["reasoning"][:120],
            "analysis": decision["analysis"],
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

    _system_prompt = RULELLM_GULLIBLE_SYS


class RuleLLMDistortingRelayer(RuleLLMSocialAgent):
    """Hybrid: Sharpening + assimilation rules + LLM distorting reasoning."""

    _system_prompt = RULELLM_DISTORTING_SYS


class RuleLLMSkepticalEvaluator(RuleLLMSocialAgent):
    """Hybrid: Critical evaluation + correction threshold + LLM skeptical reasoning."""

    _system_prompt = RULELLM_SKEPTICAL_SYS


class RuleLLMFactChecker(RuleLLMSocialAgent):
    """Hybrid: Active denial + credibility discount + LLM fact-checking reasoning."""

    _system_prompt = RULELLM_FACTCHECKER_SYS


class RuleLLMUninformedBystander(RuleLLMSocialAgent):
    """Hybrid: Random engagement rule + LLM casual reasoning."""

    _system_prompt = RULELLM_BYSTANDER_SYS


__all__ = [
    "InformationEnvironment",
    "RuleLLMSocialAgent",
    "RuleLLMGullibleSpreader",
    "RuleLLMDistortingRelayer",
    "RuleLLMSkepticalEvaluator",
    "RuleLLMFactChecker",
    "RuleLLMUninformedBystander",
]
