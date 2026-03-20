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
    - llm: LLM configuration (sys_message, user_message, lm_name, generation_config)
"""

import logging
import os
import json
import random
import re
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

logger = logging.getLogger("LiquidityDryupLLM")


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


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
        logger.debug(f"\n{'='*60}")
        logger.debug(
            f"[Market] Round {round_num}: ${current_price:.2f} → ${new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Liquidity: {total_liquidity:.1f}, Impact Factor: {liquidity_factor:.2f}x [{status}]"
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
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            load_dotenv()
            llm_config = extras["llm"]
            self.state.custom_state["lm_name"] = llm_config["lm_name"]
            self.state.custom_state["generation_config"] = llm_config[
                "generation_config"
            ]
            self.state.custom_state["llm_client"] = LangChainAPIInference(
                lm_name=llm_config["lm_name"],
                generation_config=llm_config["generation_config"],
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = state["state"].custom_state
            if "llm_client" in custom:
                custom = dict(custom)
                del custom["llm_client"]
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

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        llm_config = self.config.extras["llm"]
        template = load_prompt(llm_config["user_message"])
        return template.format(
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

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response and validate required fields are present and non-null."""
        parsed = None
        try:
            parsed = json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
        if parsed is None:
            raise ValueError(f"Parse failed: {text[:100]}")

        # Validate required fields with fallback to trigger retry
        required_fields = ["bid_price", "quantity", "reasoning"]
        missing_or_null = []
        for field in required_fields:
            if field not in parsed or parsed[field] is None:
                missing_or_null.append(field)
        if missing_or_null:
            raise ValueError(f"Fields missing or null: {missing_or_null}")

        return parsed

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        for _ in range(3):
            try:
                output = llm_client.run(
                    [
                        InferInput(
                            system_msg=system_prompt,
                            user_msg=self._build_prompt(market_data),
                        )
                    ]
                )
                decision = self._parse_response(output.response)
                break
            except:
                decision = {
                    "action": "hold",
                    "bid_price": market_data["price"],
                    "quantity": 0,
                    "provides_liquidity": 0,
                    "reasoning": "error",
                }

        bid_price = float(decision.get("bid_price", market_data["price"]))
        quantity = float(decision.get("quantity", 0))
        provides_liquidity = float(decision.get("provides_liquidity", 0))

        cash, position = (
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )
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
            "reasoning": decision.get("reasoning", "N/A")[:100],
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
    """Market maker - provides liquidity."""

    pass


class LLMLiquidityDemander(LLMInvestor):
    """Liquidity demander - takes liquidity."""

    pass


class LLMArbitrageur(LLMInvestor):
    """Arbitrageur - seeks opportunities."""

    pass


class LLMValueInvestor(LLMInvestor):
    """Value investor - patient buyer."""

    pass


class LLMForcedSeller(LLMInvestor):
    """Forced seller - must sell."""

    pass
