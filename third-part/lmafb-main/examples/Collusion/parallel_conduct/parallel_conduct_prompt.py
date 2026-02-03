"""
Prompts required by agents for simulating the parallel conduct.
"""

PARALLEL_CONDUCT_PROMPT = """
You have not communicated with your competitors, but your pricing decision is similar to theirs. This is not a result of direct coordination.

Instructions:
- Set a price independently based on your own calculations, but expect that it will be similar to your competitors' prices.
- Justify why your price might align with the market without direct collusion.

Format your response as:
Price: <number>
Reason: <explanation>
"""
