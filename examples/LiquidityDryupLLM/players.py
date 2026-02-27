"""LiquidityDryupLLM - LLM-based Market Maker Inventory Model Simulation

Phenomenon: Liquidity Dry-up
    - Market makers withdraw liquidity during stress
    - Creates self-reinforcing cycles of illiquidity
    - Reference: Grossman & Miller (1988), Amihud & Mendelson (1986)

LLM Investor Types:
    - Market Maker: Provides liquidity for spread, withdraws in stress
    - Liquidity Demander: Takes liquidity, suffers from dry-up
    - Arbitrageur: Profits from mispricings during illiquidity
    - Value Investor: Patient buyer waiting for extreme mispricings
    - Forced Seller: Must sell regardless of liquidity conditions
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
    """Market with liquidity-dependent pricing."""

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0
    PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.015
    NOISE_STD = 0.4
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["total_liquidity"] = 100.0
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
                        "provides_liquidity": order["provides_liquidity"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        liquidity_provided = sum(o["provides_liquidity"] for o in orders)
        total_liquidity = 50.0 + liquidity_provided

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell

        # Illiquidity amplifies price impact
        liquidity_factor = 100.0 / max(total_liquidity, 10.0)
        price_impact = self.PRICE_IMPACT * net_demand * liquidity_factor
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["total_liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)

        status = (
            "DRYUP!"
            if total_liquidity < 30
            else "Stressed" if total_liquidity < 60 else "Normal"
        )
        print(f"\n{'='*60}")
        print(
            f"[Market] Round {round_num}: ${current_price:.2f} → ${new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Liquidity: {total_liquidity:.1f}, Impact Factor: {liquidity_factor:.2f}x [{status}]"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "liquidity": total_liquidity,
            "liquidity_factor": liquidity_factor,
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


class LLMLiquidityInvestor(GeneralPlayer):
    """Base class for liquidity dry-up investors."""

    STRATEGY_NAME = "llm_liquidity_base"
    SYSTEM_PROMPT = "You trade in a market where liquidity can dry up."
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 50.0

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION

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
                liquidity=market_data["liquidity"],
                liquidity_factor=market_data["liquidity_factor"],
                fundamental=market_data["fundamental"],
                cash=self.state.custom_state["cash"],
                position=self.state.custom_state["position"],
                portfolio_value=self.state.custom_state["cash"]
                + self.state.custom_state["position"] * market_data["price"],
            )
        return f"Price: ${market_data['price']:.2f}, Liquidity: {market_data['liquidity']:.1f}"

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
        provides_liquidity = float(decision["provides_liquidity"])

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


class LLMMarketMaker(LLMLiquidityInvestor):
    """Market maker - provides liquidity, withdraws in stress."""

    STRATEGY_NAME = "llm_market_maker"
    SYSTEM_PROMPT = """You are a MARKET MAKER providing liquidity for profit.

YOUR ROLE:
- You PROVIDE liquidity by standing ready to buy/sell
- You profit from bid-ask spread
- You set provides_liquidity > 0 when active

WITHDRAWAL CONDITIONS (you STOP providing liquidity):
- Liquidity < 50: Others withdrawing - you withdraw too
- Liquidity factor > 1.5: Market stressed
- Return magnitude > 3%: Too volatile

When WITHDRAWN: provides_liquidity = 0, hold or small trades
When ACTIVE: provides_liquidity = 20-40, buy dips/sell rallies

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "provides_liquidity": float, "reasoning": string}
"""


class LLMLiquidityDemander(LLMLiquidityInvestor):
    """Liquidity demander - takes liquidity, suffers from dry-up."""

    STRATEGY_NAME = "llm_liquidity_demander"
    SYSTEM_PROMPT = """You are a LIQUIDITY DEMANDER who needs to trade.

YOUR SITUATION:
- You NEED to trade for portfolio reasons
- You TAKE liquidity (provides_liquidity = 0)
- When liquidity is low, your trades move prices more

STRATEGY:
- If liquidity high (>70): Trade normally
- If liquidity medium (50-70): Trade cautiously, smaller size
- If liquidity low (<50): Trade only if necessary, accept price impact

You suffer when liquidity dries up!
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMArbitrageur(LLMLiquidityInvestor):
    """Arbitrageur - profits from mispricings during illiquidity."""

    STRATEGY_NAME = "llm_arbitrageur"
    SYSTEM_PROMPT = """You are an ARBITRAGEUR profiting from liquidity dry-ups.

YOUR STRATEGY:
- When liquidity is low, prices deviate from fundamentals
- You buy undervalued (price < fundamental) in illiquid markets
- You sell overvalued (price > fundamental)
- You PROVIDE liquidity when others withdraw

TIMING:
- Liquidity < 40: Prime opportunity for mispricing
- Price deviation > 5% from fundamental: Trade opportunity
- You are a stabilizing force

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "provides_liquidity": float, "reasoning": string}
"""


class LLMValueInvestor(LLMLiquidityInvestor):
    """Value investor - patient buyer during extreme mispricings."""

    STRATEGY_NAME = "llm_value_investor"
    SYSTEM_PROMPT = """You are a VALUE INVESTOR waiting for extreme mispricings.

YOUR STRATEGY:
- You only trade when price significantly deviates from fundamental
- Liquidity dry-up creates opportunities
- Price < 0.90 × fundamental: Buy
- Price > 1.10 × fundamental: Sell
- You are PATIENT - don't trade every round

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMForcedSeller(LLMLiquidityInvestor):
    """Forced seller - must sell regardless of conditions."""

    STRATEGY_NAME = "llm_forced_seller"
    SYSTEM_PROMPT = """You are a FORCED SELLER who MUST sell.

YOUR SITUATION:
- You need to liquidate your position over time
- You MUST sell 10-20 shares per round regardless of conditions
- You cannot wait for better liquidity
- You accept price impact as a cost

BEHAVIOR:
- Always sell, quantity = -10 to -20
- Low liquidity = higher cost for you
- You are a source of selling pressure

Respond with JSON: {"action": "sell", "bid_price": float, "quantity": float, "reasoning": string}
Note: quantity should be NEGATIVE (selling)
"""
