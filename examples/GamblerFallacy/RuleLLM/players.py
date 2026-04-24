"""GamblerFallacy RuleLLM Variant Players

Rule-embedded LLM-driven agents for the GamblerFallacy simulation.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference import InferInput, LangChainAPIInference

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.GamblerFallacy.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("GamblerFallacy.RuleLLM")


class RuleLLMInvestor(GeneralPlayer):
    """Base class for RuleLLM-driven GamblerFallacy investors."""

    _system_prompt_path: str = ""

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio and LLM client; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0
            await self._initialize_agent()

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def _initialize_agent(self) -> None:
        """Initialize LangChainAPIInference client from config."""
        llm_cfg = self.config.extras.get("llm", {})
        self._llm_params = {
            "lm_name": llm_cfg["lm_name"],
            "generation_config": llm_cfg["generation_config"],
        }
        self._llm_client = LangChainAPIInference(
            lm_name=self._llm_params["lm_name"],
            generation_config=self._llm_params["generation_config"],
        )

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state.pop("_llm_client", None)
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        if hasattr(self, "_llm_params"):
            self._llm_client = LangChainAPIInference(
                lm_name=self._llm_params["lm_name"],
                generation_config=self._llm_params["generation_config"],
            )

    async def decide(self) -> dict:
        """Call LLM with embedded rules; parse decision."""
        from examples.GamblerFallacy.RuleLLM.prompts import RULELLM_USER_TEMPLATE
        from masim.utils.prompt_loader import load_prompt

        system_msg = load_prompt(self._system_prompt_path)
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        portfolio_value = cash + position * price

        user_msg = RULELLM_USER_TEMPLATE.format(
            round=self.state.custom_state["round"],
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

        try:
            infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
            response = self._llm_client.run([infer_input]).outputs[0].response
            decision = parse_llm_response_with_thinking(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))
        price_val = self.state.custom_state["price"]

        if action == "buy":
            max_qty = int(cash / price_val) if price_val > 0 else 0
            quantity = min(quantity, max_qty, 1000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 1000)
        else:
            quantity = 0

        quantity = max(0, quantity)
        return {"action": action, "quantity": quantity}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RuleLLMStreakReversalTrader(RuleLLMInvestor):
    """RuleLLM-driven StreakReversalTrader: expects reversals after consecutive moves."""

    _system_prompt_path = (
        "examples.GamblerFallacy.RuleLLM.prompts:RULELLM_STREAK_REVERSAL_TRADER_SYS"
    )


class RuleLLMHotHandTrader(RuleLLMInvestor):
    """RuleLLM-driven HotHandTrader: believes winning streaks will continue."""

    _system_prompt_path = (
        "examples.GamblerFallacy.RuleLLM.prompts:RULELLM_HOT_HAND_TRADER_SYS"
    )


class RuleLLMIndependentAssessor(RuleLLMInvestor):
    """RuleLLM-driven IndependentAssessor: treats each price change as independent."""

    _system_prompt_path = (
        "examples.GamblerFallacy.RuleLLM.prompts:RULELLM_INDEPENDENT_ASSESSOR_SYS"
    )


class RuleLLMArbitrageur(RuleLLMInvestor):
    """RuleLLM-driven Arbitrageur: exploits mispricing from streak-based traders."""

    _system_prompt_path = (
        "examples.GamblerFallacy.RuleLLM.prompts:RULELLM_ARBITRAGEUR_SYS"
    )


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """RuleLLM-driven NoiseTrader: random uninformed trader."""

    _system_prompt_path = (
        "examples.GamblerFallacy.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS"
    )


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMStreakReversalTrader",
    "RuleLLMHotHandTrader",
    "RuleLLMIndependentAssessor",
    "RuleLLMArbitrageur",
    "RuleLLMNoiseTrader",
]
