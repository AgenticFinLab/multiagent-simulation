"""LTCMCollapse LLM Variant Players

LLM-driven agents for the LTCMCollapse simulation using LangChainAPIInference.
"""

import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.LTCMCollapse.LLM.prompts import (
    LLM_CONVERGENCEARBITRAGEUR_PROMPT,
    LLM_LEVERAGETRADER_PROMPT,
    LLM_RISKMANAGER_PROMPT,
    LLM_LIQUIDITYPROVIDER_PROMPT,
    LLM_CENTRALBANK_PROMPT,
)
from examples.LTCMCollapse.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("LTCMCollapse.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven LTCMCollapse investors."""

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
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        llm_cfg = self.config.extras["llm"]
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
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
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                response = llm.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
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

        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
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


class LLMConvergenceArbitrageur(LLMInvestor):
    """LLM-driven leveraged spread convergence trader. Theory: simulation-bases.md §4.1."""

    _system_prompt = LLM_CONVERGENCEARBITRAGEUR_PROMPT


class LLMLeverageTrader(LLMInvestor):
    """LLM-driven margin-pressure deleveraging trader. Theory: simulation-bases.md §4.2."""

    _system_prompt = LLM_LEVERAGETRADER_PROMPT


class LLMRiskManager(LLMInvestor):
    """LLM-driven VaR-based position cutter. Theory: simulation-bases.md §4.3."""

    _system_prompt = LLM_RISKMANAGER_PROMPT


class LLMLiquidityProvider(LLMInvestor):
    """LLM-driven stress-sensitive liquidity provider. Theory: simulation-bases.md §4.4."""

    _system_prompt = LLM_LIQUIDITYPROVIDER_PROMPT


class LLMCentralBank(LLMInvestor):
    """LLM-driven lender-of-last-resort intervention agent. Theory: simulation-bases.md §4.5."""

    _system_prompt = LLM_CENTRALBANK_PROMPT


__all__ = [
    "Market",
    "LLMConvergenceArbitrageur",
    "LLMLeverageTrader",
    "LLMRiskManager",
    "LLMLiquidityProvider",
    "LLMCentralBank",
]
