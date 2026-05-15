"""HindsightBias Rag Prompts

System prompts for RAG-augmented agents in the HindsightBias simulation.
Imports base prompts from RuleLLM and adds a RAG user template.
"""

from examples.HindsightBias.RuleLLM.prompts import (
    RULELLM_HINDSIGHTOVERCONFIDENT_PROMPT as RAG_HINDSIGHTOVERCONFIDENT_PROMPT,
    RULELLM_OUTCOMELEARNER_PROMPT as RAG_OUTCOMELEARNER_PROMPT,
    RULELLM_PROCESSEVALUATOR_PROMPT as RAG_PROCESSEVALUATOR_PROMPT,
    RULELLM_CONTRARIANSKEPTIC_PROMPT as RAG_CONTRARIANSKEPTIC_PROMPT,
    RULELLM_NOISETRADER_PROMPT as RAG_NOISETRADER_PROMPT,
)

RAG_USER_TEMPLATE = """Relevant background knowledge:
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2f}%
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Based on your trading strategy and the background knowledge above, what action do you take?
Provide your analysis and decision in the specified format.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

__all__ = [
    "RAG_HINDSIGHTOVERCONFIDENT_PROMPT",
    "RAG_OUTCOMELEARNER_PROMPT",
    "RAG_PROCESSEVALUATOR_PROMPT",
    "RAG_CONTRARIANSKEPTIC_PROMPT",
    "RAG_NOISETRADER_PROMPT",
    "RAG_USER_TEMPLATE",
]
