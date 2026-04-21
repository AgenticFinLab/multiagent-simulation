import random
import logging
from masim.player.base import Action

"""MentalAccounting Rule-Based Simulation

Mental accounting causes investors to treat money differently based on its source or intended use

Theoretical Foundation:
- Thaler (1999): Mental Accounting Matters
- Thaler (1985): Mental accounting and consumer choice
- Barberis & Huang (2001): Mental accounting, loss aversion, and individual stock returns

Key Dynamics:
- MentalAccountant: Segregates portfolio into separate accounts, doesn't net gains/losses
- HouseMoneyTrader: Takes more risk with recent gains
- RationalPortfolioManager: Optimizes entire portfolio without mental accounting
- SunkCostHolder: Holds losing positions due to already invested capital
- NoiseTrader: Random uninformed trader

Parameters from config (see configs/MentalAccounting/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("MentalAccounting")


class Market(GeneralPlayer):
    """
    Market agent for MentalAccounting simulation.
    
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
        """Mental accounting: segregates portfolio into separate accounts."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        num_accounts = extras["num_accounts"]
        loss_lambda = extras["loss_aversion_per_account"]
        
        per_account_position = position / num_accounts if num_accounts > 0 else position
        per_account_cash = cash / num_accounts if num_accounts > 0 else cash
        
        entry_price = self.state.custom_state["entry_price"]
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0.05:
            sell_qty = int(per_account_position * 0.7)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        elif pnl < -0.05 * loss_lambda:
            sell_qty = int(per_account_position * 0.2)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """House money effect: takes more risk with recent gains."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        gain_risk = extras["gain_risk_multiplier"]
        loss_risk = extras["loss_risk_multiplier"]
        
        entry_price = self.state.custom_state["entry_price"]
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0:
            risk_factor = gain_risk
        else:
            risk_factor = loss_risk
        
        if abs(deviation) > 0.02:
            qty = min(int(500 * risk_factor), int(cash * risk_factor / price) if price > 0 else 0)
            if qty > 0:
                return {"action": "buy", "quantity": qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rational portfolio: optimizes entire portfolio."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras["risk_aversion"]
        
        if abs(deviation) > 0.02:
            qty = min(500, int(abs(deviation) * risk_aversion * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Sunk cost: holds losing positions due to already invested capital."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        sunk_weight = extras["sunk_cost_weight"]
        
        entry_price = self.state.custom_state["entry_price"]
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0.1:
            sell_qty = int(position * 0.5)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Noise trader: random uninformed trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras["trade_probability"]
        
        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "MentalAccountant", "HouseMoneyTrader", "RationalPortfolioManager", "SunkCostHolder", "NoiseTrader"]
