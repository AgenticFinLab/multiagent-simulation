"""ArchegosCollapse RuleLLM Simulation

Archegos collapse simulation with LLM-driven investors using rule-embedded prompts.

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import importlib
import logging
import os
import sys
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from examples.ArchegosCollapse.Rule.players import Market

logger = logging.getLogger("ArchegosCollapse.RuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RuleLLMInvestor(GeneralPlayer):
    """Base class for RuleLLM-powered investors in the ArchegosCollapse scenario."""

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
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            load_dotenv()
            llm_cfg = extras["llm"]
            lm_name = llm_cfg["lm_name"]
            generation_config = llm_cfg["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config
            self.state.custom_state["llm_client"] = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("llm_client", None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        strategy_name = self.__class__.__name__

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])

        user_prompt = user_template.format(
            round=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            fundamental=market_data["fundamental"],
            deviation=market_data["deviation"],
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed, retrying: %s",
                        self.identity,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d retries: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            decision = {
                "action": "hold",
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "reasoning": f"LLM fallback hold after retries: {last_error}",
                "analysis": "",
            }

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        if bid_price <= 0:
            bid_price = market_data["price"]

        if action == "buy":
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = max(-position, quantity)
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] += quantity

        logger.info(
            "[%s] R%d (%s): Q=%+.2f", self.identity, round_num, strategy_name, quantity
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "action": action,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
        }

        validate_order(order)
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class RuleLLMConcentratedFund(RuleLLMInvestor):
    """RuleLLM concentrated fund — TRS-leveraged, margin call driven. Theory: simulation-bases.md §4.1."""

    pass


class RuleLLMPrimeBroker1(RuleLLMInvestor):
    """RuleLLM prime broker 1 — first-mover liquidator. Theory: simulation-bases.md §4.2."""

    pass


class RuleLLMPrimeBroker2(RuleLLMInvestor):
    """RuleLLM prime broker 2 — delayed liquidator at worse prices. Theory: simulation-bases.md §4.3."""

    pass


class RuleLLMBlockTradeBuyer(RuleLLMInvestor):
    """RuleLLM block trade buyer — opportunistic discount buyer. Theory: simulation-bases.md §4.4."""

    pass


class RuleLLMInformationTrader(RuleLLMInvestor):
    """RuleLLM information trader — front-runs liquidation cascade. Theory: simulation-bases.md §4.5."""

    pass


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMConcentratedFund",
    "RuleLLMPrimeBroker1",
    "RuleLLMPrimeBroker2",
    "RuleLLMBlockTradeBuyer",
    "RuleLLMInformationTrader",
]
