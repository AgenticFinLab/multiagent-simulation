"""
Prompts required by agents for simulating the Price Fixing scenario.
"""

PRICE_FIXING_PROMPT = """
You and your competitors have agreed to set the same price for a certain product to avoid price wars.

Instructions:
- Propose a price that matches the agreed-upon price between you and your competitors.
- Do not try to deviate from the fixed price, as it could break the agreement.
- Explain the reasons behind maintaining this price.

Format your response as:
Price: <number>
Reason: <justification>
"""
