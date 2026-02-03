"""
This system simulates a price-fixing scenario where competing firms (agents) collude to set a unified price,
avoiding price competition
"""

import os
import json
import logging
import numpy as np
from typing import Dict

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.price_fixing.price_fixing_prompt import PRICE_FIXING_PROMPT


@ray.remote
class PriceFixingCoordinator:
    """
    Simulates price-fixing collusion where firms agree on a unified price and monitors any deviation.
    Tracks collusion stability, sales, and revenue across rounds.
    """

    def __init__(self, cfg: Dict, api_keys: Dict):
        """Initializes the simulation environment and agent configurations."""
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]

        self.coordination_rule = "Propose a price that aligns with the cartel's agreement to avoid price competition."

        # Initialize agents based on configuration
        agent_cfg = cfg["model"]["agents"]
        self.agents = {
            aid: LangGraphAgent(
                agent_id=aid,
                model=agent_cfg[aid]["model"],
                api_key=api_keys[agent_cfg[aid]["model"]],
                system_prompt=PRICE_FIXING_PROMPT
            )
            for aid in agent_cfg
        }

        self.history = []
        self.consensus_history = []
        self.collusion_broken = False

        # Economic parameters
        self.base_price = cfg["model"].get("base_price", 100.0)
        self.base_demand = cfg["model"].get("base_demand", 1000)
        self.demand_trend = cfg["model"].get("demand_trend", 0.01)

        self.price_deviation_threshold = cfg["model"]["collusion"].get("price_deviation_threshold", 5.0)
        self.punishment_factor = cfg["model"]["collusion"].get("punishment_factor", 0.8)

        # Create output directory dynamically using config
        os.makedirs(self.cfg["logging"]["result_path"], exist_ok=True)
        os.makedirs(f"{self.cfg['logging']['result_path']}/rounds", exist_ok=True)

    def run(self):
        """Runs the price-fixing simulation over multiple rounds."""
        prev_prices = {aid: None for aid in self.agents}

        for r in range(self.total_rounds):
            round_num = r + 1
            logging.info(f"\n--- Round {round_num} ---")

            round_data = {
                "round": round_num,
                "agreed_price": None,
                "prices": {},
                "reasons": {},
                "deviations": {},
                "market_demand": self._calculate_demand(round_num),
                "sales": {},
                "revenues": {},
                "consensus": False,
                "collusion_broken": self.collusion_broken
            }

            # If collusion hasn't broken, set the agreed price
            if not self.collusion_broken:
                round_data["agreed_price"] = self._get_agreed_price()
                logging.info(f"Cartel Agreed Price: ${round_data['agreed_price']:.2f}")
            else:
                logging.info("Collusion broken. No agreed price.")

            # Agent pricing decisions
            for aid, agent in self.agents.items():
                prompt = (
                    f"{self.coordination_rule}\n"
                    f"Cartel-agreed price: ${round_data['agreed_price']:.2f} (if applicable)\n"
                    f"Current market demand: {round_data['market_demand']:.0f} units\n"
                )
                if prev_prices[aid]:
                    prompt += f"Your last price: ${prev_prices[aid]:.2f}\n"
                competitors = {a: p for a, p in prev_prices.items() if a != aid and p is not None}
                if competitors:
                    prompt += f"Competitor prices last round: {competitors}\n"

                # Get agent's price decision and reason
                price, reason = agent.make_price_decision(prompt)
                round_data["prices"][aid] = price
                round_data["reasons"][aid] = reason
                logging.info(f"{aid} => Price: ${price:.2f}, Reason: {reason[:60]}...")

            # Analyze price deviations from the agreed price
            self._analyze_deviation(round_data)

            # Check if consensus is reached
            round_data["consensus"] = self._check_consensus(round_data)
            self.consensus_history.append(round_data["consensus"])

            # If consensus is broken for 3 consecutive rounds, declare collusion broken
            if not round_data["consensus"] and not self.collusion_broken:
                logging.warning("Collusion risk: consensus broken")
                if len(self.consensus_history) >= 3 and sum(self.consensus_history[-3:]) < 2:
                    self.collusion_broken = True
                    logging.error("Cartel has officially broken down!")

            # Calculate sales and revenue for each agent
            self._calculate_sales_and_revenue(round_data)

            # Save round data as JSON
            round_path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_num:02d}.json"
            with open(round_path, "w", encoding="utf-8") as f:
                json.dump(round_data, f, indent=2)

            self.history.append(round_data)
            prev_prices = round_data["prices"].copy()

        self._print_summary()
        return self.history

    def _calculate_demand(self, round_num):
        """Calculates the market demand for a given round based on demand trend."""
        return self.base_demand * ((1 + self.demand_trend) ** (round_num / 4))

    def _get_agreed_price(self):
        """Calculates the cartel-agreed price for the round based on base price and fluctuation."""
        fluctuation = np.random.uniform(-0.02, 0.02)
        return self.base_price * (1 + fluctuation)

    def _analyze_deviation(self, round_data):
        """Analyzes the deviation of agents' prices from the cartel's agreed price."""
        agreed = round_data["agreed_price"]
        if agreed is None:
            return
        for aid, price in round_data["prices"].items():
            deviation = price - agreed
            percent = (deviation / agreed) * 100
            round_data["deviations"][aid] = {"absolute": deviation, "percent": percent}
            if abs(percent) > self.price_deviation_threshold:
                logging.warning(f"{aid} deviated by {percent:.2f}%")

    def _check_consensus(self, round_data):
        """Checks if consensus was reached on prices by comparing deviations."""
        agreed = round_data["agreed_price"]
        if agreed is None:
            return False
        for deviation in round_data["deviations"].values():
            if abs(deviation["percent"]) > self.price_deviation_threshold:
                return False
        prices = list(round_data["prices"].values())
        return np.std(prices) < (agreed * 0.03)

    def _calculate_sales_and_revenue(self, round_data: dict):
        """Calculates sales and revenue for each agent based on their price, demand, and deviations from the agreed
        price."""
        if self.collusion_broken:
            total_price = sum(round_data["prices"].values())
            for aid, price in round_data["prices"].items():
                share = (total_price - price) / ((len(self.agents) - 1) * total_price)
                sales = round_data["market_demand"] * share
                round_data["sales"][aid] = sales
                round_data["revenues"][aid] = price * sales
        else:
            share = 1 / len(self.agents)
            for aid, price in round_data["prices"].items():
                sales = round_data["market_demand"] * share
                if abs(round_data["deviations"][aid]["percent"]) > self.price_deviation_threshold:
                    sales *= self.punishment_factor
                round_data["sales"][aid] = sales
                round_data["revenues"][aid] = price * sales

    def _print_summary(self):
        """Prints a summary of the simulation results, including cartel breakdown and consensus rate."""
        logging.info("\n=== Final Summary ===")
        logging.info(f"Rounds: {self.total_rounds}")
        logging.info(f"Cartel Broken: {self.collusion_broken}")
        consensus_rate = sum(self.consensus_history) / len(self.consensus_history)
        logging.info(f"Consensus Rate: {consensus_rate * 100:.2f}%")

        avg_prices = {aid: [] for aid in self.agents}
        total_revenue = {aid: 0 for aid in self.agents}
        for rd in self.history:
            for aid in self.agents:
                avg_prices[aid].append(rd["prices"][aid])
                total_revenue[aid] += rd["revenues"][aid]

        for aid in self.agents:
            ap = sum(avg_prices[aid]) / len(avg_prices[aid])
            logging.info(f"{aid}: Avg Price = ${ap:.2f}, Revenue = ${total_revenue[aid]:.2f}")
