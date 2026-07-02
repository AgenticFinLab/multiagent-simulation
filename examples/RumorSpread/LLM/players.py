"""RumorSpreadLLM - LLM-based Rumor Propagation Simulation

LLM agents with different information processing personalities:
    - Gullible Spreader
    - Distorting Relayer
    - Skeptical Evaluator
    - Fact Checker
    - Uninformed Bystander

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "RumorSpreadLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/RumorSpread/LLM/run_rumor_llm.py \
       -c configs/RumorSpread/LLM/simulation.yml
   ```

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
from masim.utils.llm_utils import is_retryable_llm_error
from examples.RumorSpread.llm_parser import parse_rumor_response

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from .prompts import (
    LLM_GULLIBLE_SYS,
    LLM_DISTORTING_SYS,
    LLM_SKEPTICAL_SYS,
    LLM_FACTCHECKER_SYS,
    LLM_BYSTANDER_SYS,
)

logger = logging.getLogger("RumorSpread.LLM")


class InformationEnvironment(GeneralPlayer):
    """
    Central information environment with rumor belief dynamics.

    Identical to Rule variant InformationEnvironment.

    Parameters from config extras:
        - rumor_truth_value, initial_belief, spread_impact, truth_correction
        - leveling_rate, sharpening_rate, noise_std, custom_state_hot_limit
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

        spread_actions = [a for a in actions if a["action_type"] == "spread"]
        correct_actions = [a for a in actions if a["action_type"] == "correct"]

        total_spread = sum(a["intensity"] for a in spread_actions)
        total_correction = sum(a["intensity"] for a in correct_actions)
        net_spread = total_spread - total_correction

        spread_impact = extras["spread_impact"]
        truth_correction = extras["truth_correction"]
        leveling_rate = extras["leveling_rate"]
        sharpening_rate = extras["sharpening_rate"]
        noise_std = extras["noise_std"]

        spread_effect = spread_impact * net_spread
        truth_effect = truth_correction * (truth_value - current_belief)
        noise = random.gauss(0, noise_std)

        new_belief = max(
            0.0, min(1.0, current_belief + spread_effect + truth_effect + noise)
        )

        leveling = leveling_rate * current_distortion
        sharpening = sharpening_rate * len(spread_actions) * (1.0 - truth_value)
        new_distortion = max(0.0, min(1.0, current_distortion - leveling + sharpening))

        self.state.custom_state["belief"] = new_belief
        self.state.custom_state["distortion"] = new_distortion
        self.state.custom_state["belief_history"].append(new_belief)
        self.state.custom_state["distortion_history"].append(new_distortion)
        self.state.custom_state["spread_count_history"].append(len(spread_actions))
        self.state.custom_state["correction_count_history"].append(len(correct_actions))

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


class LLMSocialAgent(GeneralPlayer):
    """Base class for LLM-powered social agents in RumorSpread."""

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

    def _build_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build user prompt with current environment data."""
        my_belief = self.state.custom_state["my_belief"]
        return (
            f"Round {env_data['round']}\n"
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
        """Parse LLM response with thinking and decision sections."""
        return parse_rumor_response(response_text)

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
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if not parse_error and not retryable_api_error:
                    raise
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed, retrying..."
                    )  # pylint: disable=logging-fstring-interpolation

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        action_type = decision["action_type"]
        intensity = float(decision["intensity"])
        reasoning = str(decision.pop("reasoning"))[:100]
        analysis = str(decision.pop("analysis"))

        # Update personal belief based on action
        my_belief = self.state.custom_state["my_belief"]
        if action_type == "spread":
            my_belief = max(my_belief, env_data["belief"] * 0.5 + my_belief * 0.5)
        elif action_type == "correct":
            my_belief = min(my_belief, env_data["truth_value"] * 0.5 + my_belief * 0.5)
        my_belief = max(0.0, min(1.0, my_belief))
        self.state.custom_state["my_belief"] = my_belief

        logger.debug(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:15s}): "
            f"A={action_type:7s} I={intensity:.3f} belief={my_belief:.3f}"
        )

        action = {
            "action_type": action_type,
            "intensity": intensity,
            "agent_role": strategy_name,
            "agent_id": self.identity,
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


class LLMGullibleSpreader(LLMSocialAgent):
    """LLM gullible spreader.

    Theory: simulation-bases.md §4.1
    """

    _system_prompt = LLM_GULLIBLE_SYS


class LLMDistortingRelayer(LLMSocialAgent):
    """LLM distorting relayer.

    Theory: simulation-bases.md §4.2
    """

    _system_prompt = LLM_DISTORTING_SYS


class LLMSkepticalEvaluator(LLMSocialAgent):
    """LLM skeptical evaluator.

    Theory: simulation-bases.md §4.3
    """

    _system_prompt = LLM_SKEPTICAL_SYS


class LLMFactChecker(LLMSocialAgent):
    """LLM fact checker.

    Theory: simulation-bases.md §4.4
    """

    _system_prompt = LLM_FACTCHECKER_SYS


class LLMUninformedBystander(LLMSocialAgent):
    """LLM uninformed bystander.

    Theory: simulation-bases.md §4.5
    """

    _system_prompt = LLM_BYSTANDER_SYS


__all__ = [
    "InformationEnvironment",
    "LLMSocialAgent",
    "LLMGullibleSpreader",
    "LLMDistortingRelayer",
    "LLMSkepticalEvaluator",
    "LLMFactChecker",
    "LLMUninformedBystander",
]
