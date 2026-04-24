"""MentalAccounting LLM Simulation

Mental accounting causes investors to treat money differently based on its source or intended use.

Design:
    - Market: Rule-based (same as Rule variant)
    - Investors: LLM-driven with distinct mental-accounting personas

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
from examples.MentalAccounting.LLM.prompts import (
    LLM_MENTAL_ACCOUNTANT_PROMPT,
    LLM_HOUSE_MONEY_PROMPT,
    LLM_RATIONAL_PORTFOLIO_PROMPT,
    LLM_SUNK_COST_PROMPT,
    LLM_NOISE_TRADER_PROMPT,
    LLM_USER_TEMPLATE,
)
from examples.MentalAccounting.Rule.players import Market  # noqa: F401

logger = logging.getLogger("MentalAccounting.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven mental accounting investors.

    Subclasses set _system_prompt to personalise behaviour.
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
                if payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]
                    self.state.custom_state["price_history"].append(payload["price"])

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["model"],
                generation_config={"temperature": llm_cfg.get("temperature", 0.3)},
            )
        return self._llm

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state.get("entry_price", 0.0)
        strategy_name = self.__class__.__name__

        pnl = (price - entry_price) / entry_price * 100 if entry_price > 0 else 0.0

        user_msg = LLM_USER_TEMPLATE.format(
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

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))
        quantity = max(0, quantity)

        # Enforce constraints
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


class LLMMentalAccountant(LLMInvestor):
    """LLM-driven MentalAccountant."""

    _system_prompt = LLM_MENTAL_ACCOUNTANT_PROMPT


class LLMHouseMoneyTrader(LLMInvestor):
    """LLM-driven HouseMoneyTrader."""

    _system_prompt = LLM_HOUSE_MONEY_PROMPT


class LLMRationalPortfolioManager(LLMInvestor):
    """LLM-driven RationalPortfolioManager."""

    _system_prompt = LLM_RATIONAL_PORTFOLIO_PROMPT


class LLMSunkCostHolder(LLMInvestor):
    """LLM-driven SunkCostHolder."""

    _system_prompt = LLM_SUNK_COST_PROMPT


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven NoiseTrader."""

    _system_prompt = LLM_NOISE_TRADER_PROMPT


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMMentalAccountant",
    "LLMHouseMoneyTrader",
    "LLMRationalPortfolioManager",
    "LLMSunkCostHolder",
    "LLMNoiseTrader",
]
