"""ReversalEffectRag — RAG-augmented hybrid Rule+LLM ReversalEffect simulation.

Three-way comparison:
    ReversalEffect        — pure rule-based
    ReversalEffectRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    ReversalEffectRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""

from .players import (
    Market,
    RagLLMInvestor,
    RagLLMContrarianInvestor,
    RagLLMOverconfidentTrader,
    RagLLMValueInvestor,
    RagLLMMomentumChaser,
    RagLLMNoiseTrader,
)

__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMContrarianInvestor",
    "RagLLMOverconfidentTrader",
    "RagLLMValueInvestor",
    "RagLLMMomentumChaser",
    "RagLLMNoiseTrader",
]
