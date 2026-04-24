"""SunkCostFallacy LLM Variant"""

from .players import (
    Market,
    LLMInvestor,
    LLMSunkCostHolder,
    LLMCommitmentEscalator,
    LLMRationalCutter,
    LLMOpportunityCostTrader,
    LLMNoiseTrader,
)

__all__ = [
    "Market",
    "LLMInvestor",
    "LLMSunkCostHolder",
    "LLMCommitmentEscalator",
    "LLMRationalCutter",
    "LLMOpportunityCostTrader",
    "LLMNoiseTrader",
]
