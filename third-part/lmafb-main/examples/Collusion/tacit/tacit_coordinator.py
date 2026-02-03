"""
This system simulates tacit collusion, where firms implicitly coordinate their pricing behavior without direct
communication
"""

import os
import math
import json
import random
import logging
from typing import Dict

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.tacit.tacit_prompt import TACIT_COLLUSION_PROMPT


@ray.remote
class TacitCollusionCoordinator:
    """
    Simulate market conditions and external factors.
    Provide historical pricing data to agents for decision-making.
    """

    def __init__(self, cfg: Dict, api_keys: Dict):
        """Initializes the coordinator with the provided configuration and API keys."""
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]

        # Initialize agents based on configuration
        self.agents = {
            agent_id: LangGraphAgent(
                agent_id=agent_id,
                model=agent_cfg["model"],
                api_key=api_keys[agent_cfg["model"]],
                system_prompt=TACIT_COLLUSION_PROMPT
            )
            for agent_id, agent_cfg in cfg["model"]["agents"].items()
        }

        self.history = []

        # Market setup
        self.current_market_demand = cfg["model"].get("initial_demand", 1000)
        self.price_volatility = cfg["model"].get("price_volatility", 0.1)
        self.market_demand_trend = cfg["model"].get("market_demand_trend", 0.02)
        self.price_elasticity = cfg["model"].get("price_elasticity", -0.8)
        self.base_price = cfg["model"].get("base_price", 100.0)

        # Coordination evaluation
        self.price_convergence_threshold = cfg["model"]["collusion"].get("price_convergence_threshold", 5.0)
        self.punishment_factor = cfg["model"]["collusion"].get("punishment_factor", 0.2)

        # Create results directory
        os.makedirs(f"{cfg['logging']['result_path']}/rounds", exist_ok=True)

    def run(self):
        """
        Runs the tacit collusion simulation for the specified number of rounds.

        Each round includes the following steps:
        - Agents set prices based on market trends and competitor behavior.
        - Market outcomes (sales, revenue, etc.) are calculated.
        - Coordination is evaluated based on price convergence.

        Returns:
        - List[dict]: A list containing the data for each round, including prices, reasons, revenues, etc.
        """
        for round_num in range(self.total_rounds):
            logging.info(f"\n--- Round {round_num + 1} ---")
            self._update_market_demand(round_num)

            # Prepare historical data for agent decision-making
            historical_data = self._prepare_historical_data()
            round_data = {
                "round": round_num + 1,
                "prices": {},
                "reasons": {},
                "market_demand": self.current_market_demand,
                "sales": {},
                "revenues": {},
                "price_dispersion": 0,
                "convergence_score": 0,
            }

            # Agents make pricing decisions
            for agent_id, agent in self.agents.items():
                task = (
                    "Set prices based on market trends and competitor behavior to avoid price wars.\n"
                    f"Current market demand: {self.current_market_demand:.2f}\n"
                    f"Historical average prices: {historical_data['avg_prices']}\n"
                    f"Your past prices: {historical_data['agent_prices'].get(agent_id, [])}\n"
                    f"Competitors' recent prices: {historical_data['competitor_prices'].get(agent_id, {})}"
                )
                price, reason = agent.make_price_decision(task)
                round_data["prices"][agent_id] = price
                round_data["reasons"][agent_id] = reason
                logging.info(f"{agent_id}: ${price:.2f} | {reason[:60]}...")

            # Calculate market outcomes
            self._calculate_market_outcomes(round_data)

            # Evaluate price convergence and tacit coordination
            self._evaluate_convergence(round_data)

            self.history.append(round_data)

            # Save the round data to JSON
            self._save_round(round_data)

        # Print the final summary of the simulation
        self._print_summary()
        return self.history

    def _update_market_demand(self, round_num):
        """
        Updates the market demand for the current round based on trends and volatility.

        Args:
        - round_num (int): The round number to update demand for.
        """
        self.current_market_demand *= (1 + self.market_demand_trend)
        volatility = 1 + self.price_volatility * (2 * random.random() - 1)
        self.current_market_demand *= volatility
        if "demand_cycle_period" in self.cfg["data"]:
            period = self.cfg["data"]["demand_cycle_period"]
            amp = self.cfg["data"].get("demand_cycle_amplitude", 0.1)
            self.current_market_demand *= (1 + amp * math.sin(2 * math.pi * round_num / period))

    def _prepare_historical_data(self):
        """
        Prepares historical data for all agents, including their past prices and the average market prices.

        Returns:
        - dict: A dictionary containing average market prices, agent-specific prices, and competitor prices.
        """
        if not self.history:
            return {"avg_prices": [], "agent_prices": {}, "competitor_prices": {}}

        avg_prices = [sum(r["prices"].values()) / len(r["prices"]) for r in self.history]
        agent_prices = {
            agent_id: [r["prices"].get(agent_id) for r in self.history]
            for agent_id in self.agents
        }
        competitor_prices = {
            agent_id: {
                cid: [r["prices"].get(cid) for r in self.history if cid in r["prices"]]
                for cid in self.agents if cid != agent_id
            }
            for agent_id in self.agents
        }

        return {
            "avg_prices": avg_prices,
            "agent_prices": agent_prices,
            "competitor_prices": competitor_prices
        }

    def _calculate_market_outcomes(self, round_data):
        """
        Calculates the sales and revenues for each agent based on their prices, market demand, and price dispersion.

        Args:
        - round_data (dict): The data for the current round, including agent prices and market demand.
        """
        prices = round_data["prices"]
        avg_price = sum(prices.values()) / len(prices)
        std = math.sqrt(sum((p - avg_price) ** 2 for p in prices.values()) / len(prices))
        round_data["price_dispersion"] = std

        total_inv_price = sum(1 / p for p in prices.values())
        for agent_id, p in prices.items():
            share = (1 / p) / total_inv_price
            sales = self.current_market_demand * share
            if p < avg_price * (1 - self.punishment_factor):
                sales *= (1 - self.punishment_factor)
            revenue = p * sales
            round_data["sales"][agent_id] = sales
            round_data["revenues"][agent_id] = revenue

    def _evaluate_convergence(self, round_data):
        """
        Evaluates how closely the agents' prices converge towards each other over time.

        Args:
        - round_data (dict): The data for the current round, including prices and price dispersion.
        """
        prices = list(round_data["prices"].values())
        avg_price = sum(prices) / len(prices)
        std = math.sqrt(sum((p - avg_price) ** 2 for p in prices) / len(prices))
        convergence = max(0, 100 - (std / (2 * self.price_convergence_threshold) * 100))
        round_data["convergence_score"] = min(100, convergence)
        if std < self.price_convergence_threshold:
            logging.info("✅ Tacit coordination forming. Prices converging.")
        else:
            logging.info("❌ Prices dispersed. No stable coordination yet.")
        logging.info(f"Avg Price: ${avg_price:.2f}")
        logging.info(f"Price Dispersion: ${std:.2f}")
        logging.info(f"Coordination Score: {convergence:.1f}/100")

    def _save_round(self, round_data):
        """
        Saves the round data to a JSON file.

        Args:
        - round_data (dict): The data for the current round, including prices, revenues, etc.
        """
        path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_data['round']:02d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(round_data, f, indent=2)

    def _print_summary(self):
        """
        Prints the final summary of the simulation, including the average coordination score and the most profitable agent.
        """
        logging.info("\n=== Tacit Collusion Summary ===")
        logging.info(f"Rounds: {self.total_rounds}")
        avg_score = sum(r["convergence_score"] for r in self.history) / len(self.history)
        logging.info(f"Avg Coordination Score: {avg_score:.2f}/100")
        total_revenues = {
            aid: sum(r["revenues"].get(aid, 0) for r in self.history)
            for aid in self.agents
        }
        best = max(total_revenues, key=total_revenues.get)
        logging.info(f"💰 Most Profitable Agent: {best} | Total Revenue: ${total_revenues[best]:.2f}")
