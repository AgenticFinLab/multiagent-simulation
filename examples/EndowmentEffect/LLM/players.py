"""Persona-driven investors for the EndowmentEffect LLM variant.

The language model deliberates, while this module enforces the executable
contract: valid decision fields, finite numeric values, configured order-size
limits, and cash/inventory constraints.
"""

from __future__ import annotations

import copy
import importlib
import logging
import math
import os
from typing import Dict

from dotenv import load_dotenv

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking
from masim.player.base import Action, Observation
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from examples.EndowmentEffect.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM investor for EndowmentEffect simulation."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["market_data"] = {}
        base_path = os.path.join(extras["record_path"], self.config.identity)
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=os.path.join(base_path, "llm_history"),
            entry_limit=int(extras["custom_state_hot_limit"]),
        )
        load_dotenv()
        llm_cfg = extras["llm"]
        if llm_cfg["lm_type"] != "api":
            raise ValueError("EndowmentEffect LLM requires llm.lm_type: api")
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            player_state = copy.copy(self.state)
            player_state.custom_state = dict(self.state.custom_state)
            player_state.custom_state.pop("llm_client", None)
            state["state"] = player_state
        return state

    def __setstate__(self, state: Dict) -> None:
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "llm_params" in custom and "llm_client" not in custom:
                llm_cfg = custom["llm_params"]
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=llm_cfg["lm_name"],
                    generation_config=llm_cfg["generation_config"],
                )

    async def decide(self) -> Dict:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        decision = None
        last_error = None
        max_retries = int(llm_cfg["max_retries"])
        for attempt in range(max_retries):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input])
                parsed = parse_llm_response_with_thinking(result.response)
                if parsed["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid action: {parsed['action']}")
                bid_price = float(parsed["bid_price"])
                quantity = float(parsed["quantity"])
                if not math.isfinite(bid_price) or bid_price <= 0:
                    raise ValueError(f"Invalid bid_price: {parsed['bid_price']}")
                if not math.isclose(bid_price, price, rel_tol=1e-6, abs_tol=0.01):
                    raise ValueError("bid_price must equal the current market price")
                if not math.isfinite(quantity) or quantity < 0:
                    raise ValueError(f"Invalid quantity: {parsed['quantity']}")
                if not str(parsed["reasoning"]).strip():
                    raise ValueError("Missing reasoning")
                if not str(parsed["analysis"]).strip():
                    raise ValueError("Missing <analysis> content")
                decision = parsed
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        action_str = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = min(
            int(float(decision["quantity"])),
            int(self.config.extras["base_size"]),
        )
        if action_str == "buy":
            quantity = min(quantity, int(cash / price) if price > 0 else 0)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0
        if quantity == 0:
            action_str = "hold"
        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": decision["reasoning"],
            "analysis": decision["analysis"],
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": decision["reasoning"],
            "analysis": decision["analysis"],
            "strategy": self.__class__.__name__,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class LLMEndowedHolder(LLMInvestor):
    """LLM-driven endowed holder — attachment bias suppresses selling via LLM reasoning. Theory: simulation-bases.md §4.1."""

class LLMStatusQuoSeller(LLMInvestor):
    """LLM-driven status-quo-biased seller — inertia and loss aversion modeled via LLM. Theory: simulation-bases.md §4.2."""

class LLMRationalArbitrageur(LLMInvestor):
    """LLM-driven rational arbitrageur — exploits endowment-bias gap via fundamental analysis. Theory: simulation-bases.md §4.3."""

class LLMNewBuyer(LLMInvestor):
    """LLM-driven unbiased new buyer — evaluates assets at market price, no ownership distortion. Theory: simulation-bases.md §4.4."""

class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random uninformed trades modeled with probabilistic LLM persona. Theory: simulation-bases.md §4.5."""

__all__ = [
    "Market",
    "LLMInvestor",
    "LLMEndowedHolder",
    "LLMStatusQuoSeller",
    "LLMRationalArbitrageur",
    "LLMNewBuyer",
    "LLMNoiseTrader",
]
