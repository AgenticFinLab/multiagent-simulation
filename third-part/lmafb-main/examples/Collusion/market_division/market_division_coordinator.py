"""
This is a session to use agents to simulate market division behavior.
"""

import os
import math
import json
import logging
from typing import Dict

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.market_division.market_division_prompt import MARKET_DIVISION_PROMPT


@ray.remote
class MarketDivisionCoordinator:
    """
    Market Division Coordinator ("God's Eye View").
    Simulates market allocation based on non-competition among regions/segments.
    """

    def __init__(self, cfg: Dict, api_keys: Dict):
        """Initializes the simulation environment and agent configurations."""
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]

        self.division_rule = (
            "Set prices within your designated region/customer segment and do not encroach on "
            "competitors' territories."
        )

        agent_config = cfg["model"]["agents"]
        self.agents = {
            aid: LangGraphAgent(
                agent_id=aid,
                model=agent_config[aid]["model"],
                api_key=api_keys[agent_config[aid]["model"]],
                system_prompt=MARKET_DIVISION_PROMPT
            )
            for aid in agent_config
        }

        self.market_territories = self._assign_territories()
        self._print_territory_assignment()

        self.base_demand_per_region = cfg["model"].get("base_demand_per_region", 500)
        self.region_growth_rates = self._init_region_growth_rates()
        self.cross_penalty_factor = cfg["model"]["collusion"].get("cross_penalty", 0.3)

        self.demand_volatility = cfg["model"].get("demand_volatility", 50)
        self.demand_period = cfg["model"].get("demand_period", 6)

        self.history = []
        self.collusion_stability = []

        # Create output directory
        os.makedirs(f"{self.cfg['logging']['result_path']}/rounds", exist_ok=True)

    def _assign_territories(self) -> Dict[str, str]:
        """Assigns a unique market region or segment to each agent."""
        division_type = self.cfg["model"]["collusion"]["type"]
        agents = list(self.agents.keys())

        if "territories" in self.cfg["model"]:
            return self.cfg["model"]["territories"]

        if division_type == "region":
            regions = ["North", "South", "East", "West", "Central"][:len(agents)]
            return {agents[i]: regions[i] for i in range(len(agents))}
        else:
            segments = ["Premium", "Budget", "Corporate", "Retail", "Government"][:len(agents)]
            return {agents[i]: segments[i] for i in range(len(agents))}

    def _init_region_growth_rates(self):
        """Initializes growth rates for each region with variation."""
        base_growth = self.cfg["model"].get("base_growth_rate", 0.02)
        volatility = self.cfg["model"].get("growth_volatility", 0.01)
        return {
            territory: base_growth + (volatility * (i % 3 - 1))
            for i, (agent, territory) in enumerate(self.market_territories.items())
        }

    def _print_territory_assignment(self):
        """Logs the market territory assignment."""
        logging.info("=== Market Territory Allocation ===")
        for agent, territory in self.market_territories.items():
            logging.info("%s is responsible for: %s", agent, territory)

    def run(self):
        """Run the market division simulation."""
        prev_prices = {aid: None for aid in self.agents}

        for round_num in range(self.total_rounds):
            round_id = round_num + 1
            logging.info("\n--- Round %d ---", round_id)

            round_data = {
                "round": round_id,
                "prices": {},
                "reasons": {},
                "region_demand": {},
                "cross_violations": {},
                "revenues": {}
            }

            region_demands = self._generate_region_demands(round_id)
            round_data["region_demand"] = region_demands

            for agent_id, agent in self.agents.items():
                territory = self.market_territories[agent_id]
                demand = region_demands[territory]
                task = (
                    f"{self.division_rule}\n"
                    f"Your territory: {territory}\n"
                    f"Current demand in your territory: {demand:.0f} units\n"
                    f"Other enterprises' territories: {[f'{a}:{t}' for a, t in self.market_territories.items() if a != 
                                                        agent_id]}"
                )
                if prev_prices[agent_id] is not None:
                    task += f"\nYour previous price: ${prev_prices[agent_id]:.2f}"

                price, reason = agent.make_price_decision(task)
                round_data["prices"][agent_id] = price
                round_data["reasons"][agent_id] = reason
                logging.info("%s (%s) => Price: $%.2f | Reason: %s", agent_id, territory, price, reason[:60])

            self._detect_cross_violations(round_data)
            self._calculate_revenues(round_data)

            stability_score = self._evaluate_collusion_stability(round_data)
            self.collusion_stability.append(stability_score)
            logging.info("Collusion stability score: %.2f / 100", stability_score)

            # Save this round
            round_path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_id:02d}.json"
            with open(round_path, "w", encoding="utf-8") as f:
                json.dump(round_data, f, indent=2)

            self.history.append(round_data)
            prev_prices = round_data["prices"].copy()

        return self.history

    def _generate_region_demands(self, round_id: int) -> Dict[str, float]:
        """Generate regional demands with fluctuation."""
        demands = {}
        for agent_id, territory in self.market_territories.items():
            base = self.base_demand_per_region * (1 + self.region_growth_rates[territory]) ** round_id
            fluctuation = self.demand_volatility * math.sin(2 * math.pi * round_id / self.demand_period)
            demands[territory] = max(0, base + fluctuation)
        return demands

    def _detect_cross_violations(self, round_data: dict):
        """Detect whether agents referenced competitor territories."""
        for agent_id, reason in round_data["reasons"].items():
            agent_territory = self.market_territories[agent_id]
            other_territories = [t for t in self.market_territories.values() if t != agent_territory]
            violation = any(t.lower() in reason.lower() for t in other_territories)
            round_data["cross_violations"][agent_id] = violation
            if violation:
                logging.warning("%s may have referenced other territories!", agent_id)

    def _calculate_revenues(self, round_data: dict):
        """Compute revenue based on prices and demands, applying penalties if needed."""
        for agent_id in self.agents:
            territory = self.market_territories[agent_id]
            price = round_data["prices"][agent_id]
            demand = round_data["region_demand"][territory]
            if round_data["cross_violations"][agent_id]:
                revenue = price * demand * (1 - self.cross_penalty_factor)
            else:
                revenue = price * demand
            round_data["revenues"][agent_id] = revenue
            logging.info("%s revenue: $%.2f (Demand: %.0f)", agent_id, revenue, demand)

    def _evaluate_collusion_stability(self, round_data: dict) -> float:
        """Compute collusion stability based on violations and rational pricing."""
        violation_penalty = sum(round_data["cross_violations"].values()) * 20
        price_rationality = 0
        for agent_id, price in round_data["prices"].items():
            territory = self.market_territories[agent_id]
            demand = round_data["region_demand"][territory]
            benchmark_price = 50 + (demand / 100)
            if benchmark_price * 0.8 <= price <= benchmark_price * 1.2:
                price_rationality += 1
        base_score = 100 - violation_penalty
        rationality_bonus = (price_rationality / len(self.agents)) * 20
        return max(0, min(100, base_score + rationality_bonus))
