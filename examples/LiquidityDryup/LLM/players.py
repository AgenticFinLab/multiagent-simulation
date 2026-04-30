"""LiquidityDryupLLM - LLM-based Multi-Agent Market Simulation

LLM Investor Types:
    - Market Maker: Provides liquidity for spread
    - Liquidity Demander: Takes liquidity
    - Arbitrageur: Seeks opportunities
    - Value Investor: Patient buyer
    - Forced Seller: Must sell

Market Parameters (from config.extras):
    - record_path: Path for output records
    - fundamental_value: True value for mean reversion
    - initial_price: Starting price
    - price_impact: Base price impact coefficient
    - mean_reversion: Mean reversion strength
    - noise_std: Random noise standard deviation
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash balance
    - initial_position: Starting share position
    - custom_state_hot_limit: Maximum history buffer size
    - llm: LLM configuration (model, temperature)
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

from examples.llm_utils import parse_llm_response_with_thinking
from examples.LiquidityDryup.LLM.prompts import (
    LLM_MARKET_MAKER_SYS,
    LLM_LIQUIDITY_DEMANDER_SYS,
    LLM_ARBITRAGEUR_SYS,
    LLM_VALUE_SYS,
    LLM_FORCED_SELLER_SYS,
    LLM_USER_TEMPLATE,
)

logger = logging.getLogger("LiquidityDryupLLM")


class Market(GeneralPlayer):
    """Market with liquidity-dependent pricing.

    All parameters read from config.extras (no class constants).
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["total_liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
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
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Get parameters from config
        fundamental_value = extras["fundamental_value"]
        price_impact_coef = extras["price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        liquidity_provided = sum(o["provides_liquidity"] for o in orders)
        total_liquidity = 50.0 + liquidity_provided

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell

        # Illiquidity amplifies price impact
        liquidity_factor = 100.0 / max(total_liquidity, 10.0)
        price_impact = price_impact_coef * net_demand * liquidity_factor
        mean_reversion = mean_reversion_strength * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["total_liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)

        status = (
            "LOW"
            if total_liquidity < 30
            else "Stressed" if total_liquidity < 60 else "Normal"
        )
        logger.debug("\n%s", "=" * 60)
        logger.debug(
            "[Market] Round %d: $%.2f → $%.2f (%+.2f%%)",
            round_num,
            current_price,
            new_price,
            price_return * 100,
        )
        logger.debug(
            "  Liquidity: %.1f, Impact Factor: %.2fx [%s]",
            total_liquidity,
            liquidity_factor,
            status,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "liquidity": total_liquidity,
            "liquidity_factor": liquidity_factor,
            "fundamental": fundamental_value,
            "round": round_num,
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
    """Base class for LLM-powered investors.

    All parameters read from config.extras (no class constants).
    Subclasses set _system_prompt to their agent-specific system message.
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
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_cfg = self.config.extras["llm"]
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )

        user_msg = LLM_USER_TEMPLATE.format(
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            liquidity=market_data["liquidity"],
            liquidity_factor=market_data["liquidity_factor"],
            fundamental=market_data["fundamental"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            portfolio_value=self.state.custom_state["cash"]
            + self.state.custom_state["position"] * market_data["price"],
        )

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                output = llm.run(
                    [InferInput(system_msg=self._system_prompt, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
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

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        provides_liquidity = float(decision["provides_liquidity"])

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            quantity = min(quantity, cash / bid_price if bid_price > 0 else 0)
        else:
            quantity = max(quantity, -position)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        strategy_name = self.__class__.__name__
        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": provides_liquidity,
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


class LLMMarketMaker(LLMInvestor):
    """Market maker - provides liquidity. Theory: simulation-bases.md §4.1"""

    _system_prompt = LLM_MARKET_MAKER_SYS


class LLMLiquidityDemander(LLMInvestor):
    """Liquidity demander - takes liquidity. Theory: simulation-bases.md §4.2"""

    _system_prompt = LLM_LIQUIDITY_DEMANDER_SYS


class LLMArbitrageur(LLMInvestor):
    """Arbitrageur - seeks opportunities. Theory: simulation-bases.md §4.3"""

    _system_prompt = LLM_ARBITRAGEUR_SYS


class LLMValueInvestor(LLMInvestor):
    """Value investor - patient buyer. Theory: simulation-bases.md §4.4"""

    _system_prompt = LLM_VALUE_SYS


class LLMForcedSeller(LLMInvestor):
    """Forced seller - must sell. Theory: simulation-bases.md §4.5"""

    _system_prompt = LLM_FORCED_SELLER_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMMarketMaker",
    "LLMLiquidityDemander",
    "LLMArbitrageur",
    "LLMValueInvestor",
    "LLMForcedSeller",
]
