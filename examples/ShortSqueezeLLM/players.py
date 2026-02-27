"""ShortSqueezeLLM - LLM-based Supply-Demand Imbalance Simulation

Phenomenon: Short Squeeze
    - Heavily shorted stock rises, forcing short sellers to cover
    - Creates positive feedback loop (cover → price rises → more covering)
    - GameStop 2021 is a famous example

LLM Investor Types:
    - Short Seller: Borrows and sells, forced to cover on losses
    - Retail Coordinator: Triggers initial squeeze (Reddit style)
    - Momentum Buyer: Buys on upward momentum
    - Value Investor: Buys when undervalued
    - Institutional Holder: Large passive holder
"""

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


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """Market with short interest tracking."""

    FUNDAMENTAL_VALUE = 50.0  # Low fundamental - typical for shorted stocks
    INITIAL_PRICE = 30.0  # Trading below fundamental
    PRICE_IMPACT = 0.1
    MEAN_REVERSION = 0.005  # Weak - allows squeeze to develop
    NOISE_STD = 0.5
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["short_interest"] = (
                80.0  # Start with high short interest
            )
            self.state.custom_state["squeeze_pressure"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=self.HISTORY_LIMIT
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
                        "is_short_cover": order["is_short_cover"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        short_interest = self.state.custom_state["short_interest"]
        orders = self.state.custom_state["orders"]

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        cover_buying = sum(
            o["quantity"] for o in orders if o["is_short_cover"] and o["quantity"] > 0
        )
        net_demand = total_buy - total_sell

        # Short cover has extra price impact (forced buying)
        short_squeeze_impact = cover_buying * 0.05
        price_impact = self.PRICE_IMPACT * net_demand + short_squeeze_impact
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update short interest (decreases when shorts cover)
        short_interest = max(0.0, short_interest - cover_buying * 0.5)

        # Squeeze pressure indicator
        squeeze_pressure = max(0.0, (new_price / self.INITIAL_PRICE - 1) * 100)

        self.state.custom_state["price"] = new_price
        self.state.custom_state["short_interest"] = short_interest
        self.state.custom_state["squeeze_pressure"] = squeeze_pressure
        self.state.custom_state["price_history"].append(new_price)

        status = (
            "SQUEEZE!"
            if squeeze_pressure > 50
            else "Building" if squeeze_pressure > 20 else "Normal"
        )
        print(f"\n{'='*60}")
        print(
            f"[Market] Round {round_num}: ${current_price:.2f} → ${new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Short Interest: {short_interest:.1f}%, Squeeze Pressure: {squeeze_pressure:.1f}% [{status}]"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "short_interest": short_interest,
            "squeeze_pressure": squeeze_pressure,
            "fundamental": self.FUNDAMENTAL_VALUE,
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


class LLMShortSqueezeInvestor(GeneralPlayer):
    """Base class for short squeeze investors."""

    STRATEGY_NAME = "llm_squeeze_base"
    SYSTEM_PROMPT = "You trade in a heavily shorted stock."
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0  # Start with no position

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["short_position"] = 0.0

            load_dotenv()
            llm_config = self.config.extras["llm"]
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
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                short_interest=market_data["short_interest"],
                squeeze_pressure=market_data["squeeze_pressure"],
                fundamental=market_data["fundamental"],
                cash=self.state.custom_state["cash"],
                position=self.state.custom_state["position"],
                short_position=self.state.custom_state["short_position"],
                portfolio_value=self.state.custom_state["cash"]
                + self.state.custom_state["position"] * market_data["price"],
            )
        return f"Price: ${market_data['price']:.2f}, Short Interest: {market_data['short_interest']:.1f}%"

    def _parse_response(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Parse failed: {text[:100]}")

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        llm_config = self.config.extras["llm"]
        system_prompt = (
            load_prompt(llm_config["sys_message"])
            if "sys_message" in llm_config
            else self.SYSTEM_PROMPT
        )

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
                    "reasoning": "error",
                }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        is_short_cover = decision["is_short_cover"]

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

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "is_short_cover": is_short_cover,
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


class LLMShortSeller(LLMShortSqueezeInvestor):
    """Short seller - forced to cover when squeezed."""

    STRATEGY_NAME = "llm_short_seller"
    INITIAL_POSITION = -50.0  # Start short

    SYSTEM_PROMPT = """You are a SHORT SELLER who is SHORT this stock.

CRITICAL: You have a SHORT position of 50 shares. If price rises too much, you MUST cover (buy to close).

RISK MANAGEMENT:
- Price > $40: Consider covering (20% loss on $30 short)
- Price > $50: MUST cover half (66% loss)
- Price > $60: MUST cover all (100%+ loss)
- Squeeze pressure > 50%: DANGER - cover immediately

When covering, set is_short_cover: true and quantity: positive (buying)

You are at RISK of unlimited losses if squeezed!
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "is_short_cover": bool, "reasoning": string}
"""


class LLMRetailCoordinator(LLMShortSqueezeInvestor):
    """Retail trader coordinating the squeeze (Reddit style)."""

    STRATEGY_NAME = "llm_retail_coord"
    SYSTEM_PROMPT = """You are a RETAIL TRADER coordinating a short squeeze (like Reddit/WSB).

CORE BELIEF: "To the moon! Diamond hands! Squeeze the shorts!"

YOUR STRATEGY:
1. BUY aggressively to trigger the squeeze
2. HOLD during dips ("diamond hands")
3. Encourage momentum with large buys
4. Target: Force short sellers to cover at higher prices

TIMING:
- Short interest > 50%: Prime for squeeze - BUY MORE
- Squeeze pressure rising: Add to position
- Price dipping but shorts still high: HOLD, don't sell

You are trying to CREATE the squeeze!
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMMomentumBuyer(LLMShortSqueezeInvestor):
    """Momentum trader joining the squeeze."""

    STRATEGY_NAME = "llm_momentum_buyer"
    SYSTEM_PROMPT = """You are a MOMENTUM TRADER riding the squeeze.

CORE BELIEF: "The trend is your friend - especially in a squeeze."

STRATEGY:
- Positive returns: BUY (momentum continuation)
- Squeeze pressure > 30%: Increase buying
- Price falling: Reduce or exit

You don't coordinate - you just follow momentum.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMValueInvestor(LLMShortSqueezeInvestor):
    """Value investor - cautious during squeeze."""

    STRATEGY_NAME = "llm_value_investor"
    SYSTEM_PROMPT = """You are a VALUE INVESTOR watching the squeeze skeptically.

CORE BELIEF: "This is disconnected from fundamentals."

YOUR VIEW:
- Price < $50 (fundamental): May buy for value
- Price > $50: Overvalued - stay out or sell
- Squeeze is temporary - prices will revert

You are CAUTIOUS about buying into mania.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMInstitutionalHolder(LLMShortSqueezeInvestor):
    """Large institutional holder - can lend shares."""

    STRATEGY_NAME = "llm_institutional"
    INITIAL_POSITION = 100.0  # Large holder

    SYSTEM_PROMPT = """You are a LARGE INSTITUTIONAL HOLDER with 100 shares.

YOUR SITUATION:
- You own shares and can profit from price increases
- You may sell some to take profits
- You are NOT short - no squeeze pressure on you

STRATEGY:
- Price increases significantly: Take some profits (sell 20-30%)
- Squeeze seems unsustainable: Reduce position
- You are a stabilizing force

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
