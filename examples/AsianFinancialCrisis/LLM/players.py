"""AsianFinancialCrisis LLM Simulation

1997 Asian financial crisis with LLM-driven investors using behavioral personas.
Market dynamics are rule-based; investor decisions are LLM-generated.

Theoretical Foundation:
    - Radelet & Sachs (1998): The East Asian financial crisis
    - Kaminsky & Reinhart (1999): The twin crises
    - Corsetti, Pesenti & Roubini (1999): Paper tigers?

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import importlib
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order


from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from examples.AsianFinancialCrisis.Rule.players import Market

logger = logging.getLogger("AsianFinancialCrisis.LLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the shared AsianFinancialCrisis LLM decision contract."""
    action = decision["action"]
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    if bid_price <= 0:
        raise ValueError(f"[{identity}] bid_price must be positive, got {bid_price}")
    quantity = float(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] quantity must be non-negative, got {quantity}")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": str(decision["reasoning"]),
        "analysis": str(decision["analysis"]),
    }


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-powered investors in the AsianFinancialCrisis scenario.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path, llm config
    """

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
                folder=os.path.join(base_path, "price"),
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
            round_num=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            deviation=market_data["deviation"],
            fundamental=market_data["fundamental"],
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
                decision = _validate_decision(decision, self.identity)
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
            raise RuntimeError(
                f"[{self.identity}] LLM decision contract failed after "
                f"{max_retries} retries: {last_error}"
            )

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        if action == "buy":
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0.0

        logger.info(
            "[%s] R%d (%s): Q=%+.2f", self.identity, round_num, strategy_name, quantity
        )

        order = {
            "action": action,
            "bid_price": bid_price,
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


class LLMHotMoneyFunder(LLMInvestor):
    """LLM-driven hot money funder — rapidly reverses at first crisis signal. Theory: simulation-bases.md §4.1."""

    pass


class LLMContagionTrader(LLMInvestor):
    """LLM-driven contagion trader — spreads selling across borders. Theory: simulation-bases.md §4.2."""

    pass


class LLMIMFRescuer(LLMInvestor):
    """LLM-driven IMF rescuer — stabilizing emergency liquidity provider. Theory: simulation-bases.md §4.3."""

    pass


class LLMValueContrarian(LLMInvestor):
    """LLM-driven value contrarian — buys oversold crisis assets. Theory: simulation-bases.md §4.4."""

    pass


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — uninformed random participant. Theory: simulation-bases.md §4.5."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMHotMoneyFunder",
    "LLMContagionTrader",
    "LLMIMFRescuer",
    "LLMValueContrarian",
    "LLMNoiseTrader",
]
