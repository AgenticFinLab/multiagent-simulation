"""VolatilityClusteringRag — RAG-augmented hybrid Rule+LLM VolatilityClustering simulation.

Three-way comparison:
    VolatilityClustering        — pure rule-based
    VolatilityClusteringRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    VolatilityClusteringRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""

from .players import (
    Market,
    RagLLMInvestor,
    RagLLMFundamentalist,
    RagLLMTrendFollower,
    RagLLMNoiseTrader,
    RagLLMSlowAdapter,
    RagLLMVolatilityTrader,
)

__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMFundamentalist",
    "RagLLMTrendFollower",
    "RagLLMNoiseTrader",
    "RagLLMSlowAdapter",
    "RagLLMVolatilityTrader",
]
