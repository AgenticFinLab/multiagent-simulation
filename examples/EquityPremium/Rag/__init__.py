"""EquityPremiumRag — RAG-augmented hybrid Rule+LLM EquityPremium simulation.

Three-way comparison:
    EquityPremium        — pure rule-based
    EquityPremiumRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    EquityPremiumRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""
