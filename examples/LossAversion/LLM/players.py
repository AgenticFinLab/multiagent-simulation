"""LossAversion LLM Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: LLM-driven with individual system prompts

All parameters are configured via players.yml config file.
"""

import logging
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from examples.LossAversion.LLM.prompts import (
    LLM_LOSS_AVERSE_PROMPT,
    LLM_BREAK_EVEN_PROMPT,
    LLM_RATIONAL_PROMPT,
    LLM_MOMENTUM_PROMPT,
    LLM_MARKET_MAKER_PROMPT,
    LLM_USER_TEMPLATE,
)
from examples.LossAversion.Rule.players import Market  # noqa: F401

logger = logging.getLogger("LossAversion.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven investors in LossAversion simulation.

    Subclasses set _system_prompt to their agent-specific persona.
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
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_price"] = extras.get(
                "initial_price", extras.get("entry_price", 100.0)
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(payload, dict) and payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state.get("price", 100.0)
        fundamental = self.state.custom_state.get("fundamental", 100.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]

        llm_cfg = self.config.extras.get("llm", {})
        llm = LangChainAPIInference(
            lm_name=llm_cfg["model"],
            generation_config={"temperature": llm_cfg.get("temperature", 0.3)},
        )

        user_msg = LLM_USER_TEMPLATE.format(
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        decision: Dict[str, Any] = {"action": "hold", "quantity": 0}
        for attempt in range(3):
            try:
                output = llm.run(
                    [InferInput(system_msg=self._system_prompt, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                break
            except (ValueError, RuntimeError) as exc:
                logger.debug(
                    "[%s] LLM parse failed (attempt %d): %s",
                    self.identity,
                    attempt + 1,
                    exc,
                )

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))

        # Enforce constraints
        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
            self.state.custom_state["entry_price"] = price
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision.get("reasoning", "")[:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMLossAverseInvestor(LLMInvestor):
    """LLM-driven LossAverseInvestor."""

    _system_prompt = LLM_LOSS_AVERSE_PROMPT


class LLMBreakEvenTrader(LLMInvestor):
    """LLM-driven BreakEvenTrader."""

    _system_prompt = LLM_BREAK_EVEN_PROMPT


class LLMRationalTrader(LLMInvestor):
    """LLM-driven RationalTrader."""

    _system_prompt = LLM_RATIONAL_PROMPT


class LLMMomentumTrader(LLMInvestor):
    """LLM-driven MomentumTrader."""

    _system_prompt = LLM_MOMENTUM_PROMPT


class LLMMarketMaker(LLMInvestor):
    """LLM-driven MarketMaker."""

    _system_prompt = LLM_MARKET_MAKER_PROMPT


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMLossAverseInvestor",
    "LLMBreakEvenTrader",
    "LLMRationalTrader",
    "LLMMomentumTrader",
    "LLMMarketMaker",
]
