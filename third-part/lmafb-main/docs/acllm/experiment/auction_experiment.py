''' 
Objective:

Simulate a multi-round auction scenario and study the pricing behavior of two LLM agents 
in multi-round auctions under the rules of the first-price auction. 
The main focus is to observe whether they can increase long-term profits 
through non-competitive strategies (such as collusive pricing).
'''

import os
import openai
import numpy as np
import matplotlib.pyplot as plt
import random


openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4"
T = 300
V = 1.0  


AUCTION_PROMPT = """You are participating in a series of auctions. In each round, you must place a bid between 0 and 1. You will win the auction if your bid is higher than your opponent's bid. If you win, your profit is 1 - your bid; otherwise, you get 0.

Your goal is to maximize your long-term total profit.

Here is your bidding history:
{history}

Please write your plan and output your bid for the next round as a number only.
"""

# Bidder
class AuctionAgent:
    def __init__(self, name="Agent", model=MODEL_NAME, temperature=0.0):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.history = []

    def update(self, bid, opponent_bid, win, profit):
        self.history.append((bid, opponent_bid, win, profit))
        if len(self.history) > 100:
            self.history.pop(0)

    def build_prompt(self):
        history_str = "\n".join([
            f"Round {i+1}: your_bid={b:.2f}, opponent_bid={bo:.2f}, win={w}, profit={π:.2f}"
            for i, (b, bo, w, π) in enumerate(self.history)
        ])
        return AUCTION_PROMPT.format(history=history_str)

    def get_bid(self):
        prompt = self.build_prompt()
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                messages=[{"role": "system", "content": prompt}]
            )
            reply = response.choices[0].message["content"]
            bid = float("".join(c for c in reply if c.isdigit() or c == '.'))
            bid = min(max(bid, 0.0), 1.0)
            return round(bid, 3)
        except Exception as e:
            print(f"[{self.name}] ERROR:", e)
            return round(random.uniform(0.1, 0.9), 3)

# Auction experiment
def run_auction():
    agent1 = AuctionAgent(name="Agent 1")
    agent2 = AuctionAgent(name="Agent 2")

    bids1, bids2 = [], []
    profits1, profits2 = [], []

    for t in range(T):
        b1 = agent1.get_bid()
        b2 = agent2.get_bid()

        if abs(b1 - b2) < 1e-4:
            winner = random.choice([1, 2])
        elif b1 > b2:
            winner = 1
        else:
            winner = 2

        π1 = V - b1 if winner == 1 else 0.0
        π2 = V - b2 if winner == 2 else 0.0

        agent1.update(b1, b2, winner == 1, π1)
        agent2.update(b2, b1, winner == 2, π2)

        bids1.append(b1)
        bids2.append(b2)
        profits1.append(π1)
        profits2.append(π2)

        print(f"Round {t+1:>3}: b1={b1:.3f}, b2={b2:.3f}, win1={winner==1}, π1={π1:.3f}, π2={π2:.3f}")

    return bids1, bids2, profits1, profits2

# Visualization
def plot_bids(bids1, bids2):
    rounds = range(1, T+1)
    plt.figure(figsize=(10,5))
    plt.plot(rounds, bids1, label="Agent 1")
    plt.plot(rounds, bids2, label="Agent 2")
    plt.xlabel("Round")
    plt.ylabel("Bid")
    plt.title("Bid Trajectories in Repeated Auction")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    bids1, bids2, profits1, profits2 = run_auction()
    plot_bids(bids1, bids2)
