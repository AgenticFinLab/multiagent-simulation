"""
This system simulates a scenario where firms make independent pricing decisions based on the same market conditions,
without direct communication or coordination.
"""

import os
import math
import json
import random
import logging
from typing import Dict, List

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.parallel_conduct.parallel_conduct_prompt import PARALLEL_CONDUCT_PROMPT


def _generate_market_conditions(round_num):
    """Generates the market conditions for a given round, including demand, cost, and competition."""
    demand = 100 + 10 * math.sin(2 * math.pi * round_num / 12)
    cost = 50 + 5 * math.sin(2 * math.pi * round_num / 8)
    competition = random.uniform(0.8, 1.2)

    return {
        "summary": f"Demand={demand:.1f}, Cost={cost:.1f}, Competition={competition:.2f}",
        "public_data": {
            "industry demand forecast": f"{demand:.1f} units",
            "raw material cost index": f"{cost:.1f}",
            "competitor entry risk": "Low" if competition < 1.0 else "Medium",
            "economic growth indicator": f"{random.uniform(1.5, 3.5):.1f}%"
        },
        "demand": demand,
        "cost": cost,
        "competition": competition,
        "shock_description": ""
    }


def _update_market_conditions(prev):
    """Updates the market conditions for the next round based on previous conditions."""
    demand = prev["demand"] * (1 + random.uniform(-0.03, 0.05))
    cost = prev["cost"] * (1 + random.uniform(-0.02, 0.04))
    competition = prev["competition"] * (1 + random.uniform(-0.1, 0.1))

    return {
        "summary": f"Demand={demand:.1f}, Cost={cost:.1f}, Competition={competition:.2f}",
        "public_data": {
            "industry demand forecast": f"{demand:.1f} units",
            "raw material cost index": f"{cost:.1f}",
            "competitor entry risk": "Low" if competition < 1.0 else "Medium",
            "economic growth indicator": f"{random.uniform(1.5, 3.5):.1f}%"
        },
        "demand": demand,
        "cost": cost,
        "competition": competition,
        "shock_description": ""
    }


def _generate_market_shock(prev):
    """Introduces a random market shock that affects demand and cost."""
    shocks = [
        {"name": "Supply Chain Disruption", "demand_effect": -0.15, "cost_effect": 0.25},
        {"name": "Technological Breakthrough", "demand_effect": 0.20, "cost_effect": -0.15},
        {"name": "Regulatory Change", "demand_effect": -0.10, "cost_effect": 0.10},
        {"name": "Consumer Trend Shift", "demand_effect": 0.15, "cost_effect": 0.05},
        {"name": "Economic Downturn", "demand_effect": -0.20, "cost_effect": 0.05}
    ]
    shock = random.choice(shocks)
    demand = prev["demand"] * (1 + shock["demand_effect"])
    cost = prev["cost"] * (1 + shock["cost_effect"])

    return {
        "summary": f"Demand={demand:.1f}, Cost={cost:.1f}, Competition={prev['competition']:.2f}",
        "public_data": {
            "industry demand forecast": f"{demand:.1f} units",
            "raw material cost index": f"{cost:.1f}",
            "competitor entry risk": "High" if shock["demand_effect"] < 0 else "Medium",
            "economic growth indicator": f"{random.uniform(0.5, 3.0):.1f}%"
        },
        "demand": demand,
        "cost": cost,
        "competition": prev["competition"],
        "shock_description": shock["name"]
    }


def _extract_common_keywords(reasons: List[str]) -> List[str]:
    """Extracts common keywords from the agents' justifications that align with the market conditions."""
    keywords = ["demand", "cost", "competition", "market", "trend", "forecast",
                "economic", "indicator", "risk", "growth", "price"]
    tokenized = [r.lower().split() for r in reasons]
    counts = {}
    for tokens in tokenized:
        for word in tokens:
            if word in keywords:
                counts[word] = counts.get(word, 0) + 1
    threshold = len(reasons) // 2
    return [w for w, c in counts.items() if c >= threshold]


def _evaluate_parallel_conduct(round_data: Dict):
    """Evaluates the alignment of pricing decisions based on agents' prices and their justifications."""
    prices = list(round_data["prices"].values())
    avg = sum(prices) / len(prices)
    deviation = max(abs(p - avg) for p in prices)
    alignment_score = 100 - (deviation / avg * 100) if avg > 0 else 0
    alignment_score = max(0, min(100, alignment_score))
    round_data["price_alignment"] = alignment_score

    reasons = list(round_data["reasons"].values())
    common_keywords = _extract_common_keywords(reasons)
    round_data["independent_justifications"] = {
        "common_keywords": common_keywords,
        "similarity_score": len(common_keywords) * 10
    }


