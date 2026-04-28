"""HerdingInformation LLM Simulation

Information cascade occurs when individuals ignore private signals and follow the crowd.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: LLM-driven with personas from prompts.py
"""

import importlib
import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.HerdingInformation.Rule.players import Market  # noqa: F401
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("HerdingInformation.LLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for HerdingInformation."""

    _system_prompt_path: str = ""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras.get("initial_position", 0)
        llm_cfg = extras.get("llm", {})
        self._llm_params = {
            "lm_name": llm_cfg["lm_name"],
            "generation_config": llm_cfg["generation_config"],
        }
        self._llm_client = LangChainAPIInference(
            lm_name=self._llm_params["lm_name"],
            generation_config=self._llm_params["generation_config"],
        )

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm_client", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        params = self.__dict__.get("_llm_params", {})
        if params:
            self._llm_client = LangChainAPIInference(
                lm_name=params["lm_name"],
                generation_config=params["generation_config"],
            )

    async def decide(self):
        from examples.HerdingInformation.LLM.prompts import LLM_USER_TEMPLATE

        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        system_msg = load_prompt(self._system_prompt_path)
        user_msg = LLM_USER_TEMPLATE.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )
        infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
        response = self._llm_client.run([infer_input]).outputs[0].response
        raw = parse_llm_response_with_thinking(response)

        action = raw.get("action", "hold")
        quantity = int(raw.get("quantity", 0))
        quantity = max(0, min(quantity, 5000))

        if action == "buy" and price > 0:
            quantity = min(quantity, int(cash / price))
        elif action == "sell":
            quantity = min(quantity, max(position, 0))

        return {"action": action, "quantity": quantity}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LLMCascadeFollower(LLMInvestor):
    """LLM-driven information cascade follower. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.HerdingInformation.LLM.prompts:LLM_CASCADE_FOLLOWER_SYS"
    )


class LLMReputationHerder(LLMInvestor):
    """LLM-driven reputation-based herder. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.HerdingInformation.LLM.prompts:LLM_REPUTATION_HERDER_SYS"
    )


class LLMIndependentThinker(LLMInvestor):
    """LLM-driven rational independent thinker. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.HerdingInformation.LLM.prompts:LLM_INDEPENDENT_THINKER_SYS"
    )


class LLMContrarian(LLMInvestor):
    """LLM-driven contrarian investor. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.HerdingInformation.LLM.prompts:LLM_CONTRARIAN_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven uninformed noise trader. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.HerdingInformation.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMCascadeFollower",
    "LLMReputationHerder",
    "LLMIndependentThinker",
    "LLMContrarian",
    "LLMNoiseTrader",
]
