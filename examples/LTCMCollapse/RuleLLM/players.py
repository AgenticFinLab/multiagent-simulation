"""LTCMCollapse RuleLLM Variant Players

RuleLLM agents use LangChainAPIInference (lmbase) for LLM calls.
"""

import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

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
from examples.LTCMCollapse.Rule.players import _build_order, _require_positive
from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking

logger = logging.getLogger("LTCMCollapse.RuleLLM")


def _expected_rule_actions(player: GeneralPlayer, price: float, deviation: float) -> tuple[str, ...]:
    """Return categorical directions allowed by the encoded Rule prompt."""
    extras = player.config.extras
    cash = player.state.custom_state["cash"]
    position = player.state.custom_state["position"]
    role = player.__class__.__name__
    if role == "RuleLLMConvergenceArbitrageur":
        if deviation < -extras["entry_spread"] and position < extras["max_position"] and cash >= price:
            return ("buy",)
        if deviation > extras["entry_spread"] and position > 0:
            return ("sell",)
        return ("hold",)
    if role == "RuleLLMLeverageTrader":
        initial_equity = abs(position * extras["initial_price"]) * (
            1 / extras["leverage_ratio"] + extras["margin_call_threshold"]
        )
        equity = initial_equity + position * (price - extras["initial_price"])
        if equity < abs(position * price) * extras["margin_call_threshold"]:
            if int(abs(position) * extras["delever_fraction"]) <= 0:
                return ("hold",)
            return ("sell",) if position > 0 else ("buy",) if position < 0 else ("hold",)
        if deviation < -extras["margin_call_threshold"] and cash >= price:
            return ("buy",)
        return ("hold",)
    if role == "RuleLLMRiskManager":
        threshold = max(
            extras["var_trigger"], extras["var_multiplier"] * extras["var_limit"]
        )
        if abs(deviation) > threshold:
            return ("sell",) if position > 0 else ("buy",) if position < 0 else ("hold",)
        return ("hold",)
    if role == "RuleLLMLiquidityProvider":
        if abs(deviation) >= extras["stress_exit"] or abs(position) >= extras["inventory_limit"]:
            return ("hold",)
        return ("sell",) if deviation > 0 else ("buy",)
    if role == "RuleLLMCentralBank":
        return ("buy", "hold")
    raise ValueError(f"Unknown RuleLLM role: {role}")


def _validate_decision(decision: dict, identity: str) -> dict:
    """Validate the shared LTCM RuleLLM decision contract."""
    action = decision["action"]
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    _require_positive(bid_price, "bid_price")
    quantity = int(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] quantity must be non-negative, got {quantity}")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": decision["reasoning"],
        "analysis": decision["analysis"],
    }


class RuleLLMInvestor(GeneralPlayer):
    """Base class for RuleLLM LTCMCollapse investors.

    Theory: simulation-bases.md §4.
    Strategy specification: RuleLLM prompts map to simulation-bases.md §4.
    """

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
        _require_positive(price, "price")
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        initial_price = self.config.extras["initial_price"]
        initial_position = self.config.extras["initial_position"]
        user_msg = (
            f"Current Market State (Round {round_num}):\n"
            f"- Current Price: ${price:.2f}\n"
            f"- Fundamental Value: ${fundamental:.2f}\n"
            f"- Price Deviation: {deviation * 100:+.2f}%\n"
            f"- Your Cash: ${cash:.2f}\n"
            f"- Your Position: {position} shares\n"
            f"- Initial Price: ${initial_price:.2f}\n"
            f"- Initial Position: {initial_position} shares\n"
            f"- Portfolio Value: ${portfolio_value:.2f}\n\n"
            "Apply your decision rules exactly.\n\n"
            "Required output:\n"
            "<analysis>brief calculation and rationale</analysis>\n"
            f"<decision>{{\"action\": \"buy\"|\"sell\"|\"hold\", \"bid_price\": {price:.2f}, "
            "\"quantity\": non-negative integer, \"reasoning\": \"brief rationale\"}}</decision>"
        )
        infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                response = llm.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                decision = _validate_decision(decision, self.identity)
                expected_actions = _expected_rule_actions(self, price, deviation)
                if decision["action"] not in expected_actions:
                    raise ValueError(
                        f"[{self.identity}] rule direction mismatch: "
                        f"expected one of {expected_actions}, got {decision['action']}"
                    )
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < 2 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
            )

        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        bid_price = float(decision_payload["bid_price"])
        price = self.state.custom_state["price"]
        _require_positive(price, "price")
        _require_positive(bid_price, "bid_price")
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            quantity = min(quantity, int(cash / price))
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
        order = _build_order(
            self,
            action,
            quantity,
            bid_price,
            str(decision_payload["reasoning"]),
        )
        order["analysis"] = str(decision_payload["analysis"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RuleLLMConvergenceArbitrageur(RuleLLMInvestor):
    """RuleLLM leveraged spread convergence trader.

    Theory: simulation-bases.md §4.1 — ConvergenceArbitrageur.
    """

    _system_prompt = RULELLM_CONVERGENCEARBITRAGEUR_PROMPT


class RuleLLMLeverageTrader(RuleLLMInvestor):
    """RuleLLM margin-pressure deleveraging trader.

    Theory: simulation-bases.md §4.2 — LeverageTrader.
    """

    _system_prompt = RULELLM_LEVERAGETRADER_PROMPT


class RuleLLMRiskManager(RuleLLMInvestor):
    """RuleLLM VaR-based position cutter.

    Theory: simulation-bases.md §4.3 — RiskManager.
    """

    _system_prompt = RULELLM_RISKMANAGER_PROMPT


class RuleLLMLiquidityProvider(RuleLLMInvestor):
    """RuleLLM stress-sensitive liquidity provider.

    Theory: simulation-bases.md §4.4 — LiquidityProvider.
    """

    _system_prompt = RULELLM_LIQUIDITYPROVIDER_PROMPT


class RuleLLMCentralBank(RuleLLMInvestor):
    """RuleLLM lender-of-last-resort intervention agent.

    Theory: simulation-bases.md §4.5 — CentralBank.
    """

    _system_prompt = RULELLM_CENTRALBANK_PROMPT


__all__ = [
    "Market",
    "RuleLLMConvergenceArbitrageur",
    "RuleLLMLeverageTrader",
    "RuleLLMRiskManager",
    "RuleLLMLiquidityProvider",
    "RuleLLMCentralBank",
]
