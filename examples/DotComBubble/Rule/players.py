import random
import logging
from masim.player.base import Action

"""DotComBubble Rule-Based Simulation

1995-2001 Internet bubble - NASDAQ rose 400% then fell 78%

Theoretical Foundation:
- Shiller (2000): Irrational Exuberance and narrative economics
- Ofek & Richardson (2003): Internet bubble dynamics
- Abreu & Brunnermeier (2003): Synchronization risk and bubble persistence

Key Dynamics:
- NewEconomyEvangelist: Believes in new paradigm, ignores traditional valuation
- IPOFlipper: Buys IPOs and quickly sells for short-term profit
- MomentumFollower: Follows price trends and amplifies moves
- SkepticalValueInvestor: Avoids overvalued tech stocks, waits for correction
- ShortSeller: Bets against overvalued stocks but faces squeeze risk

Parameters from config (see configs/DotComBubble/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("DotComBubble")


class Market(GeneralPlayer):
    """
    Market agent for DotComBubble simulation.
    
    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε
    
    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion strength  
        - F: Fundamental value
        - ε: Random noise
    """
    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "price" not in self.state.custom_state:
            self._initialize_market_state()
        
        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()
    
    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        
        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]
    
    def _extract_orders(self, observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append({
                    "agent_id": msg.get("from"),
                    "action": msg.get("action"),
                    "quantity": msg.get("quantity"),
                    "agent_type": msg.get("agent_type"),
                })
        return orders
    
    def _clear_market(self, orders: list) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        
        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell
        
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        
        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        
        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)
        
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5
        
        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }
    
    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])
    
    def _log_market_state(self) -> None:
        logger = logging.getLogger("{name}")
        logger.debug(
            "Round %%d: price=%%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )
    
    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        
        return Action(
            action_type="market_broadcast",
            payload={"market_data": market_update, "outbound_messages": [{"payload": market_update, "content_type": "market_update"}]},
            source_id=self.identity,
        )


    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """New economy narrative: ignores traditional valuation, buys growth stories."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        narrative_strength = extras["narrative_strength"]
        val_multiplier = extras["valuation_multiplier"]
        
        perceived_value = fundamental * val_multiplier
        if price < perceived_value:
            buy_qty = min(int(cash * narrative_strength / price), 2000) if price > 0 else 0
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """IPO flipping: buys new issues and sells quickly for profit."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        target_return = extras["target_return"]
        flip_days = extras["flip_days"]
        
        if position > 0 and deviation > target_return:
            return {"action": "sell", "quantity": position}
        elif deviation < -0.02:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Momentum following: rides price trends."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras["entry_threshold"]
        
        if deviation > entry_threshold:
            buy_qty = min(2000, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -entry_threshold:
            sell_qty = min(2000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Value investing with high skepticism toward growth narratives."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        max_pe = extras["max_pe"]
        
        if deviation < -0.3:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > 1.0:
            sell_qty = min(500, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Short selling: bets against overvalued stocks with squeeze risk."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        short_threshold = extras["short_threshold"]
        squeeze_tolerance = extras["squeeze_tolerance"]
        
        if deviation > short_threshold:
            short_qty = min(2000, int(cash / price) if price > 0 else 0)
            if short_qty > 0:
                return {"action": "sell", "quantity": short_qty}
        elif deviation > 0 and position < 0:
            if deviation < squeeze_tolerance:
                cover_qty = min(abs(position), 500)
                return {"action": "buy", "quantity": cover_qty}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "NewEconomyEvangelist", "IPOFlipper", "MomentumFollower", "SkepticalValueInvestor", "ShortSeller"]
