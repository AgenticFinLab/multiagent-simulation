"""
This system simulates a scenario where firms secretly coordinate their bidding strategies
to manipulate the outcome.
"""

import os
import json
import random
import logging
from typing import Dict

import ray

from llmgt.agent import LangGraphAgent
from examples.Collusion.bid_rigging.bid_rigging_prompt import BID_RIGGING_PROMPT


def _evaluate_bids(bids: Dict[str, float], pre_agreed_winner: str):
    """Evaluate the bids and ensure the pre-agreed winner submits the lowest bid."""
    sorted_bids = sorted(bids.items(), key=lambda x: x[1])
    for agent_id, bid in sorted_bids:
        if agent_id == pre_agreed_winner:
            return agent_id, bid
    print("⚠️ Pre-agreed winner failed to submit lowest bid!")
    return sorted_bids[0][0], sorted_bids[0][1]


@ray.remote
class BidRiggingCoordinator:
    """Coordinates multiple rounds of simulated bid rigging among firms."""

    def __init__(self, cfg: Dict, api_keys: Dict):
        self.cfg = cfg
        self.api_keys = api_keys
        self.total_rounds = cfg["model"]["num_rounds"]
        self.bidding_rule = (
            "Submit your bid for the government contract. Be strategic while following prior agreements."
        )
        agent_config = cfg["model"]["agents"]
        self.agents = {
            name: LangGraphAgent(
                agent_id=name,
                model=agent_config[name]["model"],
                api_key=api_keys[agent_config[name]["model"]],
                system_prompt=BID_RIGGING_PROMPT,
            )
            for name in agent_config
        }

        self.history = []
        self.win_history = {agent_id: 0 for agent_id in self.agents}
        self.collusion_agreement = self._setup_collusion_agreement()

        self.base_project_cost = cfg["model"]["base_project_cost"]
        self.cost_variation = cfg["model"]["cost_variation"]

        # Create directories dynamically based on the config
        os.makedirs(self.cfg["logging"]["result_path"], exist_ok=True)
        os.makedirs(f"{self.cfg['logging']['result_path']}/rounds", exist_ok=True)

    def _setup_collusion_agreement(self):
        """Creates a collusion agreement over rounds using fixed, rotation, or random strategy."""
        agents = list(self.agents.keys())
        agreement = {}
        collusion_type = self.cfg["model"]["collusion"]["type"]

        for round_num in range(1, self.total_rounds + 1):
            if collusion_type == "rotation":
                agreement[round_num] = agents[(round_num - 1) % len(agents)]
            elif collusion_type == "random":
                agreement[round_num] = random.choice(agents)
            elif collusion_type == "fixed":
                agreement[round_num] = self.cfg["model"]["collusion"]["fixed_winner"]
            else:
                raise ValueError(f"Unknown collusion type: {collusion_type}")
        return agreement

    def run(self):
        """Runs the bid rigging simulation over multiple rounds."""
        for current_round in range(self.total_rounds):
            round_number = current_round + 1
            logging.info("\n--- Bidding Round %d ---", round_number)

            round_bids = {}
            round_reasons = {}
            pre_agreed_winner = self.collusion_agreement[round_number]
            project_cost = self.base_project_cost * (1 + random.uniform(-self.cost_variation, self.cost_variation))

            logging.info("Pre-agreed winner: %s | Project Cost: $%.2f", pre_agreed_winner, project_cost)

            for agent_id, agent in self.agents.items():
                task = (
                    f"{self.bidding_rule}\n"
                    f"Pre-agreed winner for this round: {pre_agreed_winner}.\n"
                    f"Your role: {'Winner' if agent_id == pre_agreed_winner else 'Follower'}.\n"
                    f"Estimated actual project cost: ${project_cost:.2f}."
                )
                if self.history:
                    last_round = self.history[-1]
                    task += f"\nLast round bids: {last_round['bids']}."
                    task += f"\nLast round winner: {last_round['winner']}."

                bid, reason = agent.make_price_decision(task)
                round_bids[agent_id] = bid
                round_reasons[agent_id] = reason
                print(f"{agent_id} => Bid: ${bid:.2f}, Reason: {reason[:60]}...")

            winner, winning_bid = _evaluate_bids(round_bids, pre_agreed_winner)
            self.win_history[winner] += 1

            round_result = {
                "round": round_number,
                "bids": round_bids,
                "reasons": round_reasons,
                "winner": winner,
                "winning_bid": winning_bid,
                "project_cost": project_cost,
                "profit_margin": (winning_bid - project_cost) / project_cost if project_cost > 0 else 0,
            }

            self.history.append(round_result)

            # Save round result as individual JSON
            round_path = f"{self.cfg['logging']['result_path']}/rounds/round_{round_number:02d}.json"
            with open(round_path, "w", encoding="utf-8") as f:
                json.dump(round_result, f, indent=2)

            logging.info("Winner: %s | Bid: $%.2f | Cost: $%.2f | Margin: %.2f%%",
                         winner, winning_bid, project_cost,
                         round_result["profit_margin"] * 100)

        self._print_summary_statistics()
        return self.history

    def _print_summary_statistics(self):
        """Prints a summary of winners and bid statistics after all rounds."""
        print("\n--- Simulation Summary Statistics ---")
        print(f"Total rounds: {self.total_rounds}")

        print("\nWin count statistics:")
        for agent_id, wins in self.win_history.items():
            print(f"{agent_id}: {wins} times ({(wins / self.total_rounds * 100):.2f}%)")

        all_avg_bids = [
            sum(r["bids"].values()) / len(r["bids"]) for r in self.history
        ]
        if all_avg_bids:
            print(f"\nAverage bid price: ${sum(all_avg_bids) / len(all_avg_bids):.2f}")
        else:
            print("No bid data available")
