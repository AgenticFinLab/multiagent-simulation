"""DispositionEffectLLM - LLM-based Prospect Theory Trading Simulation

Phenomenon: Disposition Effect (Shefrin & Statman 1985)
    - Investors sell winners too early (realize gains prematurely)
    - Investors hold losers too long (reluctant to realize losses)

Theoretical Foundation:
    - Prospect Theory (Kahneman & Tversky 1979)
    - Loss Aversion: λ ≈ 2.25 (losses hurt 2.25x more than gains)
    - Reference Point: Purchase price as psychological anchor
    - S-shaped value function: Concave for gains, convex for losses

LLM Investor Types:
    - Disposition Investor: Exhibits classic disposition effect
    - Rational Investor: Expected utility maximizer
    - Tax-Aware Investor: Considers tax-loss harvesting
    - Institutional Investor: Less prone to behavioral biases
    - Loss-Averse Investor: Extreme loss aversion
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
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """Central market with news shocks to create gain/loss situations."""

    INITIAL_PRICE = 100.0
    FUNDAMENTAL_VALUE = 100.0
    PRICE_IMPACT = 0.06
    MEAN_REVERSION = 0.015
    NOISE_STD = 0.4
    NEWS_PROBABILITY = 0.15
    NEWS_IMPACT_RANGE = 5.0
    HISTORY_LIMIT = 200

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
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
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
        orders = self.state.custom_state["orders"]

        # Random news shock
        news_shock = 0.0
        news_event = None
        if random.random() < self.NEWS_PROBABILITY:
            news_shock = random.uniform(-self.NEWS_IMPACT_RANGE, self.NEWS_IMPACT_RANGE)
            news_event = "positive" if news_shock > 0 else "negative"

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty

        # Price update
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(
            1.0, current_price + price_impact + mean_reversion + noise + news_shock
        )
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        if news_event:
            print(f"  NEWS: {news_event} shock ({news_shock:+.2f})")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "fundamental": self.FUNDAMENTAL_VALUE,
            "news_event": news_event,
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


# =============================================================================
# LLM Disposition Investor Base Class
# =============================================================================


class LLMDispositionInvestor(GeneralPlayer):
    """Base class for LLM-powered disposition effect investors."""

    STRATEGY_NAME = "llm_disposition_base"
    SYSTEM_PROMPT = "You are an investor subject to behavioral biases."
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 50.0
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
            # Reference point = purchase price (psychological anchor)
            self.state.custom_state["purchase_price"] = 100.0

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
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        current_price = market_data["price"]

        # Calculate gain/loss
        gain_loss = (current_price - purchase_price) / purchase_price * 100
        gain_loss_status = (
            "GAIN" if gain_loss > 0 else "LOSS" if gain_loss < 0 else "EVEN"
        )

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                fundamental=market_data["fundamental"],
                purchase_price=purchase_price,
                gain_loss=gain_loss,
                gain_loss_status=gain_loss_status,
                news_event=market_data["news_event"],
                cash=cash,
                position=position,
                portfolio_value=cash + position * market_data["price"],
            )

        return f"""
Market Data:
- Price: ${market_data['price']:.2f}
- Return: {market_data['return_pct']:+.2f}%
- Fundamental: ${market_data['fundamental']:.2f}

Your Position:
- Purchase Price: ${purchase_price:.2f} (your reference point)
- Current Price: ${current_price:.2f}
- Gain/Loss: {gain_loss:+.2f}% ({gain_loss_status})
- Position: {position:.2f} shares
- Cash: ${cash:.2f}

Respond with JSON: {{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}}
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
        raise ValueError(f"Failed to parse: {response_text[:100]}")

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
        llm_client = self.state.custom_state["llm_client"]

        user_prompt = self._build_prompt(market_data)
        llm_config = self.config.extras["llm"]
        system_prompt = (
            load_prompt(llm_config["sys_message"])
            if "sys_message" in llm_config
            else self.SYSTEM_PROMPT
        )

        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM failed: {e}")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity)

        # Update purchase price if buying
        if quantity > 0:
            old_position = self.state.custom_state["position"]
            old_cost = old_position * self.state.custom_state["purchase_price"]
            new_cost = quantity * bid_price
            total_position = old_position + quantity
            if total_position > 0:
                self.state.custom_state["purchase_price"] = (
                    old_cost + new_cost
                ) / total_position
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:15s}): Q={quantity:+7.2f}"
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
# LLM Disposition Investor Types
# =============================================================================


