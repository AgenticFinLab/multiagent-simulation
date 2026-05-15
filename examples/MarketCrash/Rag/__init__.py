"""MarketCrashRag — RAG-augmented hybrid Rule+LLM MarketCrash simulation.

Three-way comparison:
    MarketCrash        — pure rule-based
    MarketCrashRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    MarketCrashRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""

from .players import (
    Market,
    RagLLMInvestor,
    RagLLMPanicSeller,
    RagLLMRiskParityFund,
    RagLLMLeveragedFund,
    RagLLMMarketMaker,
    RagLLMBottomFisher,
)

__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMPanicSeller",
    "RagLLMRiskParityFund",
    "RagLLMLeveragedFund",
    "RagLLMMarketMaker",
    "RagLLMBottomFisher",
]
