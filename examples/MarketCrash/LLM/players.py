"""MarketCrashLLM - LLM-based Multi-Agent Market Simulation

LLM investors with different trading personalities:
    - PanicSeller (Loss-Averse Retail Investor)
    - RiskParityFund (volatility-sensitive institutional)
    - LeveragedHedgeFund (margin-constrained hedge fund)
    - MarketMaker (liquidity provider)
    - BottomFisher (patient value buyer)

Market Parameters (from config.extras):
    - record_path: Path for output records
    - fundamental_value: True value for mean reversion
    - initial_price: Starting price
    - base_price_impact: Base price impact coefficient
    - mean_reversion: Mean reversion strength
    - noise_std: Random noise standard deviation
    - liquidity_decay: Liquidity decay rate during selling
    - liquidity_recovery: Liquidity recovery rate
    - min_liquidity: Minimum liquidity floor
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash balance
    - initial_position: Starting share position
    - custom_state_hot_limit: Maximum history buffer size
    - llm: model, temperature
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.MarketCrash.LLM.prompts import (
    LLM_PANIC_SELLER_SYS,
    LLM_RISK_PARITY_SYS,
    LLM_LEVERAGED_FUND_SYS,
    LLM_MARKET_MAKER_SYS,
    LLM_BOTTOM_FISHER_SYS,
    LLM_PASSIVE_INVESTOR_SYS,
    LLM_USER_TEMPLATE,
)

logger = logging.getLogger("MarketCrashLLM")


class Market(GeneralPlayer):
    """Central market with liquidity-sensitive pricing.

    Price Model:
        P(t+1) = P(t) + (base_impact / liquidity) * NetDemand
                 + mean_reversion * (F - P(t)) + noise

    Parameters from config extras:
        - fundamental_value, initial_price
        - base_price_impact, mean_reversion, noise_std
        - liquidity_decay, liquidity_recovery, min_liquidity
        - custom_state_hot_limit, record_path
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
            self.state.custom_state["liquidity"] = 1.0
            self.state.custom_state["volatility"] = 1.0
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
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
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_liquidity = self.state.custom_state["liquidity"]
        orders = self.state.custom_state["orders"]

        fundamental_value = extras["fundamental_value"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        noise_std = extras["noise_std"]
        liquidity_decay = extras["liquidity_decay"]
        liquidity_recovery = extras["liquidity_recovery"]
        min_liquidity = extras["min_liquidity"]

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Liquidity dynamics
        if net_demand < -5:
            new_liquidity = max(
                min_liquidity, current_liquidity * (1 - liquidity_decay)
            )
        else:
            new_liquidity = min(1.0, current_liquidity + liquidity_recovery)

        # Price impact increases as liquidity drops
        liquidity_multiplier = 1.0 / max(new_liquidity, min_liquidity)
        price_impact = base_price_impact * liquidity_multiplier * net_demand

        mean_reversion = mean_reversion_strength * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        new_volatility = (
            0.9 * self.state.custom_state["volatility"] + 0.1 * abs(price_return) * 100
        )

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = new_liquidity
        self.state.custom_state["volatility"] = new_volatility
        self.state.custom_state["prev_return"] = price_return

        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["liquidity_history"].append(new_liquidity)

        logger.debug(
            "[Market] R%d  P=%.2f→%.2f (%+.2f%%)  Liq=%.2f  Vol=%.2f  ND=%+.2f",
            round_num,
            current_price,
            new_price,
            price_return * 100,
            new_liquidity,
            new_volatility,
            net_demand,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "liquidity": new_liquidity,
            "volatility": new_volatility,
            "volume": total_volume,
            "net_demand": net_demand,
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


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-powered market crash investors.

    Subclasses set _system_prompt to personalise behaviour.
    All parameters read from config.extras.
    """

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

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

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )
        return self._llm

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(-position, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        strategy_name = self.__class__.__name__

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        user_msg = LLM_USER_TEMPLATE.format(
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            liquidity=market_data["liquidity"],
            volatility=market_data["volatility"],
            volume=market_data["volume"],
            net_demand=market_data["net_demand"],
            fundamental=market_data["fundamental"],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

        llm = self._get_llm()
        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
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
                "[%s] LLM failed after %d attempts: %s. Holding this round.",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_market_maker": self.__class__.__name__.endswith("MarketMaker"),
                "reasoning": "LLM parse failed: held position",
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_bid"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]
        quantity = self._apply_constraints(bid_price, quantity)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        logger.debug(
            "[%-20s] R%d (%-20s): Q=%+7.2f | Cash=%8.2f  Pos=%+7.2f",
            self.identity,
            round_num,
            strategy_name,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": self.__class__.__name__.endswith("MarketMaker"),
            "reasoning": decision["reasoning"][:100],
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


class LLMPanicSeller(LLMInvestor):
    """LLM PanicSeller. Theory: simulation-bases.md §4.5."""

    _system_prompt = LLM_PANIC_SELLER_SYS


class LLMRiskParityFund(LLMInvestor):
    """LLM RiskParityFund. Theory: simulation-bases.md §4.1."""

    _system_prompt = LLM_RISK_PARITY_SYS


class LLMLeveragedHedgeFund(LLMInvestor):
    """LLM LeveragedHedgeFund. Theory: simulation-bases.md §4.2."""

    _system_prompt = LLM_LEVERAGED_FUND_SYS


class LLMMarketMaker(LLMInvestor):
    """LLM MarketMaker. Theory: simulation-bases.md §4.3."""

    _system_prompt = LLM_MARKET_MAKER_SYS


class LLMBottomFisher(LLMInvestor):
    """LLM BottomFisher. Theory: simulation-bases.md §4.6."""

    _system_prompt = LLM_BOTTOM_FISHER_SYS


class LLMPassiveInvestor(LLMInvestor):
    """LLM PassiveInvestor. Theory: simulation-bases.md §4.4."""

    _system_prompt = LLM_PASSIVE_INVESTOR_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMPanicSeller",
    "LLMRiskParityFund",
    "LLMLeveragedHedgeFund",
    "LLMMarketMaker",
    "LLMBottomFisher",
    "LLMPassiveInvestor",
]
