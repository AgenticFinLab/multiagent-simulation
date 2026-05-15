"""MentalAccounting RuleLLM Simulation

Design:
    - Market: Rule-based (same as Rule variant)
    - Investors: Hybrid Rule+LLM — each agent's system prompt embeds the explicit
      quantitative rules alongside a rich persona description.

All parameters are configured via players.yml config file.
"""

import logging
import os
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from examples.MentalAccounting.RuleLLM.prompts import (
    RULELLM_MENTAL_ACCOUNTANT_SYS,
    RULELLM_HOUSE_MONEY_SYS,
    RULELLM_RATIONAL_PORTFOLIO_SYS,
    RULELLM_SUNK_COST_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_USER_TEMPLATE,
)
from examples.MentalAccounting.Rule.players import Market  # noqa: F401

logger = logging.getLogger("MentalAccounting.RuleLLM")


class RuleLLMInvestor(GeneralPlayer):
    """Base class for hybrid Rule+LLM mental accounting investors.

    Subclasses set _system_prompt with persona + quantitative rules.
    """

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_price"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]
                    self.state.custom_state["price_history"].append(payload["price"])

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )
        return self._llm

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state["entry_price"]
        strategy_name = self.__class__.__name__

        pnl = (price - entry_price) / entry_price * 100 if entry_price > 0 else 0.0

        user_msg = RULELLM_USER_TEMPLATE.format(
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
            entry_price=entry_price,
            pnl=pnl,
        )

        llm = self._get_llm()
        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
            infer_output = llm.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "type": "order",
                "action": "hold",
                "quantity": 0,
                "agent_type": strategy_name,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        action = decision["action"]
        quantity = int(decision["quantity"])
        quantity = max(0, quantity)

        if action == "buy" and quantity > 0:
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
                if self.state.custom_state["entry_price"] == 0:
                    self.state.custom_state["entry_price"] = price
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, position)
            if quantity > 0:
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity
        else:
            action = "hold"
            quantity = 0

        logger.debug(
            "[%-25s] R%d (%-25s): %s qty=%d | Cash=%.2f  Pos=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
            cash,
            position,
        )

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RuleLLMMentalAccountant(RuleLLMInvestor):
    """Hybrid: MentalAccountant rules + LLM reasoning."""

    _system_prompt = RULELLM_MENTAL_ACCOUNTANT_SYS


class RuleLLMHouseMoneyTrader(RuleLLMInvestor):
    """Hybrid: HouseMoneyTrader rules + LLM reasoning."""

    _system_prompt = RULELLM_HOUSE_MONEY_SYS


class RuleLLMRationalPortfolioManager(RuleLLMInvestor):
    """Hybrid: RationalPortfolioManager rules + LLM reasoning."""

    _system_prompt = RULELLM_RATIONAL_PORTFOLIO_SYS


class RuleLLMSunkCostHolder(RuleLLMInvestor):
    """Hybrid: SunkCostHolder rules + LLM reasoning."""

    _system_prompt = RULELLM_SUNK_COST_SYS


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """Hybrid: NoiseTrader rules + LLM reasoning."""

    _system_prompt = RULELLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMMentalAccountant",
    "RuleLLMHouseMoneyTrader",
    "RuleLLMRationalPortfolioManager",
    "RuleLLMSunkCostHolder",
    "RuleLLMNoiseTrader",
]
