"""LiquidityDryupRag — RAG-augmented hybrid Rule+LLM LiquidityDryup simulation.

Three-way comparison:
    LiquidityDryup        — pure rule-based
    LiquidityDryupRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    LiquidityDryupRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""
