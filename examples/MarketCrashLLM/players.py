"""MarketCrashLLM - LLM-based Market Crash Simulation

Phenomenon: Market Crash with LLM Decision-Making
    LLM investors simulate different crash-related trading personalities:
    - Panic Seller (accelerates crash)
    - Risk Parity Fund (volatility-sensitive, forced selling)
    - Leveraged Fund (margin-triggered liquidation)
    - Market Maker (liquidity withdrawal)
    - Bottom Fisher (provides eventual floor)

Theoretical Foundation:
    - Minsky Moment: Sudden shift from stability to instability
    - Liquidity Spiral (Brunnermeier & Pedersen, 2009)
    - Fire Sales: Forced selling creates additional price pressure

Key Crash Dynamics:
    1. Initial shock → Price drops
    2. Volatility rises → Risk parity reduces exposure
    3. Leveraged funds hit margin → Forced liquidation
    4. Market makers withdraw → Liquidity evaporates
    5. Panic sellers add pressure → Crash accelerates
    6. Bottom fishers provide eventual floor
"""

import os
import json
import random
import re
import importlib
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Rule-Based (Same as MarketCrash)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Price Model:
        P(t+1) = P(t) + λ(L) × NetDemand + γ × [F - P(t)] + σ × ε

    Where λ(L) is liquidity-adjusted price impact:
        - When liquidity is high: low impact
        - When liquidity is low: high impact (accelerates crashes)
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    BASE_PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.01
    NOISE_STD = 0.5

    LIQUIDITY_DECAY = 0.1
    LIQUIDITY_RECOVERY = 0.05
    MIN_LIQUIDITY = 0.1

    HISTORY_LIMIT = 300

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["liquidity"] = 1.0
            self.state.custom_state["volatility"] = 1.0
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=self.HISTORY_LIMIT,
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_liquidity = self.state.custom_state["liquidity"]
        orders = self.state.custom_state["orders"]

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Liquidity dynamics
        if net_demand < -5:  # Heavy selling
            new_liquidity = max(
                self.MIN_LIQUIDITY, current_liquidity * (1 - self.LIQUIDITY_DECAY)
            )
        else:
            new_liquidity = min(1.0, current_liquidity + self.LIQUIDITY_RECOVERY)

        # Price impact increases as liquidity drops
        liquidity_multiplier = 1.0 / max(new_liquidity, self.MIN_LIQUIDITY)
        price_impact = self.BASE_PRICE_IMPACT * liquidity_multiplier * net_demand

        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update volatility estimate
        prev_return = self.state.custom_state["prev_return"]
        new_volatility = (
            0.9 * self.state.custom_state["volatility"] + 0.1 * abs(price_return) * 100
        )

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = new_liquidity
        self.state.custom_state["volatility"] = new_volatility
        self.state.custom_state["prev_return"] = price_return

        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["liquidity_history"].append(new_liquidity)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Liquidity: {new_liquidity:.2f}, Volatility: {new_volatility:.2f}")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  LLM Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:20s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
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
            "fundamental": self.FUNDAMENTAL_VALUE,
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
# LLM Crash Investor Base Class
# =============================================================================


