"""EchoChamber Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.EchoChamber.RuleLLM.prompts import (  # noqa: F401
    RULELLM_IDEOLOGUE_SYS,
    RULELLM_CONFORMIST_SYS,
    RULELLM_CRITICAL_SYS,
    RULELLM_BRIDGE_SYS,
    RULELLM_PASSIVE_SYS,
)

RAG_IDEOLOGUE_SYS = RULELLM_IDEOLOGUE_SYS
RAG_CONFORMIST_SYS = RULELLM_CONFORMIST_SYS
RAG_CRITICAL_SYS = RULELLM_CRITICAL_SYS
RAG_BRIDGE_SYS = RULELLM_BRIDGE_SYS
RAG_PASSIVE_SYS = RULELLM_PASSIVE_SYS

RAG_USER_TEMPLATE = """== OPINION ENVIRONMENT (Round {round}) ==
- Polarization Index:          {polarization:.3f}  (0=united, 1=fully polarized)
- Previous Polarization:       {prev_polarization:.3f}
- Polarization Change:         {polarization_change:+.3f}
- Mean Opinion:                {mean_opinion:.3f}  (-1=far left, 0=center, +1=far right)
- Cluster Separation:          {cluster_separation:.3f}  (distance between left and right clusters)
- Cross-cutting Exposure:      {cross_cutting_exposure:.3f}  (0=silos, 1=diverse interaction)
- Active Polarizers:           {num_polarizers}
- Active Depolarizers:         {num_depolarizers}
- Net Polarization Intensity:  {net_polarization_intensity:+.3f}

== YOUR STATE ==
- Your Personal Opinion:       {my_opinion:.3f}

Relevant Domain Knowledge:
{rag_context}

Apply your DECISION RULES and the domain knowledge above to decide your action.
First output your reasoning inside <analysis>...</analysis> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {{"action_type": "polarize" | "neutral" | "depolarize", "intensity": <float 0-1>, "reasoning": "<brief>"}}
IMPORTANT: intensity MUST be a numeric value between 0 and 1, NOT an expression."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
