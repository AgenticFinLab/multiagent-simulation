"""GameStopShortSqueeze LLM Simulation

January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: LLM-driven with personas from prompts.py
"""

import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.GameStopShortSqueeze.Rule.players import Market, _build_order  # noqa: F401
from masim.utils.llm_utils import (
    parse_llm_response_with_thinking,
    robust_llm_call,
)
from masim.format import get_order_format
from examples.GameStopShortSqueeze.LLM.prompts import LLM_USER_TEMPLATE

logger = logging.getLogger("GameStopShortSqueeze.LLM")
PARAMETER_KEYS = (
    "buy_pressure",
    "cover_threshold",
    "gamma_exposure",
    "sell_threshold",
    "fomo_threshold",
)


# Re-export the canonical prompt loader from masim.agents._base — this
# gives shipped scenarios the same import_module -> file-based fallback
# that Customized bundles depend on (hyphenated bundle dir names are
# illegal in Python import syntax and require file loading).
from masim.agents._base import load_prompt  # noqa: F401


def _format_decision_params(params):
    """Format configured decision parameters for the LLM user prompt."""
    if not params:
        return "None for this agent."
    return "\n".join(f"- {key}: {value}" for key, value in sorted(params.items()))


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for GameStopShortSqueeze."""

    _system_prompt_path: str = ""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["decision_params"] = {
            key: extras[key] for key in PARAMETER_KEYS if key in extras
        }
        llm_cfg = extras["llm"]
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
        params = self.__dict__["_llm_params"]
        if params:
            self._llm_client = LangChainAPIInference(
                lm_name=params["lm_name"],
                generation_config=params["generation_config"],
            )

    async def decide(self):

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
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
            decision_params=_format_decision_params(
                self.state.custom_state["decision_params"]
            ),
        )

        decision = robust_llm_call(
            self._llm_client,
            system_msg,
            user_msg,
            parse_fn=parse_llm_response_with_thinking,
            validate_fn=get_order_format("GameStopShortSqueeze").validate_decision,
            max_retries=5,
            fallback="hold",
            identity=self.identity,
        )

        if decision.get("_fallback"):
            logger.warning(
                "[%s] R%d LLM unavailable; emitting noop hold.",
                self.identity,
                round_num,
            )
            return _build_order(self, "hold", 0, float(price), "llm_fallback_noop")

        action = decision["action"]
        quantity = int(decision["quantity"])
        quantity = max(0, min(quantity, 5000))

        if action == "buy" and price > 0:
            quantity = min(quantity, int(cash / price))
        elif action == "sell":
            quantity = min(quantity, max(position, 0))

        return _build_order(
            self,
            action,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )

    async def act(self, decision_payload):
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
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


class LLMRetailCoordinated(LLMInvestor):
    """LLM-driven retail coordinated buyer. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.GameStopShortSqueeze.LLM.prompts:LLM_RETAIL_COORDINATED_SYS"
    )


class LLMShortSellerHF(LLMInvestor):
    """LLM-driven short seller hedge fund. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.GameStopShortSqueeze.LLM.prompts:LLM_SHORT_SELLER_HF_SYS"
    )


class LLMMarketMakerGamma(LLMInvestor):
    """LLM-driven gamma-hedging market maker. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.GameStopShortSqueeze.LLM.prompts:LLM_MARKET_MAKER_GAMMA_SYS"
    )


class LLMInstitutionalValue(LLMInvestor):
    """LLM-driven institutional value investor. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.GameStopShortSqueeze.LLM.prompts:LLM_INSTITUTIONAL_VALUE_SYS"
    )


class LLMMomentumRetail(LLMInvestor):
    """LLM-driven FOMO momentum retail trader. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = (
        "examples.GameStopShortSqueeze.LLM.prompts:LLM_MOMENTUM_RETAIL_SYS"
    )


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMRetailCoordinated",
    "LLMShortSellerHF",
    "LLMMarketMakerGamma",
    "LLMInstitutionalValue",
    "LLMMomentumRetail",
]
