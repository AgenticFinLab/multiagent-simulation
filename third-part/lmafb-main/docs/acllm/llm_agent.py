# llm_agent.py
from openai import OpenAI
import os

class LLMPriceAgent:
    def __init__(self, prompt_prefix, model="gpt-4", temperature=0.7):
        self.model = model
        self.prompt_prefix = prompt_prefix
        self.temperature = temperature
        self.memory = []

    def update_memory(self, price, quantity, profit, competitor_price):
        self.memory.append({
            "price": price,
            "quantity": quantity,
            "profit": profit,
            "competitor_price": competitor_price,
        })
        self.memory = self.memory[-100:]  # save at most 100 rounds

    def build_prompt(self):
        history_text = "\n".join([
            f"Round {i+1}: price={m['price']}, q={m['quantity']}, π={m['profit']}, comp_price={m['competitor_price']}"
            for i, m in enumerate(self.memory)
        ])
        return f"""{self.prompt_prefix}

Here is your pricing history:
{history_text}

Please write your plan and output your price for next round.
"""

    def get_price(self):
        prompt = self.build_prompt()
        response = OpenAI().chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}]
        )
        output = response.choices[0].message.content.strip()
        price = float("".join(filter(lambda x: x.isdigit() or x == '.', output)))
        return price