class LLMCrashInvestor(GeneralPlayer):
    """Base class for LLM-powered crash investors."""

    STRATEGY_NAME = "llm_crash_base"
    SYSTEM_PROMPT = "You are an investor in a potentially crashing market."

    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 50.0  # Start with position to enable selling
    HISTORY_LIMIT = 100

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION

            load_dotenv()
            llm_config = self.config.extras["llm"]
            lm_name = llm_config["lm_name"]
            generation_config = llm_config["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config

            llm_client = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["llm_client"] = llm_client

            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

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
                llm_client = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )
                custom["llm_client"] = llm_client

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build user prompt with crash-specific market data."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
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

        return f"""
Current Market Data:
- Price: ${market_data['price']:.2f}
- Previous Price: ${market_data['prev_price']:.2f}
- Return: {market_data['return_pct']:+.2f}%
- Liquidity: {market_data['liquidity']:.2f} (1.0=normal, lower=stress)
- Volatility: {market_data['volatility']:.2f}
- Volume: {market_data['volume']:.2f}
- Net Demand: {market_data['net_demand']:+.2f}
- Fundamental Value: ${market_data['fundamental']:.2f}
- Recent Prices: {recent_prices}

Your Portfolio:
- Cash: ${cash:.2f}
- Position: {position:.2f} shares
- Portfolio Value: ${cash + position * market_data['price']:.2f}

Respond with ONLY valid JSON:
{{"action": "buy" | "sell" | "hold", "bid_price": <your price>, "quantity": <shares, +buy/-sell>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        raise ValueError(f"Failed to parse LLM response: {response_text[:100]}")

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]

        user_prompt = self._build_prompt(market_data)

        llm_config = self.config.extras["llm"]
        if "sys_message" in llm_config:
            system_prompt = load_prompt(llm_config["sys_message"])
        else:
            system_prompt = self.SYSTEM_PROMPT

        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM failed after {max_retries} attempts: {e}")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity)

        # Execute trade
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
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


# =============================================================================
# LLM Crash Investor Types
# =============================================================================


class LLMPanicSeller(LLMCrashInvestor):
    """
    LLM Panic Seller - Accelerates crash through fear-driven selling.

    Behavioral Finance: Loss aversion + herding in crisis
    """

    STRATEGY_NAME = "llm_panic_seller"
    SYSTEM_PROMPT = """You are a PANIC-PRONE RETAIL INVESTOR who is extremely fearful.

CORE BELIEF: "I can't afford to lose any more money - I need to get out NOW!"

YOUR BEHAVIOR:
1. You PANIC when you see falling prices
2. The more the price drops, the MORE urgently you want to sell
3. You watch liquidity closely - low liquidity terrifies you
4. You don't care about fundamental value during a crisis
5. You SELL at ANY price just to exit

PSYCHOLOGICAL PROFILE:
- Extreme loss aversion (losses hurt 3x more than gains feel good)
- You experience FOMO (fear of missing out) on selling
- You follow the crowd - if others are selling, you sell harder
- During normal times, you may hold or buy cautiously

TRIGGERS FOR PANIC SELLING:
- Price drop > 2% in a round
- Liquidity below 0.7
- Net demand strongly negative
- Your portfolio value declining

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMRiskParityFund(LLMCrashInvestor):
    """
    LLM Risk Parity Fund - Volatility-sensitive forced selling.

    Theory: Risk parity strategies reduce exposure when volatility rises,
    which can accelerate crashes through synchronized selling.
    """

    STRATEGY_NAME = "llm_risk_parity"
    SYSTEM_PROMPT = """You are a RISK PARITY FUND MANAGER following strict volatility targeting.

CORE BELIEF: "We must maintain constant portfolio risk - when volatility rises, we MUST reduce exposure."

YOUR RULES (MANDATORY - you cannot deviate):
1. Target volatility: 1.5
2. If current volatility > 2.0: You MUST reduce position significantly
3. If current volatility > 3.0: You MUST sell aggressively to de-risk
4. If volatility < 1.0: You MAY increase position

CALCULATION:
- position_adjustment = (target_vol - current_vol) * current_position * 0.3
- Negative adjustment = MUST SELL

BEHAVIOR:
- You are NOT emotional - you follow rules mechanically
- You don't care about price levels, only volatility
- Your selling during high vol can CAUSE more volatility (feedback loop)
- You cannot ignore your risk mandate

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Note: Include your volatility calculation in reasoning.
"""


