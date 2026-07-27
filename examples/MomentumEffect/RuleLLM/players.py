"""MomentumEffect RuleLLM Players - Hybrid Rule+LLM momentum simulation.

Design:
    - Market coordinator: identical rule-based price dynamics as MomentumEffect.
    - Investors: LLM-powered with system prompts embedding explicit quantitative
      rules (formulas, thresholds) from the rule-based counterpart, alongside
      rich persona descriptions.

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from .prompts import (
    RULELLM_CONTRARIAN_TRADER_SYS,
    RULELLM_FUNDAMENTAL_ANCHOR_SYS,
    RULELLM_MOMENTUM_TRADER_SYS,
    RULELLM_TECHNICAL_TRADER_SYS,
    RULELLM_TREND_FOLLOWER_SYS,
    RULELLM_USER_TEMPLATE,
)
from masim.utils.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("MomentumEffectRuleLLM")


# =============================================================================
# Market - Rule-Based Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """Central market with liquidity-sensitive pricing.

    Price model:
        P(t+1) = P(t) + price_impact * liquidity_factor * NetDemand
                 + mean_reversion * (F - P(t)) + epsilon
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=custom_state_hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                        "provides_liquidity": order["provides_liquidity"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        base_liquidity = extras["base_liquidity"]
        low_liquidity_threshold = extras["low_liquidity_threshold"]
        high_impact_multiplier = extras["high_impact_multiplier"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        liquidity_provision = sum(
            abs(o["quantity"]) for o in orders if o["provides_liquidity"]
        )
        total_liquidity = base_liquidity + liquidity_provision

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        if total_liquidity < low_liquidity_threshold:
            liquidity_factor = high_impact_multiplier
        else:
            liquidity_factor = (
                1.0 + (low_liquidity_threshold / total_liquidity - 1.0) * 0.5
            )

        price_impact = base_price_impact * net_demand * liquidity_factor
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        logger.debug(
            "[Market] R%d  P=%.2f→%.2f (%+.2f%%)  Liq=%.1f  IF=%.2f  ND=%+.2f",
            round_num,
            current_price,
            new_price,
            price_return * 100,
            total_liquidity,
            liquidity_factor,
            net_demand,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "liquidity": total_liquidity,
            "round": round_num,
            "fundamental": fundamental_value,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# RuleLLMInvestor - Base
# =============================================================================


class RuleLLMInvestor(GeneralPlayer):
    """Base class for hybrid Rule+LLM momentum effect investors."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )
        return self._llm

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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        round_num = self.state.custom_state["round"]
        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )
        return RULELLM_USER_TEMPLATE.format(
            round=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            liquidity=market_data["liquidity"],
            fundamental=market_data["fundamental"],
            volume=market_data["volume"],
            net_demand=market_data["net_demand"],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        strategy_name = self.__class__.__name__
        llm = self._get_llm()

        user_prompt = self._build_prompt(market_data)

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(
                system_msg=self._system_prompt, user_msg=user_prompt
            )
            infer_output = llm.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "action": "hold",
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "strategy": strategy_name,
                "investor": self.identity,
                "reasoning": "LLM parse failed: held position",
                "provides_liquidity": False,
                "_skipped": True,
                "_skipped_reason": f"llm_failed_after_{max_retries}_attempts: {last_error}",
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_bid"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(-position, quantity)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        logger.debug(
            "[%-25s] R%d (%-25s): P=%7.2f  Q=%+7.2f | Cash=%8.2f  Pos=%+7.2f",
            self.identity,
            round_num,
            strategy_name,
            bid_price,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "reasoning": decision["reasoning"][:120],
            "provides_liquidity": decision["provides_liquidity"],
        }

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


# =============================================================================
# Concrete Hybrid Investor Types
# =============================================================================


class RuleLLMMomentumTrader(RuleLLMInvestor):
    """Hybrid MomentumTrader. Theory: simulation-bases.md §4.1."""

    _system_prompt = RULELLM_MOMENTUM_TRADER_SYS


class RuleLLMContrarianTrader(RuleLLMInvestor):
    """Hybrid ContrarianTrader. Theory: simulation-bases.md §4.2."""

    _system_prompt = RULELLM_CONTRARIAN_TRADER_SYS


class RuleLLMTechnicalTrader(RuleLLMInvestor):
    """Hybrid TechnicalTrader. Theory: simulation-bases.md §4.5."""

    _system_prompt = RULELLM_TECHNICAL_TRADER_SYS


class RuleLLMTrendFollower(RuleLLMInvestor):
    """Hybrid TrendFollower. Theory: simulation-bases.md §4.7."""

    _system_prompt = RULELLM_TREND_FOLLOWER_SYS


class RuleLLMFundamentalAnchor(RuleLLMInvestor):
    """Hybrid FundamentalAnchor. Theory: simulation-bases.md §4.6."""

    _system_prompt = RULELLM_FUNDAMENTAL_ANCHOR_SYS


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMMomentumTrader",
    "RuleLLMContrarianTrader",
    "RuleLLMTechnicalTrader",
    "RuleLLMTrendFollower",
    "RuleLLMFundamentalAnchor",
]
