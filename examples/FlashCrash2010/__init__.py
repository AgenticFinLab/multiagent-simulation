"""FlashCrash2010 Simulation Package

2010 Flash Crash multi-agent simulation based on Kirilenko et al. (2017).

This package implements the May 6, 2010 flash crash event with:
- HFT market makers providing/withdrawing liquidity
- Momentum chasers creating feedback loops
- Fundamental traders providing stability
- Stop-loss traders with magnet effects
- Noise traders creating background activity

Variants:
    Rule:       Deterministic rule-based agents
    LLM:        LLM-driven agent decisions
    RuleLLM:    Hybrid rules + LLM judgment
    Rag:        RAG-augmented with historical flash crash knowledge
"""