class LLMLeveragedFund(LLMCrashInvestor):
    """
    LLM Leveraged Fund - Margin-triggered forced liquidation.

    Theory: Leverage creates forced selling at worst times.
    """

    STRATEGY_NAME = "llm_leveraged_fund"
    INITIAL_POSITION = 80.0  # Higher leverage exposure

    SYSTEM_PROMPT = """You are a LEVERAGED HEDGE FUND using 2x leverage.

CORE BELIEF: "Leverage amplifies returns... until it amplifies losses."

YOUR CONSTRAINTS:
1. Starting leverage: 2x (you own $16000 worth on $10000 capital)
2. MARGIN CALL: If portfolio value drops below $7500, you MUST liquidate 50%
3. FORCED LIQUIDATION: If portfolio value drops below $5000, you MUST sell EVERYTHING

CRITICAL: Calculate your current portfolio value each round:
- Portfolio Value = Cash + Position × Price
- If below thresholds, you HAVE NO CHOICE but to sell

BEHAVIOR:
- During normal times: May buy/hold to maintain leverage
- During stress: MUST follow margin rules - no exceptions
- Your forced selling adds to market pressure
- You can trigger cascade if your liquidation pushes others to margin

WARNING SIGNS:
- Portfolio value approaching $7500 → prepare to cut
- Rapid price decline → you may be forced out

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Note: ALWAYS state your current portfolio value in reasoning.
"""


class LLMMarketMaker(LLMCrashInvestor):
    """
    LLM Market Maker - Liquidity provider who withdraws in stress.

    Theory: Market makers provide liquidity in normal times but
    withdraw during crises, causing liquidity to evaporate.
    """

    STRATEGY_NAME = "llm_market_maker"
    INITIAL_POSITION = 30.0

    SYSTEM_PROMPT = """You are a MARKET MAKER providing liquidity for profit.

CORE BELIEF: "I profit from the bid-ask spread, but I won't catch falling knives."

YOUR BUSINESS MODEL:
1. Normal times: You buy dips and sell rallies (stabilizing)
2. Crisis times: You WITHDRAW to protect your capital

WITHDRAWAL TRIGGERS (you STOP providing liquidity):
- Liquidity < 0.5 (others are withdrawing)
- Volatility > 3.0 (too dangerous)
- Price drop > 5% in one round (catching falling knife)
- Net demand < -10 (one-sided market)

WHEN WITHDRAWN:
- You may hold, or slowly reduce position
- You do NOT buy until conditions normalize
- You prioritize capital preservation over profit

WHEN ACTIVE (normal conditions):
- You buy when price dips (expecting mean reversion)
- You sell when price spikes (taking profit)
- Position size: moderate (10-25 shares)

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Note: State whether you are "ACTIVE" or "WITHDRAWN" in reasoning.
"""


class LLMBottomFisher(LLMCrashInvestor):
    """
    LLM Bottom Fisher - Value buyer who provides eventual floor.

    Theory: Eventually, prices become attractive enough that
    value buyers step in and provide a floor.
    """

    STRATEGY_NAME = "llm_bottom_fisher"
    INITIAL_POSITION = 10.0  # Light starting position

    SYSTEM_PROMPT = """You are a BOTTOM FISHER / VALUE INVESTOR waiting for extreme bargains.

CORE BELIEF: "Be greedy when others are fearful - but only at the RIGHT price."

YOUR STRATEGY:
1. You WAIT for extreme undervaluation
2. You only buy when price < 0.8 × fundamental (20%+ discount)
3. The LOWER the price, the MORE you buy
4. You are PATIENT - you can wait many rounds

BUYING CRITERIA:
- Price < $80: Start buying cautiously (10-20 shares)
- Price < $70: Buy moderately (20-40 shares)
- Price < $60: Buy aggressively (40-60 shares)
- Price > $90: Hold or reduce position

BEHAVIOR:
- You are NOT emotional - crashes are opportunities
- You don't panic sell during crashes
- You provide stabilizing demand when others panic
- You are the "buyer of last resort"

PATIENCE:
- If conditions aren't right, just "hold"
- Don't chase the market - let it come to you

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
