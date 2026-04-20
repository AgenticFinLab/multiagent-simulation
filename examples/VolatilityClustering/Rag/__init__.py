"""VolatilityClusteringRag — RAG-augmented hybrid Rule+LLM VolatilityClustering simulation.

Three-way comparison:
    VolatilityClustering        — pure rule-based
    VolatilityClusteringRuleLLM — rule-embedded LLM (persona + quantitative rules in prompt)
    VolatilityClusteringRag     — rule-embedded LLM + personal RAG library (retrieved context per decision)
"""
