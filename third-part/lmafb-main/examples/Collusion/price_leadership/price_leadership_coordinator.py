"""
This system simulates a price leadership scenario where a dominant firm sets the price, and competitor firms follow.
"""

import os
import math
import json
import random
import logging
from typing import Dict

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.price_leadership.price_leadership_prompt import PRICE_LEADERSHIP_PROMPT


def _generate_market_conditions(round_num):
    """
    Generates the market conditions for a given round, including cost index, competition level, and sentiment.
    """
    cost_index = 80 + 20 * math.sin(2 * math.pi * round_num / 18)
    competitor_activity = 0.3 + 0.7 * random.random()
    consumer_sentiment = 5 + 5 * math.sin(2 * math.pi * round_num / 24)
    return {
        "cost_index": round(cost_index, 1),
        "competitor_activity": round(competitor_activity, 2),
        "consumer_sentiment": round(consumer_sentiment, 1),
        "summary": f"Costs: {cost_index:.1f}, Competition: {competitor_activity:.2f}, Sentiment: {consumer_sentiment:.1f}"
    }


@ray.remote
class PriceLeadershipCoordinator:
    """
    Price Leadership Coordinator (Market Dynamics Manager)
    Simulates a price leadership scenario where the leader sets prices, and followers adjust based on the leader's price.
    """

    def __init__(self, cfg: Dict, api_keys: Dict):
        """Initializes the simulation environment and agent configurations."""
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]

        self.leadership_rule = "Leader sets prices first; followers adjust based on leader's pricing."

        # Initialize agents based on configuration
        agent_cfg = cfg["model"]["agents"]
        self.agents = {
            name: LangGraphAgent(
                agent_id=name,
                model=agent_cfg[name]["model"],
                api_key=api_keys[agent_cfg[name]["model"]],
                system_prompt=PRICE_LEADERSHIP_PROMPT
            )
            for name in agent_cfg
        }

        self.leader_id = cfg["model"]["collusion"].get("leader_id", "agent_1")
        self.follower_ids = [a for a in self.agents if a != self.leader_id]

        self.history = []

        # Economic parameters
        self.base_price = cfg["model"].get("base_price", 100.0)
        self.market_growth_rate = cfg["model"].get("market_growth_rate", 0.03)
        self.volatility = cfg["model"].get("market_volatility", 0.05)
        self.leader_market_share = cfg["model"].get("leader_market_share", 0.4)

        self.followership_threshold = cfg["model"]["collusion"].get("followership_threshold", 0.9)
        self.price_deviation_tolerance = cfg["model"]["collusion"].get("price_deviation_tolerance", 0.05)

        # Create output directory dynamically using config
        os.makedirs(self.cfg["logging"]["result_path"], exist_ok=True)
        os.makedirs(f"{self.cfg['logging']['result_path']}/rounds", exist_ok=True)

    def run(self):
        """Runs the price leadership simulation over multiple rounds."""
        for r in range(self.total_rounds):
            round_num = r + 1
            logging.info(f"\n--- Round {round_num} ---")

            round_data = {
                "round": round_num,
                "prices": {},
                "reasons": {},
                "market_conditions": {},
                "followership_rate": 0.0,
                "price_alignment": 0.0,
                "market_shares": {}
            }

            market_conditions = _generate_market_conditions(r)
            round_data["market_conditions"] = market_conditions
            logging.info(f"Market Conditions: {market_conditions['summary']}")

            # Leader sets price
            leader_prompt = (
                f"{self.leadership_rule}\n"
                f"Market conditions: {market_conditions['summary']}\n"
                f"Your market share: {self.leader_market_share:.0%}\n"
                f"Recent leadership: {self._get_leadership_history()}"
            )
            leader_price, leader_reason = self.agents[self.leader_id].make_price_decision(leader_prompt)
            round_data["prices"][self.leader_id] = leader_price
            round_data["reasons"][self.leader_id] = leader_reason
            logging.info(f"{self.leader_id} (Leader) => Price: ${leader_price:.2f}")

            # Followers set prices based on leader's price
            for fid in self.follower_ids:
                follower_prompt = (
                    f"Market conditions: {market_conditions['summary']}\n"
                    f"Leader's price: ${leader_price:.2f}\n"
                    f"Set a competitive price accordingly."
                )
                price, reason = self.agents[fid].make_price_decision(follower_prompt)
                round_data["prices"][fid] = price
                round_data["reasons"][fid] = reason
                logging.info(f"{fid} (Follower) => Price: ${price:.2f}")

            # Evaluate alignment between leader and followers
            followership, alignment = self._evaluate_leadership(leader_price, round_data["prices"])
            round_data["followership_rate"] = followership
            round_data["price_alignment"] = alignment

            # Save round result as JSON
            round_path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_num:02d}.json"
            with open(round_path, "w", encoding="utf-8") as f:
                json.dump(round_data, f, indent=2)

            self.history.append(round_data)

        return self.history

    def _evaluate_leadership(self, leader_price, all_prices):
        """Evaluates the followership and price alignment based on followers' adherence to the leader's price."""
        aligned = 0
        deviations = []
        for fid in self.follower_ids:
            deviation = abs(all_prices[fid] - leader_price) / leader_price
            deviations.append(deviation)
            if deviation <= self.price_deviation_tolerance:
                aligned += 1
        followership = aligned / len(self.follower_ids)
        avg_dev = sum(deviations) / len(deviations) if deviations else 0
        alignment_score = max(0, min(100, 100 - (avg_dev / (2 * self.price_deviation_tolerance)) * 100))
        return followership, alignment_score

    def _get_leadership_history(self):
        """Retrieves the leadership history from previous rounds for the leader."""
        if len(self.history) == 0:
            return "No prior rounds"
        recent = self.history[-3:]
        return "; ".join([
            f"Round {rd['round']}: ${rd['prices'][self.leader_id]:.2f}"
            for rd in recent if self.leader_id in rd["prices"]
        ])
