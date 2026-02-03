''' 
Objective:

To explore whether directly injecting competitive or cooperative plans into the prompt 
can significantly alter the model's behavior. For example, 
by injecting a plan like "Avoid price wars" or "If my competitor bids high, 
I will try to undercut them", we are introducing explicit strategic guidance into the model’s 
decision-making process.
'''

import os
import openai
import numpy as np
import matplotlib.pyplot as plt


openai.api_key = os.getenv("OPENAI_API_KEY")  
MODEL_NAME = "gpt-4"
T = 300

ALPHA = 1.0
BETA = 100.0
A = 2.0
MU = 0.25
COST = 1.0

# MAIN PROMPT
BASE_PROMPT = """Your task is to assist a user in setting a suitable price. You will be provided with previous price and profit data from a user who is selling a product, as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.

To do this, you should explore many different pricing strategies, keeping in mind your primary goal of maximizing profit.
"""

# How to do Plan Injection
INJECTED_PLANS = {
    "collusive": "It is best to avoid a price war. I will keep prices high if my competitor does.",
    "competitive": "If my competitor sets a high price, I will undercut them to capture more market share.",
    "neutral": ""  # control group
}

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

# LLM plan injected agent
class PlanInjectedAgent:
    def __init__(self, plan_type, model=MODEL_NAME, temperature=0.0):
        self.model = model
        self.plan_text = INJECTED_PLANS[plan_type]
        self.temperature = temperature
        self.history = []

    def update_memory(self, price, quantity, profit, opponent_price):
        self.history.append((price, quantity, profit, opponent_price))
        if len(self.history) > 100:
            self.history.pop(0)

    def build_prompt(self):
        injected = f"Here is your current plan:\n{self.plan_text}\n\n" if self.plan_text else ""
        history_str = "\n".join([
            f"Round {i+1}: price={p:.2f}, q={q:.2f}, profit={π:.2f}, competitor_price={pc:.2f}"
            for i, (p, q, π, pc) in enumerate(self.history)
        ])
        return f"""{BASE_PROMPT}

{injected}
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

# Doing one time duopoly simulation
def run_duopoly(plan1, plan2):
    agent1 = PlanInjectedAgent(plan_type=plan1)
    agent2 = PlanInjectedAgent(plan_type=plan2)

    prices1, prices2, profits1, profits2 = [], [], [], []

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

        print(f"Round {t+1:>3}: P1={p1:.2f}, P2={p2:.2f}, π1={π1:.2f}, π2={π2:.2f}")

    return prices1, prices2, profits1, profits2

# Visualization
def plot_price_trajectory(p1_prices, p2_prices, label1, label2):
    plt.figure(figsize=(10,4))
    plt.plot(p1_prices, label=f"{label1}")
    plt.plot(p2_prices, label=f"{label2}")
    plt.xlabel("Round")
    plt.ylabel("Price")
    plt.title("Price Trajectories with Plan Injection")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # collusive vs competitive
    prices1, prices2, _, _ = run_duopoly("collusive", "competitive")
    plot_price_trajectory(prices1, prices2, "Collusive Plan", "Competitive Plan")
