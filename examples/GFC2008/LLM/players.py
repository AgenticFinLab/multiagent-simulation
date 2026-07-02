"""GFC2008 LLM Variant Players

LLM-driven agents for the GFC2008 simulation using LangChainAPIInference.
"""

import importlib
import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.GFC2008.Rule.players import Market, _build_order
from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.GFC2008.LLM.prompts import LLM_USER_TEMPLATE

logger = logging.getLogger("GFC2008.LLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven GFC2008 investors."""

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
        """Call LLM with market state; parse decision."""

        system_msg = load_prompt(self._system_prompt_path)
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        portfolio_value = cash + position * price

        user_msg = LLM_USER_TEMPLATE.format(
            round=self.state.custom_state["round"],
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
                response = self._llm_client.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid action: {decision['action']}")
                if float(decision["bid_price"]) <= 0:
                    raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
                if not str(decision["reasoning"]).strip():
                    raise ValueError("Missing reasoning")
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
            )

        action = decision["action"]
        quantity = int(decision["quantity"])
        price_val = self.state.custom_state["price"]

        if action == "buy":
            max_qty = int(cash / price_val) if price_val > 0 else 0
            quantity = min(quantity, max_qty, 3000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 3000)
        else:
            quantity = 0

        quantity = max(0, quantity)
        return _build_order(
            self,
            action,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )

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

        order = _build_order(
            self,
            action,
            quantity,
            float(decision_payload["bid_price"]),
            str(decision_payload["reasoning"]),
        )
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LLMMBSOriginator(LLMInvestor):
    """LLM-driven MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.GFC2008.LLM.prompts:LLM_MBS_ORIGINATOR_SYS"


class LLMRatingAgency(LLMInvestor):
    """LLM-driven RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = "examples.GFC2008.LLM.prompts:LLM_RATING_AGENCY_SYS"


class LLMLeveragedInvestor(LLMInvestor):
    """LLM-driven LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.GFC2008.LLM.prompts:LLM_LEVERAGED_INVESTOR_SYS"


class LLMDistressedBuyer(LLMInvestor):
    """LLM-driven DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.GFC2008.LLM.prompts:LLM_DISTRESSED_BUYER_SYS"


class LLMRegulator(LLMInvestor):
    """LLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.GFC2008.LLM.prompts:LLM_REGULATOR_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMMBSOriginator",
    "LLMRatingAgency",
    "LLMLeveragedInvestor",
    "LLMDistressedBuyer",
    "LLMRegulator",
]
