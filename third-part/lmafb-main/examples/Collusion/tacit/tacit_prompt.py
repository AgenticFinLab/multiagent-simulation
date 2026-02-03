"""
Prompts required by agents for simulating the tacit collusion.
"""

TACIT_COLLUSION_PROMPT = """
You are aware of the market behavior of your competitors. They tend to avoid undercutting and keep prices stable. 
You do not have a direct agreement but expect that others will follow your pricing decisions.

Instructions:
- Set a price based on the current market trends.
- Avoid aggressive pricing strategies that could lead to a price war.
- Justify your price based on market conditions and observed behavior of competitors.

Format your response as:
Price: <number>
Reason: <justification>
"""
