"""LTCMCollapse RuleLLM Variant Players

RuleLLM agents use LangChainAPIInference (lmbase) for LLM calls.
"""

import logging

from lmbase.inference import LangChainAPIInference, InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.LTCMCollapse.RuleLLM.prompts import (
    RULELLM_CONVERGENCEARBITRAGEUR_PROMPT,
    RULELLM_LEVERAGETRADER_PROMPT,
    RULELLM_RISKMANAGER_PROMPT,
    RULELLM_LIQUIDITYPROVIDER_PROMPT,
    RULELLM_CENTRALBANK_PROMPT,
)
from examples.LTCMCollapse.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("LTCMCollapse.RuleLLM")


class RuleLLMInvestor(GeneralPlayer):
    """Base class for RuleLLM LTCMCollapse investors."""

    _system_prompt = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        llm_cfg = self.config.extras.get("llm", {})
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg.get("generation_config", {}),
        )
        price = self.state.custom_state.get("price", 0)
        fundamental = self.state.custom_state.get("fundamental", 0)
        deviation = self.state.custom_state.get("deviation", 0)
        cash = self.state.custom_state.get("cash", 0)
        position = self.state.custom_state.get("position", 0)
        round_num = self.state.custom_state.get("round", 0)
        portfolio_value = cash + position * price
        user_msg = (
            f"Current Market State (Round {round_num}):\n"
            f"- Current Price: ${price:.2f}\n"
            f"- Fundamental Value: ${fundamental:.2f}\n"
            f"- Price Deviation: {deviation * 100:+.2f}%\n"
            f"- Your Cash: ${cash:.2f}\n"
            f"- Your Position: {position} shares\n"
            f"- Portfolio Value: ${portfolio_value:.2f}\n\n"
            "Based on your trading strategy and current market conditions, what action do you take?\n"
            "Provide your analysis and decision in the specified format."
        )
        infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
        try:
            response = llm.run([infer_input]).outputs[0].response
            result = parse_llm_response_with_thinking(response)
            decision = result.get("decision", {})
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = int(decision_payload.get("quantity", 0))
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state.get("cash", 0)
        position = self.state.custom_state.get("position", 0)
        if action == "buy" and quantity > 0 and price > 0:
            quantity = min(quantity, int(cash / price))
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RuleLLMConvergenceArbitrageur(RuleLLMInvestor):
    """RuleLLM ConvergenceArbitrageur: leveraged spread convergence trader."""

    _system_prompt = RULELLM_CONVERGENCEARBITRAGEUR_PROMPT


class RuleLLMLeverageTrader(RuleLLMInvestor):
    """RuleLLM LeverageTrader: forced deleveraging under margin pressure."""

    _system_prompt = RULELLM_LEVERAGETRADER_PROMPT


class RuleLLMRiskManager(RuleLLMInvestor):
    """RuleLLM RiskManager: VaR-based position cutting."""

    _system_prompt = RULELLM_RISKMANAGER_PROMPT


class RuleLLMLiquidityProvider(RuleLLMInvestor):
    """RuleLLM LiquidityProvider: market maker withdrawing under stress."""

    _system_prompt = RULELLM_LIQUIDITYPROVIDER_PROMPT


class RuleLLMCentralBank(RuleLLMInvestor):
    """RuleLLM CentralBank: lender of last resort."""

    _system_prompt = RULELLM_CENTRALBANK_PROMPT


__all__ = [
    "Market",
    "RuleLLMConvergenceArbitrageur",
    "RuleLLMLeverageTrader",
    "RuleLLMRiskManager",
    "RuleLLMLiquidityProvider",
    "RuleLLMCentralBank",
]
