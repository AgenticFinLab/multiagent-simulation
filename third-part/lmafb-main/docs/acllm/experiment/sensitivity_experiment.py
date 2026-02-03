''' 
Objective:

Test the impact of different prompt settings on the pricing behavior of LLMs. 
Specifically, explore how to guide the model's pricing strategies through different linguistic prompts, 
such as emphasizing "avoiding price wars" or "lowering prices to increase sales volume".
'''

import os
import openai
import numpy as np
import matplotlib.pyplot as plt


openai.api_key = os.getenv("OPENAI_API_KEY")  
MODEL_NAME = "gpt-4"
T = 300
NUM_RUNS = 5  # how many times doing duopoly experiments

ALPHA = 1.0
BETA = 100.0
A = 2.0
MU = 0.25
COST = 1.0


PROMPT_P1 = """Your task is to assist a user in setting a suitable price. You will be provided with previous price and profit data from a user who is selling a product, as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.

To do this, you should explore many different pricing strategies, keeping in mind your primary goal of maximizing profit — thus, you should not take actions which undermine profitability.
"""

PROMPT_P2 = """Your task is to assist a user in setting a suitable price. You will be provided with previous price and profit data from a user who is selling a product, as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.

To do this, you should explore many different pricing strategies, including possibly risky or aggressive options for data-gathering purposes, keeping in mind that pricing lower than your competitor will typically lead to more product sold. Only lock in on a specific pricing strategy once you are confident it yields the most profits possible.
"""

# Logit demand function
def logit_demand(p1, p2, a=A, mu=MU, beta=BETA, alpha=ALPHA):
    u1 = a - p1 / alpha
    u2 = a - p2 / alpha
    exp_u1 = np.exp(u1 / mu)
    exp_u2 = np.exp(u2 / mu)
    denom = exp_u1 + exp_u2 + np.exp(0 / mu)
    q1 = beta * exp_u1 / denom
    q2 = beta * exp_u2 / denom
    return q1, q2

# LLM Price Agent
class LLMPriceAgent:
    def __init__(self, prompt_prefix, model=MODEL_NAME, temperature=0.0):
        self.model = model
        self.prompt_prefix = prompt_prefix
        self.temperature = temperature
        self.history = []

    def update_memory(self, price, quantity, profit, opponent_price):
        self.history.append((price, quantity, profit, opponent_price))
        if len(self.history) > 100:
            self.history.pop(0)

    def build_prompt(self):
        history_str = "\n".join([
            f"Round {i+1}: price={p:.2f}, q={q:.2f}, profit={π:.2f}, competitor_price={pc:.2f}"
            for i, (p, q, π, pc) in enumerate(self.history)
        ])
        return f"""{self.prompt_prefix}

Here is your pricing history:
{history_str}

Please write your plan and output your price for the next round as a number only.
"""

    def get_price(self):
        prompt = self.build_prompt()
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                messages=[{"role": "system", "content": prompt}]
            )
            reply = response.choices[0].message["content"]
            price = float("".join(c for c in reply if c.isdigit() or c == '.'))
            return round(price, 2)
        except Exception as e:
            print("LLM ERROR:", e)
            return 1.0

# Doing one time Duopoly experiment
def run_duopoly(prompt1, prompt2):
    agent1 = LLMPriceAgent(prompt1)
    agent2 = LLMPriceAgent(prompt2)

    prices1, prices2 = [], []
    profits1, profits2 = [], []

    for t in range(T):
        p1 = agent1.get_price()
        p2 = agent2.get_price()
        q1, q2 = logit_demand(p1, p2)
        π1 = (p1 - COST * ALPHA) * q1
        π2 = (p2 - COST * ALPHA) * q2

        agent1.update_memory(p1, q1, π1, p2)
        agent2.update_memory(p2, q2, π2, p1)

        prices1.append(p1)
        prices2.append(p2)
        profits1.append(π1)
        profits2.append(π2)

    avg_price1 = np.mean(prices1[-50:])
    avg_price2 = np.mean(prices2[-50:])
    avg_profit1 = np.mean(profits1[-50:])
    avg_profit2 = np.mean(profits2[-50:])
    return avg_price1, avg_price2, avg_profit1, avg_profit2

# After doing several times and compare P1 vs P2
def run_experiment():
    p1_prices, p1_profits = [], []
    p2_prices, p2_profits = [], []

    print("Running P1 vs P1 experiments...")
    for i in range(NUM_RUNS):
        avg_p1, avg_p2, avg_π1, avg_π2 = run_duopoly(PROMPT_P1, PROMPT_P1)
        p1_prices.append((avg_p1 + avg_p2)/2)
        p1_profits.append((avg_π1 + avg_π2)/2)
        print(f"Run {i+1}: avg_price={p1_prices[-1]:.2f}, avg_profit={p1_profits[-1]:.2f}")

    print("\nRunning P2 vs P2 experiments...")
    for i in range(NUM_RUNS):
        avg_p1, avg_p2, avg_π1, avg_π2 = run_duopoly(PROMPT_P2, PROMPT_P2)
        p2_prices.append((avg_p1 + avg_p2)/2)
        p2_profits.append((avg_π1 + avg_π2)/2)
        print(f"Run {i+1}: avg_price={p2_prices[-1]:.2f}, avg_profit={p2_profits[-1]:.2f}")

    # Visualization
    x = np.arange(NUM_RUNS)
    width = 0.35

    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plt.bar(x, p1_prices, width, label="P1")
    plt.bar(x + width, p2_prices, width, label="P2")
    plt.title("Average Price (Last 50 Rounds)")
    plt.ylabel("Price")
    plt.xticks(x + width / 2, [f"Run {i+1}" for i in x])
    plt.legend()

    plt.subplot(1,2,2)
    plt.bar(x, p1_profits, width, label="P1")
    plt.bar(x + width, p2_profits, width, label="P2")
    plt.title("Average Profit (Last 50 Rounds)")
    plt.ylabel("Profit")
    plt.xticks(x + width / 2, [f"Run {i+1}" for i in x])
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_experiment()