class LLMDispositionBiased(LLMDispositionInvestor):
    """Classic disposition effect - sells winners, holds losers."""

    STRATEGY_NAME = "llm_disposition_biased"
    SYSTEM_PROMPT = """You are an investor with STRONG DISPOSITION EFFECT bias.

CORE BELIEF: "A profit isn't real until you sell. Losses aren't real if you don't sell."

YOUR PSYCHOLOGY (Prospect Theory):
1. You HATE realizing losses - they feel 2.25x worse than gains feel good
2. When at a GAIN: You feel urge to "lock in" profits quickly
3. When at a LOSS: You refuse to sell - "it will come back"

YOUR BEHAVIOR:
- If gain > 5%: Strong urge to sell and realize profit
- If gain > 10%: Very strong urge to sell immediately
- If loss < -5%: Hold, hoping for recovery
- If loss < -10%: Still hold - "can't sell at a loss"

PSYCHOLOGICAL JUSTIFICATION:
- "I don't want to lose the gain I've made"
- "If I sell at a loss, I'm admitting I was wrong"
- "The market will recover eventually"

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMRationalInvestor(LLMDispositionInvestor):
    """Expected utility maximizer - no disposition bias."""

    STRATEGY_NAME = "llm_rational"
    SYSTEM_PROMPT = """You are a RATIONAL INVESTOR who maximizes expected utility.

CORE BELIEF: "Past prices are irrelevant - only future prospects matter."

YOUR APPROACH:
1. Your purchase price is IRRELEVANT to your decision
2. Only consider: current price vs fundamental value
3. You have NO emotional attachment to gains or losses
4. You sell when overvalued, buy when undervalued

DECISION RULE:
- If price > 1.05 × fundamental: Sell (overvalued)
- If price < 0.95 × fundamental: Buy (undervalued)
- Otherwise: Hold

You do NOT care about "realizing" gains or losses - only expected returns.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMTaxAwareInvestor(LLMDispositionInvestor):
    """Tax-loss harvesting - opposite of disposition effect."""

    STRATEGY_NAME = "llm_tax_aware"
    SYSTEM_PROMPT = """You are a TAX-AWARE INVESTOR focused on after-tax returns.

CORE BELIEF: "Tax-loss harvesting improves after-tax returns."

YOUR STRATEGY:
1. SELL losers to realize tax losses (opposite of disposition!)
2. HOLD winners to defer capital gains taxes
3. You actively look for opportunities to realize losses

TAX LOGIC:
- Realized losses offset other gains (tax benefit)
- Unrealized gains grow tax-free (tax deferral)
- Loss > 3%: Consider selling for tax benefit
- Gain > 0%: Prefer holding to defer taxes

You are ANTI-disposition - you sell losers and hold winners for tax reasons.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMInstitutionalInvestor(LLMDispositionInvestor):
    """Professional investor - reduced behavioral biases."""

    STRATEGY_NAME = "llm_institutional"
    SYSTEM_PROMPT = """You are an INSTITUTIONAL INVESTOR with professional discipline.

CORE BELIEF: "Emotion has no place in investment decisions."

YOUR APPROACH:
1. You follow a systematic process
2. Purchase price is noted but doesn't drive decisions
3. You rebalance based on portfolio weights, not emotions
4. You can sell losers and hold winners when appropriate

RULES:
- Position > 40% of portfolio: Reduce for diversification
- Valuation vs fundamental matters more than gain/loss
- You acknowledge behavioral biases but consciously override them

You are disciplined and process-driven.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMLossAverse(LLMDispositionInvestor):
    """Extreme loss aversion - paralyzed by losses."""

    STRATEGY_NAME = "llm_loss_averse"
    SYSTEM_PROMPT = """You are an EXTREMELY LOSS-AVERSE investor.

CORE BELIEF: "I absolutely cannot afford to lose money."

YOUR PSYCHOLOGY:
1. Losses feel 3x worse than gains feel good (extreme λ)
2. When losing: You are PARALYZED and cannot act
3. When gaining: You are NERVOUS and want to protect gains
4. Any volatility makes you anxious

BEHAVIOR:
- At a loss: NEVER sell, just hope and pray
- At a gain: Sell quickly to protect what you have
- High volatility: Reduce exposure immediately
- You prefer certainty over expected value

Warning signs of your paralysis:
- Loss > 5%: You freeze, unable to decide
- Loss > 10%: Complete denial

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
