"""FramingEffect RuleLLM Variant Players

Rule-embedded LLM-driven agents for the FramingEffect simulation.
"""

import importlib
import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.FramingEffect.Rule.players import Market
from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from examples.FramingEffect.RuleLLM.prompts import RULELLM_USER_TEMPLATE

logger = logging.getLogger("FramingEffect.RuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RuleLLMInvestor(GeneralPlayer):
    """Base class for RuleLLM-driven FramingEffect investors."""

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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0
            await self._initialize_agent()

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        """Initialize LangChainAPIInference client from config."""
        llm_cfg = self.config.extras["llm"]
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

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
                response = self._llm_client.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed (attempt %d), retrying: %s",
                        self.identity,
                        attempt + 1,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM decision contract failed after "
                f"{max_retries} retries: {last_error}"
            )

        action = decision["action"]
        if action not in ("buy", "sell", "hold"):
            raise ValueError(f"[{self.identity}] Invalid LLM action: {action}")
        bid_price = float(decision["bid_price"])
        reasoning = decision["reasoning"]
        analysis = decision["analysis"]
        quantity = int(decision["quantity"])
        price_val = self.state.custom_state["price"]

        if action == "buy":
            max_qty = int(cash / price_val) if price_val > 0 else 0
            quantity = min(quantity, max_qty, 1000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 1000)
        else:
            quantity = 0

        quantity = max(0, quantity)
        return {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": analysis,
            "strategy": self.__class__.__name__,
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
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
            "bid_price": decision_payload["bid_price"],
            "quantity": quantity,
            "reasoning": decision_payload["reasoning"],
            "analysis": decision_payload["analysis"],
            "agent_type": self.__class__.__name__,
            "strategy": decision_payload["strategy"],
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RuleLLMGainFrameFollower(RuleLLMInvestor):
    """RuleLLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.FramingEffect.RuleLLM.prompts:RULELLM_GAIN_FRAME_FOLLOWER_SYS"
    )


class RuleLLMLossFrameReactor(RuleLLMInvestor):
    """RuleLLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.FramingEffect.RuleLLM.prompts:RULELLM_LOSS_FRAME_REACTOR_SYS"
    )


class RuleLLMFrameInvariantTrader(RuleLLMInvestor):
    """RuleLLM-driven FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.FramingEffect.RuleLLM.prompts:RULELLM_FRAME_INVARIANT_TRADER_SYS"
    )


class RuleLLMArbitrageFramer(RuleLLMInvestor):
    """RuleLLM-driven ArbitrageFramer: exploits framing-induced mispricing. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.FramingEffect.RuleLLM.prompts:RULELLM_ARBITRAGE_FRAMER_SYS"
    )


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """RuleLLM-driven NoiseTrader: random uninformed trader. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = (
        "examples.FramingEffect.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS"
    )


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMGainFrameFollower",
    "RuleLLMLossFrameReactor",
    "RuleLLMFrameInvariantTrader",
    "RuleLLMArbitrageFramer",
    "RuleLLMNoiseTrader",
]