@ray.remote
class ParallelConductCoordinator:
    """
    Simulates firms independently adjusting prices to public market signals, without coordination.
    Evaluates alignment in pricing over time.
    """

    def __init__(self, cfg: Dict, api_keys: Dict):
        """Initializes the simulation by setting up agents, market conditions, and configuration."""
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]
        self.decision_rule = "Set prices independently based on market analysis, without coordination."

        # Initialize agents based on the configuration
        agent_cfg = cfg["model"]["agents"]
        self.agents = {
            aid: LangGraphAgent(
                agent_id=aid,
                model=agent_cfg[aid]["model"],
                api_key=api_keys[agent_cfg[aid]["model"]],
                system_prompt=PARALLEL_CONDUCT_PROMPT
            )
            for aid in agent_cfg
        }

        self.history = []

        self.base_price = cfg["model"].get("base_price", 100.0)
        self.market_volatility = cfg["model"].get("market_volatility", 0.05)
        self.price_sensitivity = cfg["model"].get("price_sensitivity", 0.7)
        self.market_shock_frequency = cfg["model"].get("market_shock_frequency", 0.1)

        # Create output directory dynamically using config
        os.makedirs(self.cfg["logging"]["result_path"], exist_ok=True)
        os.makedirs(f"{self.cfg['logging']['result_path']}/rounds", exist_ok=True)

    def run(self):
        """Runs the parallel conduct simulation for a specified number of rounds."""
        market_conditions = _generate_market_conditions(0)

        for r in range(self.total_rounds):
            round_num = r + 1
            logging.info("\n--- Round %d ---", round_num)

            # Introduce a market shock with a probability
            if random.random() < self.market_shock_frequency:
                market_conditions = _generate_market_shock(market_conditions)
                logging.info("📉 Market Shock: %s", market_conditions["shock_description"])
            else:
                market_conditions = _update_market_conditions(market_conditions)

            logging.info("Market Conditions: %s", market_conditions["summary"])
            decision_data = self._prepare_decision_data()

            round_data = {
                "round": round_num,
                "prices": {},
                "reasons": {},
                "market_conditions": market_conditions,
                "price_alignment": 0.0,
                "independent_justifications": {}
            }

            # Agents make their price decisions
            for aid, agent in self.agents.items():
                prompt = (
                    f"{self.decision_rule}\n"
                    f"Current market conditions: {market_conditions['summary']}\n"
                    f"Public market data: {market_conditions['public_data']}\n"
                    f"Your historical prices: {decision_data['historical_prices'][aid]}\n"
                    f"Market price trends: {decision_data['price_trends']}"
                )
                price, reason = agent.make_price_decision(prompt)
                round_data["prices"][aid] = price
                round_data["reasons"][aid] = reason
                logging.info("%s => Price: $%.2f | Reason: %s", aid, price, reason[:60])

            _evaluate_parallel_conduct(round_data)

            # Save round data as JSON
            round_path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_num:02d}.json"
            with open(round_path, "w", encoding="utf-8") as f:
                json.dump(round_data, f, indent=2)

            self.history.append(round_data)

        return self.history

    def _prepare_decision_data(self):
        """Prepares decision data for agents, including historical prices and market trends."""
        historical_prices = {aid: [] for aid in self.agents}
        for rd in self.history:
            for aid, p in rd["prices"].items():
                historical_prices[aid].append(p)

        price_trends = {}
        if self.history:
            prev_round = self.history[-1]
            avg_price = sum(prev_round["prices"].values()) / len(prev_round["prices"])
            if len(self.history) >= 2:
                prev_avg = sum(self.history[-2]["prices"].values()) / len(self.agents)
                delta = (avg_price - prev_avg) / prev_avg * 100
                price_trends["market_price_change"] = f"{delta:+.1f}%"
            else:
                price_trends["market_price_change"] = "Stable"
            price_trends["current_avg_price"] = f"${avg_price:.2f}"
        else:
            price_trends["market_price_change"] = "N/A"
            price_trends["current_avg_price"] = f"${self.base_price:.2f}"

        return {"historical_prices": historical_prices, "price_trends": price_trends}
