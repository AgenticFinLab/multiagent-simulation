"""SVBBankRun LLM Simulation

March 2023 SVB collapse — $42B deposit outflow in one day triggered by social media panic.

Design:
    - Market: Rule-based coordinator (identical to SVBBankRun.Rule.Market).
    - Investors: LLM-powered agents with unique personas defined in prompts.py.
      Each agent calls an LLM to decide whether to buy / sell / hold based on
      current price, fundamental value, and their portfolio state.

All parameters configured via players.yml.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from examples.llm_utils import parse_llm_response_with_thinking
from .prompts import (
    LLM_DEPOSITOR_SYS,
    LLM_SOCIAL_MEDIA_INFLUENCER_SYS,
    LLM_BANK_MANAGER_SYS,
    LLM_REGULATOR_SYS,
    LLM_BOND_TRADER_SYS,
)
from ..Rule.players import Market  # noqa: F401 — re-exported

logger = logging.getLogger("SVBBankRun.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven SVBBankRun investors."""

    _system_prompt: str = ""
    _llm: Optional[LangChainAPIInference] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        if self._llm is None:
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

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["price"] = market_data["price"]
                self.state.custom_state["fundamental"] = market_data["fundamental"]
                self.state.custom_state["deviation"] = market_data["deviation"]

    def _build_prompt(self) -> str:
        """Build user prompt from current market state."""
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        return (
            f"Round {round_num} — Market Update\n"
            f"Current Price: ${price:.2f}  Fundamental: ${fundamental:.2f}  "
            f"Deviation: {deviation * 100:+.2f}%\n"
            f"Portfolio — Cash: ${cash:.2f}  Position: {position} shares  "
            f"Value: ${portfolio_value:.2f}\n\n"
            "Based on your strategy and current conditions, decide your action.\n"
            "Respond with <analysis>...</analysis> then <decision>...</decision> containing "
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer}'
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        strategy_name = self.__class__.__name__
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        decision: Dict[str, Any] = {"action": "hold", "quantity": 0}
        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except (ValueError, KeyError):
                if attempt == max_retries - 1:
                    logger.warning(
                        "[%s] LLM parse failed after %d attempts; holding.",
                        self.identity,
                        max_retries,
                    )
                    decision = {"action": "hold", "quantity": 0}

        action = decision["action"]
        quantity = int(decision["quantity"])

        # Validate and constrain
        valid_actions = ["buy", "sell", "hold"]
        if action not in valid_actions:
            action = "hold"
            quantity = 0
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))

        # Update portfolio
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d (%s): action=%s qty=%d | Cash=%.2f Pos=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": decision["reasoning"][:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMDepositor(LLMInvestor):
    """LLM-driven depositor managing savings under uncertainty."""

    _system_prompt = LLM_DEPOSITOR_SYS


class LLMSocialMediaInfluencer(LLMInvestor):
    """LLM-driven social media influencer amplifying market signals."""

    _system_prompt = LLM_SOCIAL_MEDIA_INFLUENCER_SYS


class LLMBankManager(LLMInvestor):
    """LLM-driven bank manager handling duration risk."""

    _system_prompt = LLM_BANK_MANAGER_SYS


class LLMRegulator(LLMInvestor):
    """LLM-driven regulator intervening with guarantees."""

    _system_prompt = LLM_REGULATOR_SYS


class LLMBondTrader(LLMInvestor):
    """LLM-driven bond trader based on interest rate expectations."""

    _system_prompt = LLM_BOND_TRADER_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMDepositor",
    "LLMSocialMediaInfluencer",
    "LLMBankManager",
    "LLMRegulator",
    "LLMBondTrader",
]
