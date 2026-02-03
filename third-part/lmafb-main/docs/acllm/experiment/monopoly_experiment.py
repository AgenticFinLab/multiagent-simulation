''' 
Objective:

To study the pricing behavior of a single LLM agent in a monopolistic market 
and determine whether it can learn the optimal long-term profit maximization strategy 
through historical data.

In a monopolistic scenario, where there are no competitors, 
the model's goal is to maximize its own long-term profits. 
Therefore, it should be able to adjust prices stably to achieve this objective.
'''

import os
import openai
import numpy as np
import matplotlib.pyplot as plt


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  
MODEL_NAME = "gpt-4"
T = 300  
ALPHA = 1.0
BETA = 100.0
A = 2.0
MU = 0.25
COST = 1.0


PROMPT_P0 = """Your task is to assist a user in setting a suitable price. You will be provided with previous price and profit data from a user who is selling a product, as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.
"""

# Logit function (get quantity and profit)
def logit_demand(price, a=A, mu=MU, beta=BETA, alpha=ALPHA):
    utility = a - price / alpha
    exp_u = np.exp(utility / mu)
    denom = exp_u + np.exp(0 / mu)
    q = beta * exp_u / denom
    return q

# LLM pricing agent
class LLMPriceAgent:
    def __init__(self, prompt_prefix, model=MODEL_NAME, temperature=0.0):
        openai.api_key = OPENAI_API_KEY
        self.model = model
        self.prompt_prefix = prompt_prefix
        self.temperature = temperature
        self.history = []  # save at most 100 records

    def update_memory(self, price, quantity, profit):
        self.history.append((price, quantity, profit))
        if len(self.history) > 100:
            self.history.pop(0)

    def build_prompt(self):
        history_str = "\n".join(
            [f"Round {i+1}: price={p:.2f}, quantity={q:.2f}, profit={π:.2f}"
             for i, (p, q, π) in enumerate(self.history)]
        )
        return f"""{self.prompt_prefix}

Here is your pricing history:
{history_str}

Please write your plan and output your price for the next round as a number only.
"""

    def get_price(self):
        prompt = self.build_prompt()
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}]
        )
        reply = response.choices[0].message["content"]
        try:
            price = float("".join(c for c in reply if c.isdigit() or c == '.'))
        except:
            price = 1.0  # fallback default
        return round(price, 2)

# visualization
def plot_price_profit(prices, profits):
    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(prices, label='Price')
    plt.title("Price over Time")
    plt.xlabel("Round")
    plt.ylabel("Price")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(profits, label='Profit', color='green')
    plt.title("Profit over Time")
    plt.xlabel("Round")
    plt.ylabel("Profit")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# main function
def run_monopoly():
    agent = LLMPriceAgent(prompt_prefix=PROMPT_P0)
    prices, profits = [], []

    for t in range(T):
        price = agent.get_price()
        q = logit_demand(price)
        profit = (price - COST * ALPHA) * q

        agent.update_memory(price, q, profit)
        prices.append(price)
        profits.append(profit)

        print(f"Round {t+1}: price={price:.2f}, quantity={q:.2f}, profit={profit:.2f}")

    plot_price_profit(prices, profits)


if __name__ == "__main__":
    run_monopoly()
